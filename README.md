# P2P Local Network File Transfer

A decentralized, cross-platform file-sharing application designed for local network environments. Built for our Computer Networks class, this application acts as a cross-platform "AirDrop," utilizing UDP broadcasts for peer discovery and TCP sockets for reliable file chunk streaming.

## System Architecture

This application bypasses central servers by operating in two distinct network phases:
1. **Discovery Phase (UDP):** Nodes broadcast and listen for presence packets on the local subnet to dynamically build a directory of active peers.
2. **Transfer Phase (TCP):** Upon user initiation, a reliable TCP socket is established to stream binary file chunks directly from the sender to the receiver, preventing memory overflow on large files.

## Project Structure

The repository uses the standard Python `src/` layout to isolate application code from configurations and tests.

```text
p2p_app/
├── .gitignore
├── README.md
├── requirements.txt
├── src/
│   └── p2p_core/
│       ├── __init__.py      # Package initializer
│       ├── main.py          # Entry point and UI/CLI loop
│       ├── discovery.py     # UDP broadcast and listening threads
│       ├── transfer.py      # TCP server and file chunking logic
│       └── utils.py         # Helper functions (IP routing, hashing)
└── tests/                   # Unit tests
    ├── test_discovery.py
    └── test_transfer.py
```
## Local Development Setup
1. Clone the repository
```bash
git clone https://github.com/AJB233/comp-networks-project.git
cd p2p_app
```
2. Create the virtual environment
```bash
python3 -m venv venv
```
3. Activate the virtual environment
```bash
source venv/bin/activate
```
4. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Running the Application
Ensure your virtual environment is active. Start the application from the root directory
```bash
python3 src/p2p_core/main.py
