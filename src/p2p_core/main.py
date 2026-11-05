import time
import os
from utils import get_local_ip

# Import stubs (these will be built by your team)
# from discovery import PeerDiscovery
# from transfer import FileTransfer

def print_menu():
    print("\n--- P2P AirDrop ---")
    print("1. View available peers")
    print("2. Send a file")
    print("3. Exit")

def main():
    my_ip = get_local_ip()
    my_handle = input("Enter your display name: ")
    print(f"Starting node on {my_ip} as {my_handle}...")

    # Initialize Modules (Stubbed for now)
    # discovery = PeerDiscovery(handle=my_handle)
    # discovery.start()
    # transfer = FileTransfer(save_dir="./received_files")
    # transfer.start_listening()

    try:
        while True:
            print_menu()
            choice = input("Select an option: ")

            if choice == '1':
                print("\n[Scanning local network...]")
                # peers = discovery.get_peers()
                # for ip, name in peers.items():
                #     print(f"- {name} ({ip})")
                print("- Dummy Student (192.168.1.99)") # Placeholder

            elif choice == '2':
                target_ip = input("Enter target IP address: ")
                filepath = input("Enter full path to file: ")
                
                if os.path.exists(filepath):
                    print(f"Initiating transfer to {target_ip}...")
                    # success = transfer.send_file(target_ip, filepath)
                    # print("Transfer Complete!" if success else "Transfer Failed.")
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
        # discovery.stop()
        # transfer.stop()
        pass

if __name__ == "__main__":
    main()