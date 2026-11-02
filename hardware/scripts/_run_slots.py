"""Host-wide heavy-run leases, shared by Python, Rust and command wrappers.

The live one-line count is /tmp/hsm-<uid>/heavy/count. The repository defaults
name physical capacity, concurrent-start spacing and host-pressure limits.
Timing reserves every slot. Descriptors carry flock ownership into children;
environment text alone grants nothing.
"""
from __future__ import annotations

import array
import atexit
import errno
import fcntl
import functools
import hashlib
import json
import os
from pathlib import Path
import secrets
import socket
import stat
import sys
import threading
import time

RUN_ENV, CAD_ENV, COMPILER_ENV, BROKER_ENV = 'HSM_RUN_LEASE', 'HSM_CAD_LEASE', 'HSM_COMPILER_LEASE', 'HSM_RUN_BROKER'
_directory = None                         # private process fixtures may set this to a temporary directory
_run = _cad = _compiler = _broker = None
_broker_checked = False
_WIRE_LIMIT = 16384                       # shared with the Rust broker receiver
# Darwin can install all 512 rights in an mbuf even when the returned control data
# is truncated. Receive the full set so every rejected excess descriptor is owned.
# https://github.com/apple-oss-distributions/xnu/blob/main/bsd/kern/uipc_usrreq.c
_ANCILLARY_SPACE = socket.CMSG_SPACE(512 * array.array('i').itemsize)


def directory():
    path = Path(_directory) if _directory is not None else Path(f'/tmp/hsm-{os.getuid()}/heavy')
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    return path


@functools.cache
def _defaults():
    root = Path(__file__).resolve().parents[2]
    git = root / '.git'
    if git.is_file():
        gd = Path(git.read_text().strip().removeprefix('gitdir: '))
        if not gd.is_absolute():
            gd = root / gd
        common = gd / 'commondir'
        if common.is_file():
            candidate = (gd / common.read_text().strip()).resolve().parent
            if (candidate / 'tools/hsm/run-slots.defaults.json').is_file():
                root = candidate
    return json.loads((root / 'tools/hsm/run-slots.defaults.json').read_text())


def capacity():
    return int(_defaults()['slots'])


def count():
    path = directory() / 'count'
    try:
        value = int(path.read_text().strip())
    except FileNotFoundError:
        value = capacity()
    if value not in range(1, capacity() + 1):
        raise ValueError(f'{path} must hold an integer from 1 to {capacity()}')
    return value


def set_count(value):
    if value not in range(1, capacity() + 1):
        raise ValueError(f'count must be an integer from 1 to {capacity()}')
    guard = _open(directory() / 'admission.lock')
    try:
        fcntl.flock(guard, fcntl.LOCK_EX)
        path = directory() / 'count'
        temp = path.with_name(f'.count.{os.getpid()}')
        temp.write_text(f'{value}\n')
        os.replace(temp, path)
    finally:
        os.close(guard)


def _path(kind, slot=None):
    return directory() / (f'{kind}.lock' if kind in ('cad', 'compiler') else f'slot.{slot}.lock')


def _read_fd(fd):
    try:
        return json.loads(os.pread(fd, 16384, 0))
    except (OSError, ValueError):
        return {}


def _write_fd(fd, value):
    text = (json.dumps(value, separators=(',', ':')) + '\n').encode()
    os.ftruncate(fd, 0)
    os.pwrite(fd, text, 0)


def _open(path):
    return os.open(path, os.O_RDWR | os.O_CREAT, 0o600)


