import socket
import threading
import json

class PeerDiscovery:
    """Handles UDP broadcasting and listening to discover classmates on the local network."""
    
    def __init__(self, broadcast_port: int, user_handle: str):
        self.broadcast_port = broadcast_port
        self.user_handle = user_handle
        self.active_peers = {}  # Dictionary mapping IP addresses to user handles
        self._is_running = False

    def start_listening(self) -> None:
        """
        Starts a background thread to listen for incoming UDP broadcast packets 
        from other students opening the app.
        """
        raise NotImplementedError("UDP listening thread logic not yet implemented")

    def broadcast_presence(self) -> None:
        """
        Sends a UDP packet to the local subnet announcing this user's IP and handle.
        Typically called in a loop every few seconds while the app is open.
        """
        raise NotImplementedError("UDP broadcast logic not yet implemented")

    def get_active_peers(self) -> dict:
        """
        Returns the current list of discovered peers.
        
        Returns:
            dict: Format {'192.168.4.10': 'Alice', '192.168.4.11': 'Bob'}
        """
        return self.active_peers
    
    def stop(self) -> None:
        """Safely shuts down the UDP sockets and background threads."""
        self._is_running = False