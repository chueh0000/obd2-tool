# OBD2 / CAN Bus Analysis Tool

This project provides a comprehensive toolset for analyzing CAN bus data, developing DBC files for unsupported vehicles, and reading/clearing Diagnostic Trouble Codes (DTCs) via the OBD2 port.

## Hardware & Environment

- **Host Machine:** M-series Mac or Linux Virtual Machine
- **CAN Interface:** MKS CANable v2.0 Pro
- **Connector:** OBD2 Male Pigtail to CAN interface 
- **Firmware:** Stock `canable2` firmware (`16e7497-dirty github.com/normaldotcom/canable2.git` in SLCAN mode)
  - Try [Elmue/CANable-2.5-firmware-Slcan-and-Candlelight](https://github.com/Elmue/CANable-2.5-firmware-Slcan-and-Candlelight) if:
    - You are on Windows and having USB driver stability issues.
    - You are working with high-bandwidth CAN-FD (Flexible Data-rate) and experiencing frame drops.

## Project Goals

1. **CAN Bus Sniffing & DBC Development:** 
   - Capture real-time data from an unsupported vehicle's CAN bus.
   - Reverse-engineer CAN frames and develop a custom DBC (Database CAN) file to decode proprietary vehicle signals.
2. **Vehicle Diagnostics:**
   - Query, read, and clear Diagnostic Trouble Codes (DTCs) over the CAN network using standard UDS (Unified Diagnostic Services) protocols, falling back to ISO 15031 (standard OBD2 Modes 03, 04, 07) if UDS is unsupported by the vehicle.

## Implementation Plan

### Phase 1: Hardware & Firmware Setup
- [x] Flash / verify the MKS CANable v2.0 Pro with `slcan` firmware (stock `canable2` firmware is verified and running).
- [x] Wire the OBD2 Pigtail to the CANable interface (CAN High to Pin 6, CAN Low to Pin 14 of the OBD2 connector, GND to Pin 4/5).
    - GND to Pin 5 (Signal GND) is recommended.
- [x] Verify host machine recognition (verified at `/dev/cu.usbmodem209B368539451` on macOS).

### Phase 2: Software Environment Setup
- [x] Set up a Python virtual environment (`.venv`).
- [x] Install required libraries (`python-can`, `udsoncan`, `cantools`, `can-isotp`, `pyserial`).
- [x] Verify library imports and environment functionality.

### Phase 3: Live Data (OBD2 Service 01) & PID Discovery
- [x] Extend `DiagnosticsClient` to support reading raw standard OBD2 PIDs via Service 01 requests.
- [x] Implement PID discovery by querying Availability PIDs (0x00, 0x20, 0x40, etc.) to dynamically map supported features on the vehicle.
- [x] Maintain a library of standard OBD2 PIDs (`obd2_pids.py`) mapping standard units and decoding formulas (e.g., `(A * 256 + B) / 4` for Engine RPM).
- [x] Develop a `live_data.py` CLI script supporting a `discover` action to scan available parameters, and a `monitor` action to continuously poll specified PIDs at defined intervals.

### Phase 4: Diagnostic Trouble Codes (DTCs) Management
- [x] Implement an OBD2/UDS client script using `udsoncan`, ensuring fallback support for ISO 15031 if UDS is not supported.
- [x] **Read DTCs:** Send a diagnostic request (e.g., OBD2 Service 03/07/0A or UDS Service 0x19) to the Engine Control Unit (ECU) (typically CAN ID `0x7DF` for broadcast or `0x7E0` for the specific node) and parse responses to extract DTCs.
- [x] **Clear DTCs:** Send the diagnostic request (e.g., OBD2 Service 04 or UDS Service 0x14) to clear the stored emission-related diagnostic information.
- [x] Wrap these functionalities into a Command Line Interface (`dtc.py`) for easy field use.

### Phase 5: Capturing Real-time Data & DBC Development

This phase focuses on logging raw vehicle CAN traffic and reverse-engineering the signals into a custom Database CAN (.dbc) file.

**Step 5.1: Connection & Baseline Logging**
- [ ] Connect the CANable v2.0 Pro to the vehicle's OBD2 port.
- [x] Write `src/reverse_engineering/sniff.py` utilizing `python-can` to read raw CAN frames from the slcan interface.
- [ ] Execute `src/reverse_engineering/sniff.py` to capture three distinct 60-second baselines without physical interaction:
  - **Baseline 1 (Accessory):** Key ON, Engine/Motor OFF (`logs/baseline_accessory.asc`).
  - **Baseline 2 (Active):** Powertrain Active, Parked (`logs/baseline_active.asc`).
  - **Baseline 3 (Sleep):** Dead Silence, vehicle off and asleep (`logs/baseline_sleep.asc`).
- **Verification:** Confirm the log files are generated, non-empty, and contain a consistent stream of recurring CAN IDs relevant to each vehicle state.

**Step 5.2: Action-Specific Data Capture**
- [x] Develop guided loggers in `src/loggers/` (brakes, steering, throttle, shifting, turn signals, doors) to support tagged logging sessions.
- [ ] Perform and log isolated physical actions sequentially, saving each to its own file (e.g., `logs/brakes_guided.asc`).
- **Verification:** Ensure each action log is cleanly isolated and stored in the `logs/` directory.

**Step 5.3: Data Analysis & Signal Identification**
- [x] Write `src/reverse_engineering/analyze.py` to filter out baseline idle traffic and highlight changing bytes across action logs.
- [ ] Analyze the filtered logs to isolate the specific CAN IDs and data payloads correlating to physical actions.
- **Verification:** Successfully identify and document at least one specific signal mapping (CAN ID, start bit, length, endianness).

**Step 5.4: Iterative DBC File Creation**
- [ ] Initialize `dbc/custom_vehicle.dbc` using `cantools`.
- [ ] Define messages and signals in the DBC file based on the analysis from Step 5.3.
- **Verification:** Use `cantools` to parse the DBC file and confirm there are no syntax or formatting errors.

**Step 5.5: Live Decoding Validation**
- [x] Write `src/reverse_engineering/decode.py` to consume the raw CAN bus stream and decode the frames in real-time using `dbc/custom_vehicle.dbc`.
- [ ] Run `src/reverse_engineering/decode.py` while physically interacting with the vehicle to see human-readable signal changes printed to the console.

## CLI Usage & Quickstart

All project tools are accessible via the unified CLI entrypoint `src/cli.py`:

```bash
# View help and available subcommands
python -m src.cli --help

# 1. OBD2 Live Data & Dashboard Server (Service 01)
python -m src.cli live-data monitor --mock   # Test live polling with mock data
python -m src.cli live-data discover         # Scan vehicle supported PIDs

# 2. Diagnostic Trouble Codes (DTCs)
python -m src.cli dtc read                    # Read stored DTCs
python -m src.cli dtc clear                   # Clear emission-related DTCs

# 3. Raw CAN Sniffing & Loggers (Field Execution)
python -m src.cli sniff --output logs/baseline_active.asc --duration 60
python -m src.cli log brakes                  # Guided brake action logger

# 4. Analysis & DBC Decoding
python -m src.cli analyze --baseline logs/baseline_active.asc --action logs/brakes_guided.asc
python -m src.cli decode --dbc dbc/custom_vehicle.dbc
```

## Repository Structure

```text
.
├── README.md               # Project documentation and plan
├── requirements.txt        # Python dependencies
├── data/
│   └── obd2_codes.json     # Standard OBD2 & UDS DTC definition database
├── dbc/
│   └── custom_vehicle.dbc  # Custom Database CAN file (developed during Phase 5)
├── docs/
│   └── phase5_field_instructions.md # Field execution guide
├── frontend/               # React + TypeScript + Vite Dashboard UI
│   ├── src/                # Gauges, PID tables, DTC UI
│   └── scripts/            # Asset & icon processing tools
├── logs/                   # Raw CAN bus dump files (.asc)
├── src/                    # Python Backend & CLI
│   ├── cli.py              # Unified CLI entrypoint
│   ├── core/               # Base logging infrastructure
│   ├── diagnostics/        # OBD2 Service 01/03/04 & UDS client scripts
│   ├── loggers/            # Guided physical action loggers
│   └── reverse_engineering/# Sniffing, log analysis, and live DBC decoding
└── tests/                  # Hardware & environment verification suite
```