def _valid(entry, kind):
    """Prove an inherited descriptor shares the *held* open-file-description."""
    try:
        fd = entry['fd']
        if not isinstance(fd, int) or fd < 3 or not isinstance(entry['token'], str):
            return False
        if kind == 'run' and entry['slot'] not in range(capacity()):
            return False
        path = _path(kind, entry.get('slot'))
        held, named = os.fstat(fd), path.stat()
        if not stat.S_ISREG(held.st_mode) or (held.st_dev, held.st_ino) != (named.st_dev, named.st_ino):
            return False
        probe = os.open(path, os.O_RDWR)
        try:
            try:
                fcntl.flock(probe, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as error:
                if error.errno not in (errno.EACCES, errno.EAGAIN):
                    return False
            else:
                return False                # an unlocked descriptor is not a lease
        finally:
            os.close(probe)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        record = _read_fd(fd)
        return record.get('token') == entry['token'] and record.get('kind') == kind
    except (OSError, KeyError, TypeError, ValueError):
        return False


class Lease:
    def __init__(self, entries, kind, inherited=False):
        self.entries, self.kind, self.inherited = entries, kind, inherited

    def close(self):
        # LOCK_UN would release a child's lock too. Last close releases the OFD.
        for entry in self.entries:
            try:
                os.close(entry['fd'])
            except OSError:
                pass
        self.entries = []


def _export(lease):
    if lease.kind == 'run':
        os.environ[RUN_ENV] = json.dumps({'v': 1, 'fds': lease.entries}, separators=(',', ':'))
    else:
        os.environ[CAD_ENV if lease.kind == 'cad' else COMPILER_ENV] = json.dumps({'v': 1, **lease.entries[0]}, separators=(',', ':'))


def _env_lease(kind):
    try:
        record = json.loads(os.environ.get({'run': RUN_ENV, 'cad': CAD_ENV, 'compiler': COMPILER_ENV}[kind], 'null'))
        if not isinstance(record, dict) or record.get('v') != 1:
            return None
        entries = record['fds'] if kind == 'run' else [{k: record[k] for k in ('fd', 'token')}]
        if not entries or (kind == 'run' and len({e['slot'] for e in entries}) != len(entries)):
            return None
        if all(_valid(e, kind) for e in entries):
            return Lease(entries, kind, inherited=True)
    except (KeyError, TypeError, ValueError):
        pass
    return None


def wire():
    """Ancillary order is slots, CAD, compiler. Acquires no new capacity."""
    if not _broker_checked:
        _from_broker()
    run, cad, compiler = current(), current_cad(), current_compiler()
    slots = run.entries if run else []
    c = cad.entries[0] if cad else None
    build = compiler.entries[0] if compiler else None
    if not slots and c is None and build is None:
        return None, ()
    return ({'v': 1, 'slots': [{k: e[k] for k in ('slot', 'token')} for e in slots],
             'cad': {'token': c['token']} if c else None,
             'compiler': {'token': build['token']} if build else None,
             'profile': os.environ.get('HSM_RUN_PROFILE')},
            tuple(e['fd'] for e in slots) + ((c['fd'],) if c else ()) + ((build['fd'],) if build else ()))


def adopt(metadata, fds):
    global _run, _cad, _compiler, _broker_checked
    try:
        slots, cad, compiler = metadata['slots'], metadata.get('cad'), metadata.get('compiler')
        if metadata.get('v') != 1 or len(fds) != len(slots) + bool(cad) + bool(compiler):
            raise ValueError('lease descriptor count does not match')
        runs = [{**e, 'fd': fd} for e, fd in zip(slots, fds)]
        offset = len(slots)
        ce = {'fd': fds[offset], 'token': cad['token']} if cad else None
        offset += bool(cad)
        build = {'fd': fds[offset], 'token': compiler['token']} if compiler else None
        if (not all(_valid(e, 'run') for e in runs) or (ce and not _valid(ce, 'cad'))
                or (build and not _valid(build, 'compiler'))):
            raise ValueError('received descriptors are not held leases')
        for old, entries, kind in ((_run, runs, 'run'), (_cad, [ce] if ce else [], 'cad'),
                                   (_compiler, [build] if build else [], 'compiler')):
            if entries and old:
                old.close()
            if entries:
                lease = Lease(entries, kind, inherited=True)
                globals()[{'run':'_run','cad':'_cad','compiler':'_compiler'}[kind]] = lease
                _export(lease)
        if metadata.get('profile'):
            os.environ['HSM_RUN_PROFILE'] = metadata['profile']
        _broker_checked = True
        return True
    except (KeyError, TypeError, ValueError):
        for fd in fds:
            os.close(fd)
        return False


def _receive(peer, limit=_WIRE_LIMIT):
    """One JSON line and its rights; close all received rights on a failed frame."""
    data, fds = bytearray(), []
    timeout = peer.gettimeout()
    deadline = time.monotonic() + (timeout if timeout is not None else 1)
    try:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('lease frame timed out')
            peer.settimeout(remaining)
            chunk, ancillary, flags, _addr = peer.recvmsg(4096, _ANCILLARY_SPACE)
            for level, typ, value in ancillary:
                if (level, typ) == (socket.SOL_SOCKET, socket.SCM_RIGHTS):
                    numbers = array.array('i')
                    numbers.frombytes(value[:len(value) - len(value) % numbers.itemsize])
                    fds.extend(numbers)
                    for fd in numbers:
                        os.set_inheritable(fd, False)
            if flags & socket.MSG_CTRUNC or len(fds) > capacity() + 2:
                raise ValueError('truncated or excess lease descriptors')
            data.extend(chunk)
            if len(data) > limit:
                raise ValueError('oversized lease frame')
            if b'\n' in data:
                value = json.loads(data)
                if not isinstance(value, dict):
                    raise ValueError('a lease frame must be an object')
                return value, fds
            if not chunk:
                raise ValueError('socket closed before a complete lease frame')
    except BaseException:
        for fd in fds:
            os.close(fd)
        raise
    finally:
        peer.settimeout(timeout)


def _send(peer, value, fds=()):
    data = (json.dumps(value) + '\n').encode()
    if len(data) > _WIRE_LIMIT or len(fds) > capacity() + 2:
        raise ValueError('oversized lease frame')
    ancillary = [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array('i', fds))] if fds else []
    sent = peer.sendmsg([data], ancillary)
    if sent <= 0:
        raise OSError('socket accepted no lease bytes')
    peer.sendall(data[sent:])                 # rights belong only to the first write


