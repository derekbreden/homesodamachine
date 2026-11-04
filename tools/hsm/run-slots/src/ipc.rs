//! JSON lines with optional SCM_RIGHTS, using rustix's owned ancillary descriptors.
use anyhow::{Result, bail, ensure};
use rustix::{
    io::{FdFlags, fcntl_setfd},
    net::{
        RecvAncillaryBuffer, RecvAncillaryMessage, RecvFlags, ReturnFlags, SendAncillaryBuffer,
        SendAncillaryMessage, SendFlags, recvmsg, sendmsg,
    },
};
use serde_json::Value;
use std::{
    io::{IoSlice, IoSliceMut, Write},
    mem::MaybeUninit,
    os::fd::{BorrowedFd, OwnedFd},
    os::unix::net::UnixStream,
    process::{Child, Command, Output},
    sync::Mutex,
    thread,
    time::{Duration, Instant},
};

// macOS lacks atomic MSG_CMSG_CLOEXEC. Serialize the nonblocking receive + CLOEXEC step with
// child spawning so an unrelated request's newly received descriptor cannot leak into a child.
static DESCRIPTORS: Mutex<()> = Mutex::new(());

pub fn spawn(command: &mut Command) -> std::io::Result<Child> {
    let _guard = DESCRIPTORS.lock().unwrap();
    command.spawn()
}

pub fn output(command: &mut Command) -> std::io::Result<Output> {
    command.stdout(std::process::Stdio::piped()).stderr(std::process::Stdio::piped());
    spawn(command)?.wait_with_output()
}

pub fn send(mut stream: &UnixStream, value: &Value, fds: &[BorrowedFd<'_>]) -> Result<()> {
    let mut bytes = serde_json::to_vec(value)?;
    bytes.push(b'\n');
    if fds.is_empty() {
        stream.write_all(&bytes)?;
        return Ok(());
    }
    ensure!(fds.len() <= 6, "a run has at most four slots, one CAD and one compiler descriptor");
    let mut space = [MaybeUninit::uninit(); rustix::cmsg_space!(ScmRights(6))];
    let mut ancillary = SendAncillaryBuffer::new(&mut space);
    ensure!(ancillary.push(SendAncillaryMessage::ScmRights(fds)), "ancillary descriptor buffer");
    let sent = sendmsg(stream, &[IoSlice::new(&bytes)], &mut ancillary, SendFlags::empty())?;
    ensure!(sent > 0, "socket accepted no request bytes");
    stream.write_all(&bytes[sent..])?;
    Ok(())
}

pub fn receive(stream: &UnixStream, limit: usize, timeout: Duration) -> Result<(Value, Vec<OwnedFd>)> {
    let began = Instant::now();
    let mut bytes = Vec::new();
    let mut descriptors = Vec::new();
    loop {
        let mut buffer = [0u8; 8192];
        let mut space = [MaybeUninit::uninit(); rustix::cmsg_space!(ScmRights(512))];
        let mut ancillary = RecvAncillaryBuffer::new(&mut space);
        let received = {
            let _guard = DESCRIPTORS.lock().unwrap();
            let result =
                recvmsg(stream, &mut [IoSliceMut::new(&mut buffer)], &mut ancillary, RecvFlags::DONTWAIT);
            match result {
                Ok(message) => {
                    for message in ancillary.drain() {
                        if let RecvAncillaryMessage::ScmRights(fds) = message {
                            for fd in fds {
                                fcntl_setfd(&fd, FdFlags::CLOEXEC)?;
                                descriptors.push(fd);
                            }
                        }
                    }
                    ensure!(!message.flags.contains(ReturnFlags::CTRUNC), "truncated ancillary descriptors");
                    Some(message.bytes)
                }
                Err(rustix::io::Errno::AGAIN) | Err(rustix::io::Errno::INTR) => None,
                Err(error) => return Err(error.into()),
            }
        };
        match received {
            Some(0) => bail!("socket closed before a complete JSON line"),
            Some(count) => {
                bytes.extend_from_slice(&buffer[..count]);
                ensure!(bytes.len() <= limit && descriptors.len() <= 6, "oversized socket request");
                if bytes.ends_with(b"\n") {
                    return Ok((serde_json::from_slice(&bytes)?, descriptors));
                }
            }
            None => thread::sleep(Duration::from_millis(1)),
        }
        ensure!(began.elapsed() < timeout, "socket request timed out");
    }
}
