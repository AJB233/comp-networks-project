import socket
import threading
import os

class FileTransfer:
    """Handles the reliable TCP socket connections for streaming large file chunks."""
    
    def __init__(self, tcp_port: int, save_directory: str):
        self.tcp_port = tcp_port
        self.save_directory = save_directory
        self._is_running = False

    def start_server(self) -> None:
        """
        Starts a background thread listening on `tcp_port` for incoming file handshakes.
        Once a handshake is accepted, loops to receive and write binary chunks to disk.
        """
        raise NotImplementedError("TCP receiver logic not yet implemented")

    def send_file(self, target_ip: str, filepath: str) -> bool:
        """
        Initiates a connection to a peer, sends the metadata handshake, and streams 
        the file in chunks to prevent memory overflow.
        
        Args:
            target_ip (str): The IP address of the receiving peer.
            filepath (str): The local file to send.
            
        Returns:
            bool: True if transfer was successful, False if failed or rejected.
        """
        raise NotImplementedError("TCP sender logic not yet implemented")

    def stop(self) -> None:
        """Safely shuts down the TCP listening server."""
        self._is_running = False