def _from_broker():
    global _broker_checked
    fds = []
    try:
        record = json.loads(os.environ.get(BROKER_ENV, 'null'))
        path = Path(record['path'])
        if _broker is not None and path == _broker.path:
            _broker_checked = True
            return False
        if path.parent.resolve() != directory().resolve():
            return False
        owner = json.loads(path.with_suffix('.json').read_text())
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as peer:
            peer.settimeout(1)
            peer.connect(str(path))
            _send(peer, {'v': 1, 'token': owner['token']})
            reply, fds = _receive(peer)
        if not reply.get('ok'):
            for fd in fds:
                os.close(fd)
            return False
        return adopt(reply['_lease'], fds)
    except (OSError, ValueError, KeyError, TypeError):
        for fd in fds:
            os.close(fd)
        return False


def current():
    global _run
    if _run and _run.entries:
        return _run
    _run = _env_lease('run')
    if _run is None and not _broker_checked:
        _from_broker()
    return _run


def current_cad():
    global _cad
    if _cad and _cad.entries:
        return _cad
    _cad = _env_lease('cad')
    if _cad is None and not _broker_checked:
        _from_broker()
    return _cad


def current_compiler():
    global _compiler
    if _compiler and _compiler.entries:
        return _compiler
    _compiler = _env_lease('compiler')
    if _compiler is None and not _broker_checked:
        _from_broker()
    return _compiler


class TimingLeaseError(RuntimeError):
    """A nested timing run cannot reserve more than its already-admitted parent."""


class InheritanceError(RuntimeError):
    """An advertised parent lease must validate before a child can run."""


def _expects_parent():
    if any(os.environ.get(name) for name in (RUN_ENV, CAD_ENV, COMPILER_ENV)):
        return True
    if config := os.environ.get(BROKER_ENV):
        try:
            return _broker is None or Path(json.loads(config)['path']) != _broker.path
        except (KeyError, TypeError, ValueError):
            return True
    return False


@functools.cache
def _sysctl():
    import ctypes
    libc = ctypes.CDLL(None, use_errno=True)
    libc.sysctlbyname.argtypes = [ctypes.c_char_p, ctypes.c_void_p,
                                  ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p, ctypes.c_size_t]
    return ctypes, libc


