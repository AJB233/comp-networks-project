import socket
import threading
import os
import json
import struct
from .utils import generate_file_hash

class FileTransfer:
    """Handles the reliable TCP socket connections for streaming large file chunks."""
    
    def __init__(self, tcp_port: int, save_directory: str, sender_name: str = ""):
        """
        Here we set up our port, the save directory and initially set the server to not be running, to show the server at default being turned off,
        we also do this to get the senders name, or check the socket to get the hosts name.
        """
        self.tcp_port = tcp_port
        self.save_directory = save_directory
        self._is_running = False
        self.sender_name = sender_name or socket.gethostname()

    def start_server(self) -> None:
        """
        Starts a background thread listening on `tcp_port` for incoming file handshakes.
        Once a handshake is accepted, loops to receive and write binary chunks to disk.
        """
        os.makedirs(self.save_directory, exist_ok=True)
        self._is_running = True

        server_thread = threading.Thread(target=self.listen_loop, daemon=True)
        server_thread.start()

    """Here we begin listening for a socket
        I wrote it down to first initiate the socket as server_sock, then binding it together, the queue is Length of 5
        , which is the number of peers that can wait in line and the timeout, we wrote so the server can check if the server will turn off
    """
    def listen_loop(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind(("0.0.0.0", self.tcp_port))
            server_sock.listen(5)
            server_sock.settimeout(1.0)
            """here I wrote, to have the code check while the server is running, it should be having the client socket accept the server incoming socket connection
            and to continuously be doing handle_client for that client socket, while the server is running, however if the socket times out, it can continue
            but if theres an error, it will outright break and stop.
            """
            while self._is_running:
                try:
                    client_sock, _addr = server_sock.accept()
                    self.handle_client(client_sock)
                except socket.timeout:
                    continue
                except OSError:
                    break
    
    def handle_client(self, client_sock: socket.socket) -> None:


        """ Code in This section written for the purpose of handling the client, first initializing the destination path before the try
        block, the client here receives the file, unpacks it in !I format, and reads the bytes and byte Length, then loads it in the JSON
        format. Then I wrote it going down the list of the Json, getting the files name, the size, and the expected checksum.
        Finally then setting down the path it goes into.
        """
        dest_path = None
        with client_sock:
            client_sock.settimeout(10.0)
            try:
                raw_header = self.recv_file(client_sock, 4)
                meta_length = struct.unpack("!I", raw_header)[0]
                meta_bytes = self.recv_file(client_sock, meta_length)
                metadata = json.loads(meta_bytes.decode("utf-8"))

                safe_name = os.path.basename(metadata["filename"])
                filesize_bytes = int (metadata["filesize_bytes"])
                expected_hash = metadata["checksum"]
                dest_path = os.path.join(self.save_directory, safe_name)
                """ Here we begin counting the actual bytes received, and loop through to make sure we received all the bytes
                we need to make sure that the file fully arrives, so thats why if, in chunk =, if its not received, then it raises a connection error
                if theres no connection error it then saves it by writing the file down, then we add the amount of bytes we received into bytes_received
                """
                bytes_received = 0
                with open(dest_path, "wb") as f:
                    while bytes_received < filesize_bytes:
                        to_read = min(4096, filesize_bytes - bytes_received)
                        chunk = client_sock.recv(to_read)
                        if not chunk:
                            raise ConnectionError("Peer disconnected mid-transfer")
                        f.write(chunk)
                        bytes_received += len(chunk)
                """
                Here when we write into the file, we check if the actual hash number is the same as what we expect,
                if it is and we're expecting to receive something, I wrote sendall "1" to indicate we received, otherwise if its incorrect
                , we remove that path, and sendall 0 to indicate not received when the error is brought up below, here we have it raise the
                value error
                """
                actual_hash = generate_file_hash(dest_path)
                if actual_hash == expected_hash:
                    client_sock.sendall(b"1")
                else:
                    raise ValueError("Error: SHA-256 checksum mismatch")
                """
                Here we wrote this part, for the purpose of checking if there is an issue, crashing or disconnection.Basically if the file is half written or bugged, it raises the exception so that way we dont leave broken files when downloading.
                to then remove it from the path. in the try block we sendall "0" indicating we're not receiving anymore to then show its finished or that theres an error and wont send anymore.
                here if the error comes up, like how it was raised earlier, we send "0".
                """
            except Exception as e:
                print(f"[Transfer Error] {e}")
                if dest_path and os.path.exists(dest_path):
                    os.remove(dest_path)
                try:
                    client_sock.sendall(b"0")
                except OSError:
                    pass


    
    
    # Here the definition for receiving the file, we built it like this.
    # I decided to first set up the buffer array, and so long as the buffer was less than the incoming bytes, then the chunk,
    # would read through and receive the bytes until all expected bytes are received, if there's nothing in the chunk, we raised the error
    # of the connection closing before being fulfilled, the buffer.extend then adds the chunks onto the list of the buffer array, then
    # we return the bytes from buffer, which is how we receive the file.

    def recv_file(self, sock: socket.socket, num_bytes: int) -> bytes:
        buffer = bytearray()
        while len(buffer) < num_bytes:
            chunk = sock.recv(num_bytes - len(buffer))
            if not chunk:
                raise ConnectionError("Connection closed before expected bytes arrived")
            buffer.extend(chunk)
        return bytes(buffer)

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
        #First we check if there is a filepath, I wrote this down in case there wasnt, and if there isnt is returns false.
        if not os.path.isfile(filepath):
            return False

        """
        Here we wrote a try block, choosing to manually hard code in the JSON for now in the try block with metadata.
        matching it to how the client is handled.
        Then we begin constructing how the file will be sent, the data first encodes it in the proper format.
        The Header also does the same with the bytes packing it.
        Then it creates the socket connection using the targeted ip and the tcp port, I also added a timeout of 5 seconds just in case no connection is created
        """
        try:
            metadata =  {
                        "sender": self.sender_name,
                        "filename": os.path.basename(filepath),
                        "filesize_bytes": os.path.getsize(filepath),
                        "checksum": generate_file_hash(filepath)
                        }
            
            data= json.dumps(metadata).encode("utf-8")
            HEADER = struct.pack("!I", len(data))
            with socket.create_connection((target_ip, self.tcp_port), timeout = 5.0) as sock:
                sock.settimeout(30.0)
                """Here we send the file we just constructed and its data,
                using sendall for the header and the metadata, with opening the file path and while it is reading the file we're meant to send
                it is actively using sendall on chunk to send that file over until the end.
                """
                sock.sendall(HEADER + data)
                with open(filepath, "rb") as f:
                    while chunk := f.read(4096):
                        sock.sendall(chunk)
                """here we are waiting for the receivers reply, if they mark 1, then that means
                that the file was sent successfully.
                """
                return self.recv_file(sock, 1) == b"1"
        except Exception as e:
            print(f"[Transfer Error] {e}")
            return False

    def stop(self) -> None:
        """Safely shuts down the TCP listening server."""
        self._is_running = False