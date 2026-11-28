"""Functionality and robustness tests for the TCP file-transfer module.

Run from the repository root:  PYTHONPATH=src python3 -m pytest tests -v
"""
import json
import os
import socket
import struct
import time

import pytest

from p2p_core.transfer import FileTransfer
from p2p_core.utils import generate_file_hash


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def node(tmp_path):
    """A running receiver on localhost saving into tmp_path/received."""
    port = free_port()
    ft = FileTransfer(port, str(tmp_path / "received"), sender_name="tester")
    ft.start_server()
    time.sleep(0.3)
    yield ft
    ft.stop()
    time.sleep(1.2)  # listen loop wakes every 1 s


def make_file(path, size):
    with open(path, "wb") as f:
        f.write(os.urandom(size))
    return str(path)


def raw_send(port, metadata, body, close_early=False):
    """Hand-built sender so we can inject bad metadata or cut the stream."""
    data = json.dumps(metadata).encode()
    s = socket.create_connection(("127.0.0.1", port), timeout=5)
    s.sendall(struct.pack("!I", len(data)) + data + body)
    if close_early:
        s.close()
        return None
    reply = s.recv(1)
    s.close()
    return reply


@pytest.mark.parametrize("size", [0, 1, 4095, 4096, 4097, 1_000_000])
def test_roundtrip_integrity(node, tmp_path, size):
    src = make_file(tmp_path / f"src_{size}.bin", size)
    assert node.send_file("127.0.0.1", src) is True
    dst = tmp_path / "received" / f"src_{size}.bin"
    assert dst.exists()
    assert generate_file_hash(str(dst)) == generate_file_hash(src)


def test_send_missing_file_returns_false(node, tmp_path):
    assert node.send_file("127.0.0.1", str(tmp_path / "nope.bin")) is False


def test_send_to_unreachable_peer_returns_false(tmp_path):
    ft = FileTransfer(free_port(), str(tmp_path / "r"))
    src = make_file(tmp_path / "a.bin", 100)
    assert ft.send_file("127.0.0.1", src) is False  # nothing listening


def test_checksum_mismatch_rejected_and_file_removed(node, tmp_path):
    body = b"hello world"
    meta = {"sender": "x", "filename": "bad.txt", "filesize_bytes": len(body), "checksum": "0" * 64}
    assert raw_send(node.tcp_port, meta, body) == b"0"
    assert not (tmp_path / "received" / "bad.txt").exists()


def test_disconnect_mid_transfer_removes_partial_and_server_survives(node, tmp_path):
    meta = {"sender": "x", "filename": "half.bin", "filesize_bytes": 100_000, "checksum": "0" * 64}
    raw_send(node.tcp_port, meta, b"A" * 1000, close_early=True)
    time.sleep(0.5)
    assert not (tmp_path / "received" / "half.bin").exists()
    # server must still accept a normal transfer afterwards
    src = make_file(tmp_path / "ok.bin", 5000)
    assert node.send_file("127.0.0.1", src) is True


def test_path_traversal_filename_is_sanitised(node, tmp_path):
    body = b"data"
    meta = {"sender": "x", "filename": "../../evil.txt", "filesize_bytes": 4,
            "checksum": __import__("hashlib").sha256(body).hexdigest()}
    assert raw_send(node.tcp_port, meta, body) == b"1"
    assert (tmp_path / "received" / "evil.txt").exists()
    assert not (tmp_path / "evil.txt").exists()


def test_malformed_metadata_does_not_crash_server(node, tmp_path):
    s = socket.create_connection(("127.0.0.1", node.tcp_port), timeout=5)
    junk = b"not json"
    s.sendall(struct.pack("!I", len(junk)) + junk)
    assert s.recv(1) == b"0"
    s.close()
    src = make_file(tmp_path / "ok.bin", 100)
    assert node.send_file("127.0.0.1", src) is True


def test_throughput_10mb(node, tmp_path, capsys):
    src = make_file(tmp_path / "big.bin", 10 * 1024 * 1024)
    t0 = time.perf_counter()
    assert node.send_file("127.0.0.1", src) is True
    dt = time.perf_counter() - t0
    with capsys.disabled():
        print(f"\n[perf] 10 MiB loopback transfer: {dt:.2f}s, {10/dt:.1f} MiB/s")