def host_pressure():
    """macOS pressure level and used swap bytes; unavailable measurements are None."""
    if sys.platform != 'darwin':
        return None, None
    ctypes, libc = _sysctl()
    def read(name, value):
        size = ctypes.c_size_t(ctypes.sizeof(value))
        return value if libc.sysctlbyname(name.encode(), ctypes.byref(value), ctypes.byref(size), None, 0) == 0 else None
    class Swap(ctypes.Structure):
        _fields_ = [('total', ctypes.c_uint64), ('available', ctypes.c_uint64),
                    ('used', ctypes.c_uint64), ('page_size', ctypes.c_uint32), ('encrypted', ctypes.c_int)]
    pressure = read('kern.memorystatus_vm_pressure_level', ctypes.c_int())
    swap = read('vm.swapusage', Swap())
    return pressure.value if pressure is not None else None, swap.used if swap is not None else None


def acquire(key=None, timing=False):
    """Admit a new logical root; descendants reuse their valid existing lease."""
    global _run
    inherited = current()
    if inherited:
        if timing and len(inherited.entries) < capacity():
            raise TimingLeaseError('request timing at the logical root so it can reserve all slots')
        return inherited
    if _expects_parent():
        raise InheritanceError('the advertised parent lease or broker could not be validated; refusing a second logical run')
    waiting = None
    token = secrets.token_hex(16)
    while True:
        gate = _open(directory() / 'admission.lock')
        free = []
        try:
            fcntl.flock(gate, fcntl.LOCK_EX)
            busy = set()
            newest_busy_start = 0
            for slot in range(capacity()):
                fd = _open(_path('run', slot))
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    record = _read_fd(fd)
                    busy.add(record.get('token', f'unknown:{slot}'))
                    started = record.get('started_unix_ms')
                    if isinstance(started, int):
                        newest_busy_start = max(newest_busy_start, started)
                    os.close(fd)
                else:
                    free.append({'fd': fd, 'slot': slot, 'token': token})
            limit = count()                    # live count applies to already-queued roots too
            level, swap = host_pressure()
            policy = _defaults()
            reason = None
            if level == policy['critical_pressure_level'] or (swap is not None and swap > policy['max_swap_bytes']):
                reason = f'host pressure level={level}, swap={swap} bytes'
            elif timing and busy:
                reason = 'all heavy-run slots for timing'
            elif len(busy) >= limit:
                reason = f'capacity {limit} ({len(busy)} active logical runs)'
            else:
                state_path = directory() / 'admission.json'
                now = int(time.time() * 1000)
                remaining = policy['stagger_seconds'] - (now - newest_busy_start) / 1000
                if busy and remaining > 0:
                    reason = 'staggering concurrent logical starts'
                elif free:
                    held, free = (free, []) if timing else (free[:1], free[1:])
                    for entry in held:
                        _write_fd(entry['fd'], {'v': 1, 'kind': 'run', 'token': token,
                                                'pid': os.getpid(), 'key': key, 'slot': entry['slot'],
                                                'started_unix_ms': now})
                    state_path.write_text(json.dumps({'v': 1, 'last_start_unix_ms': now}) + '\n')
                    _run = Lease(held, 'run')
                    _export(_run)
                    if key:
                        os.environ['HSM_RUN_PROFILE'] = key
                    return _run
                else:
                    reason = 'available heavy-run descriptor'
        finally:
            for entry in free:
                os.close(entry['fd'])
            os.close(gate)
        if reason != waiting:
            print(f'[run] waiting: {reason}', file=sys.stderr, flush=True)
            waiting = reason
        time.sleep(0.1)


def acquire_cad():
    global _cad
    if inherited := current_cad():
        return inherited
    if current_compiler() is not None:
        raise RuntimeError('native CAD must be reserved before compiler; use --cad at the logical root')
    fd = _open(_path('cad'))
    fcntl.flock(fd, fcntl.LOCK_EX)
    entry = {'fd': fd, 'token': secrets.token_hex(16)}
    _write_fd(fd, {'v': 1, 'kind': 'cad', 'token': entry['token'], 'pid': os.getpid()})
    _cad = Lease([entry], 'cad')
    _export(_cad)
    return _cad


