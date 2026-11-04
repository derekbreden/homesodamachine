#!/usr/bin/env python3
"""JSON frame writes to a peer that replies and closes immediately.

    tools/cad-venv/bin/python hardware/scripts/test_run_slots.py
"""
import array
import json
import os
import socket
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import _run_slots as slots
import _rust_part as part


class FastReply:
    """Close the real peer before a complete sendmsg returns to its caller."""
    def __init__(self, first_write=None):
        self.sender, self.peer = socket.socketpair()
        self.sender.settimeout(2)
        self.peer.settimeout(2)
        self.first_write = first_write
        self.request = None
        self.rights = []
        self.reply = {'ok': True, 'result': {'fixture': True}}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.sender.close()
        self.peer.close()

    def connect(self, _address):
        pass                                # the socketpair is already connected

    def sendmsg(self, buffers, ancillary):
        data = b''.join(buffers)
        sent = self.sender.sendmsg([data[:self.first_write]], ancillary)
        if sent == len(data):
            self._finish_request()
        return sent

    def sendall(self, data):
        self.sender.sendall(data)
        self._finish_request()

    def recv(self, size):
        return self.sender.recv(size)

    def _finish_request(self):
        data = bytearray()
        while not data.endswith(b'\n'):
            chunk, ancillary, _flags, _address = self.peer.recvmsg(
                4096, socket.CMSG_SPACE(6 * array.array('i').itemsize))
            data.extend(chunk)
            for level, kind, value in ancillary:
                if (level, kind) == (socket.SOL_SOCKET, socket.SCM_RIGHTS):
                    descriptors = array.array('i')
                    descriptors.frombytes(value[:len(value) - len(value) % descriptors.itemsize])
                    for fd in descriptors:
                        try:
                            held = os.fstat(fd)
                            self.rights.append((held.st_dev, held.st_ino))
                        finally:
                            os.close(fd)
            if not chunk:
                raise AssertionError('sender closed before its complete JSON frame')
        self.request = json.loads(data)
        self.peer.sendall(json.dumps(self.reply).encode() + b'\n')
        self.peer.close()


class FramedWrites(unittest.TestCase):
    def test_broker_request_to_a_fast_closing_peer(self):
        for first_write in (None, 7):
            with self.subTest(first_write=first_write), tempfile.TemporaryFile() as source:
                with FastReply(first_write) as peer:
                    request = {'v': 1, 'token': 'fixture'}
                    slots._send(peer, request, (source.fileno(),))
                    self.assertEqual(peer.request, request)
                    self.assertEqual(json.loads(peer.recv(4096)), peer.reply)
                    held = os.fstat(source.fileno())
                    self.assertEqual(peer.rights, [(held.st_dev, held.st_ino)])

    def test_engine_request_to_a_fast_closing_peer(self):
        for first_write in (None, 7):
            with self.subTest(first_write=first_write), tempfile.TemporaryFile() as source:
                with FastReply(first_write) as peer:
                    metadata = {'v': 1, 'slots': [{'slot': 0, 'token': 'fixture'}]}
                    lease = SimpleNamespace(wire=lambda: (metadata, (source.fileno(),)))
                    with (patch.object(socket, 'socket', return_value=peer),
                          patch.object(part, '_socket', return_value='/fixture'),
                          patch.object(part, '_has_lease_environment', return_value=True),
                          patch.object(part, '_slots', return_value=lease)):
                        reply = part._ask({'op': 'ping'})
                    self.assertEqual(reply, peer.reply)
                    self.assertEqual(peer.request, {'op': 'ping', '_lease': metadata})
                    held = os.fstat(source.fileno())
                    self.assertEqual(peer.rights, [(held.st_dev, held.st_ino)])


if __name__ == '__main__':
    unittest.main()
