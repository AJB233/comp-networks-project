import time
import threading
import os
from .utils import get_local_ip
from .transfer import FileTransfer
from .discovery import PeerDiscovery

def print_menu():
    print("\n--- P2P AirDrop ---")
    print("1. View available peers")
    print("2. Send a file")
    print("3. Exit")

def main():
    my_ip = get_local_ip()
    my_handle = input("Enter your display name: ").strip()
    print(f"Starting node on {my_ip} as {my_handle}...")

    # Initialize Modules
    BROADCAST_PORT = 50000

    discovery = PeerDiscovery(broadcast_port=BROADCAST_PORT, user_handle=my_handle)
    discovery.start_listening()

    stop_broadcast = threading.Event()

    def periodic_broadcast():
        while not stop_broadcast.is_set():
            discovery.broadcast_presence()
            stop_broadcast.wait(3.0)

    threading.Thread(target=periodic_broadcast, daemon=True).start()

    TCP_PORT = 50001

    transfer = FileTransfer(
        tcp_port=TCP_PORT,
        save_directory="./received_files",
        sender_name=my_handle,
    )
    transfer.start_server()

    try:
        while True:
            print_menu()
            choice = input("Select an option: ")

            if choice == '1':
                print("\n[Scanning local network...]")
                peers = discovery.get_active_peers()
                if not peers:
                    print("No active peers found...")
                else:
                    for ip, name in peers.items():
                        print(f"- {name} ({ip})")

            elif choice == '2':
                target_ip = input("Enter target IP address: ")
                filepath = input("Enter full path to file: ")
                
                if os.path.exists(filepath):
                    print(f"Initiating transfer to {target_ip}...")
                    success = transfer.send_file(target_ip, filepath)
                    print("Transfer Complete!" if success else "Transfer Failed.")
                else:
                    print("Error: File not found.")

            elif choice == '3':
                print("Shutting down...")
                break
            else:
                print("Invalid selection.")

    except KeyboardInterrupt:
        print("\nForce quitting...")
    finally:
        # Clean up threads
        discovery.stop()
        stop_broadcast.set()
        transfer.stop()
        pass

if __name__ == "__main__":
    main()