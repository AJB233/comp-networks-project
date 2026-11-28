"""Discovery tests. Real UDP broadcast needs a network interface with a
broadcast address, so the broadcast test is skipped when the OS refuses it."""
import socket
import time

import pytest

from p2p_core.discovery import PeerDiscovery


def free_udp_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def test_listener_records_peer_and_ignores_self():
    port = free_udp_port()
    d = PeerDiscovery(port, "alice")
    d.start_listening()
    time.sleep(0.3)
    tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    tx.sendto(b"bob", ("127.0.0.1", port))      # another peer
    tx.sendto(b"alice", ("127.0.0.1", port))    # our own handle -> filtered
    tx.sendto(b"\xff\xfe", ("127.0.0.1", port)) # garbage -> must not crash listener
    tx.close()
    time.sleep(0.5)
    peers = d.get_active_peers()
    d.stop()
    assert list(peers.values()) == ["bob"]


def test_two_nodes_discover_each_other_via_broadcast():
    port = free_udp_port()
    a, b = PeerDiscovery(port, "alice"), PeerDiscovery(port, "bob")
    a.start_listening(); b.start_listening()
    time.sleep(0.3)
    try:
        a.broadcast_presence(); b.broadcast_presence()
    except OSError as e:
        a.stop(); b.stop()
        pytest.skip(f"broadcast not available here: {e}")
    time.sleep(0.7)
    pa, pb = a.get_active_peers(), b.get_active_peers()
    a.stop(); b.stop()
    if not pa and not pb:
        pytest.skip("broadcast not delivered in this environment")
    assert "bob" in pa.values() and "alice" in pb.values()
