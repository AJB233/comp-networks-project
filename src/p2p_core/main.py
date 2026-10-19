import time
from .discovery import PeerDiscovery
from .transfer import FileTransfer
from .utils import get_local_ip

# Configuration constants
BROADCAST_PORT = 50000
TCP_PORT = 50001
SAVE_DIR = "./received_files"
USER_HANDLE = "Student_A" # This could be dynamically requested on launch

def main():
    print(f"Starting P2P Node as {USER_HANDLE}...")
    
    # 1. Initialize modules
    discovery = PeerDiscovery(broadcast_port=BROADCAST_PORT, user_handle=USER_HANDLE)
    transfer = FileTransfer(tcp_port=TCP_PORT, save_directory=SAVE_DIR)
    
    try:
        # 2. Start background services
        discovery.start_listening()
        transfer.start_server()
        
        # 3. Main application loop (CLI or UI event loop goes here)
        while True:
            discovery.broadcast_presence()
            time.sleep(3) # Broadcast every 3 seconds
            
            # Example UI logic stub:
            # peers = discovery.get_active_peers()
            # print(peers)
            
    except KeyboardInterrupt:
        print("\nShutting down application...")
    finally:
        # 4. Graceful cleanup
        discovery.stop()
        transfer.stop()

if __name__ == "__main__":
    main()