def acquire_compiler():
    global _compiler
    if inherited := current_compiler():
        return inherited
    fd = _open(_path('compiler'))
    fcntl.flock(fd, fcntl.LOCK_EX)
    entry = {'fd': fd, 'token': secrets.token_hex(16)}
    _write_fd(fd, {'v': 1, 'kind': 'compiler', 'token': entry['token'], 'pid': os.getpid()})
    _compiler = Lease([entry], 'compiler')
    _export(_compiler)
    return _compiler


def release():
    global _run, _cad, _compiler, _broker_checked
    if _compiler:
        _compiler.close()
    if _cad:
        _cad.close()
    if _run:
        _run.close()
    _run = _cad = _compiler = None
    _broker_checked = False
    os.environ.pop(COMPILER_ENV, None)
    os.environ.pop(RUN_ENV, None)
    os.environ.pop(CAD_ENV, None)


def release_cad():
    global _cad, _broker_checked
    if _cad:
        _cad.close()
    _cad = None
    _broker_checked = False
    os.environ.pop(CAD_ENV, None)


def pass_fds():
    return wire()[1]


def broker_config(workspace):
    name = hashlib.sha256(str(Path(workspace).resolve()).encode()).hexdigest()[:16]
    return json.dumps({'path': str(directory() / f'w.{name}.sock')}, separators=(',', ':'))


class Broker:
    def __init__(self, config=None):
        self.path = Path(json.loads(config)['path']) if config else directory() / f'b.{os.getpid()}.sock'
        self.token = secrets.token_hex(16)
        self.peer = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.path.unlink(missing_ok=True)
        self.peer.bind(str(self.path))
        self.peer.listen(8)
        self.peer.settimeout(0.2)
        self.closed = False
        self.path.with_suffix('.json').write_text(json.dumps({'v': 1, 'token': self.token, 'pid': os.getpid()}))
        threading.Thread(target=self._serve, daemon=True).start()

    def _serve(self):
        while not self.closed:
            try:
                peer, _addr = self.peer.accept()
            except (socket.timeout, OSError):
                continue
            with peer:
                try:
                    peer.settimeout(1)
                    asked, incoming = _receive(peer, 4096)
                    try:
                        if incoming:
                            raise ValueError('a broker request carries no lease descriptors')
                        metadata, descriptors = wire()
                        ok = asked.get('v') == 1 and secrets.compare_digest(asked.get('token', ''), self.token)
                        reply = {'ok': bool(ok and metadata), '_lease': metadata if ok else None}
                        _send(peer, reply, descriptors if ok and metadata else ())
                    finally:
                        for fd in incoming:
                            os.close(fd)
                except (OSError, ValueError, TypeError):
                    pass

    def close(self):
        self.closed = True
        self.peer.close()
        self.path.unlink(missing_ok=True)
        self.path.with_suffix('.json').unlink(missing_ok=True)


def child_env(env=None, broker=True):
    global _broker
    if broker and pass_fds():
        if _broker is None:
            _broker = Broker()
        os.environ[BROKER_ENV] = json.dumps({'path': str(_broker.path)}, separators=(',', ':'))
    answer = dict(os.environ if env is None else env,
                  **{k: os.environ[k] for k in (RUN_ENV, CAD_ENV, COMPILER_ENV, BROKER_ENV, 'HSM_RUN_PROFILE') if k in os.environ})
    if current_cad():
        answer['HSM_NO_BUILD_LOCK'] = '1'      # compatibility for a child in an older worktree
    else:
        answer.pop('HSM_NO_BUILD_LOCK', None)
    return answer


def subprocess_kwargs(env=None):
    return {'env': child_env(env), 'pass_fds': pass_fds()}


def command(argv, key=None):
    """A raw native child, measured by wait4 in the shared command wrapper."""
    runner = Path(__file__).resolve().parents[2] / 'tools/run.py'
    return [sys.executable, str(runner), *(['--key', key] if key else []), '--', *map(str, argv)]


def ensure_cli(key):
    """Put a directly invoked Python entrypoint under a waiting, lease-holding parent."""
    if current():
        return acquire(key)
    argv = command([sys.executable, *sys.argv], key=key)
    os.execv(sys.executable, argv)


def _finish():
    if _broker:
        _broker.close()
    release()


atexit.register(_finish)
