# OBD2 / CAN Bus Analysis Tool

This project provides a comprehensive toolset for analyzing CAN bus data, developing DBC files for unsupported vehicles, and reading/clearing Diagnostic Trouble Codes (DTCs) via the OBD2 port.

## Hardware & Environment

- **Host Machine:** M-series Mac or Linux Virtual Machine
- **CAN Interface:** MKS CANable v2.0 Pro
- **Connector:** OBD2 Pigtail to CAN interface
- **Firmware:** [Elmue/CANable-2.5-firmware-Slcan-and-Candlelight](https://github.com/Elmue/CANable-2.5-firmware-Slcan-and-Candlelight)

## Project Goals

1. **CAN Bus Sniffing & DBC Development:** 
   - Capture real-time data from an unsupported vehicle's CAN bus.
   - Reverse-engineer CAN frames and develop a custom DBC (Database CAN) file to decode proprietary vehicle signals.
2. **Vehicle Diagnostics:**
   - Query, read, and clear Diagnostic Trouble Codes (DTCs) over the CAN network using standard OBD2 (Mode 03, 04, 07) or UDS (Unified Diagnostic Services) protocols.

## Implementation Plan

### Phase 1: Hardware & Firmware Setup
- [ ] Flash the MKS CANable v2.0 Pro with `Candlelight` or `slcan` firmware (Candlelight is generally preferred for Linux SocketCAN compatibility; slcan is often easier for Mac environments).
- [ ] Wire the OBD2 Pigtail to the CANable interface (CAN High to Pin 6, CAN Low to Pin 14 of the OBD2 connector).
- [ ] Verify host machine recognition (e.g., via `/dev/cu.usbmodem*` on Mac or `ip link show can0` on Linux).

### Phase 2: Software Environment Setup
- [ ] Set up a Python virtual environment.
- [ ] Install required libraries:
  - `python-can` (for generic CAN bus communication).
  - `udsoncan` (for handling UDS diagnostics).
  - `cantools` (for parsing and creating DBC files).
  - `can-utils` (if running on a Linux VM for `candump`, `cansniffer`, `cansend`).

### Phase 3: Capturing Real-time Data & DBC Development
- [ ] Connect the CANable to the vehicle's OBD2 port and bring up the CAN interface.
- [ ] Establish a baseline of idle CAN traffic.
- [ ] Isolate single actions and log raw CAN traffic for each system we want to analyze (e.g., pedal position, lights, steering, wheel speed, engine rpm, transmission, etc.).
- [ ] Analyze the logs (using `cansniffer` or Python scripts) to identify changing bytes correlated to physical actions.
- [ ] Iteratively build a `.dbc` file using `cantools` or a DBC editor mapping the identified CAN IDs and byte ranges to human-readable signals.
- [ ] Write a Python script to consume the `.dbc` file and output live, decoded vehicle metrics.

### Phase 4: Diagnostic Trouble Codes (DTCs) Management
- [ ] Implement an OBD2/UDS client script using `udsoncan`.
- [ ] **Read DTCs:** Send a diagnostic request (e.g., OBD2 Service 03) to the Engine Control Unit (ECU) (typically CAN ID `0x7DF` for broadcast or `0x7E0` for the specific node) and parse the multiframe ISO-TP response to extract DTCs.
- [ ] **Clear DTCs:** Send the diagnostic request (e.g., OBD2 Service 04) to clear the stored emission-related diagnostic information.
- [ ] Wrap these functionalities into a Command Line Interface (CLI) for easy field use.

## Repository Structure (Proposed)
```text
.
├── README.md               # Project documentation and plan
├── requirements.txt        # Python dependencies
├── dbc/
│   └── custom_vehicle.dbc  # Custom DBC file developed during Phase 3
├── src/
│   ├── sniff.py            # Script for capturing and logging CAN traffic
│   ├── decode.py           # Script for live-decoding using the DBC file
│   └── diagnostics.py      # Script for reading and clearing DTCs
└── logs/                   # Directory for storing raw CAN dumps
```
