# Phase 3: Field Execution & DBC Development Guide

This guide details the remaining steps required to complete Phase 3. You will be moving from the development environment to the physical vehicle to capture raw CAN data, analyze it, and build the DBC database.

## Prerequisites
- Laptop with the `.venv` activated.
- MKS CANable v2.0 Pro connected via USB.
- OBD2 Male Pigtail securely connected to the CANable (Pin 6 -> CAN_H, Pin 14 -> CAN_L, Pin 4/5 -> GND).
- Vehicle keys.

---

## Step 1: Capture Baselines
*Goal: Record the background "noise" of the vehicle in different power states so we can filter it out later.*

1. Connect the OBD2 pigtail to the vehicle's diagnostic port.
2. Ensure the vehicle is completely OFF (Sleep Mode).
3. Run: `python src/reverse_engineering/sniff.py --output logs/baseline_sleep.asc` (Wait 60s).
4. Turn the key to Accessory Mode (Engine OFF).
5. Run: `python src/reverse_engineering/sniff.py --output logs/baseline_accessory.asc` (Wait 60s).
6. Turn the Engine ON (Powertrain Active, Parked).
7. Run: `python src/reverse_engineering/sniff.py --output logs/baseline_active.asc` (Wait 60s).

---

## Step 2: Capture Action Logs
*Goal: Use the guided loggers to isolate specific physical actions.*

Run each of the following scripts. Read the prerequisite warnings printed on the console, ensure the vehicle is in the correct state, and follow the step-by-step prompts exactly.

1. **Brakes**: `python src/loggers/brakes.py`
2. **Steering**: `python src/loggers/steering.py`
3. **Throttle**: `python src/loggers/throttle.py`
4. **Shifting**: `python src/loggers/shifting.py`
5. **Turn Signals**: `python src/loggers/turn_signals.py`
6. **Doors/Locks**: `python src/loggers/doors.py`

*Tip: If you mess up an action during a logging session, just hit `Ctrl+C` and run the script again to keep the log clean.*

---

## Step 3: Analyze the Data
*Goal: Compare the action logs against the baselines to discover which CAN IDs and Bytes represent the physical actions.*

Move back to your desk. For each system, run the analysis script comparing the appropriate baseline to the action log. 

**Example (Brakes):**
Since braking was likely logged in Active Mode, compare it against the active baseline:
```bash
python src/reverse_engineering/analyze.py --baseline logs/baseline_active.asc --action logs/brakes_guided.asc
```

The script will output something like:
```text
CAN ID: 0x1A4
  -> Byte 3 changed to new values: ['0x0', '0x1']
  -> Byte 5 changed to 35 new distinct values (Analog signal?)
```
In this hypothetical example, Byte 3 is the digital Brake Switch, and Byte 5 is the analog Brake Pedal Position.

---

## Step 4: Iteratively Build the DBC
*Goal: Map your discoveries into a formal CAN database.*

1. Open `dbc/custom_vehicle.dbc` in a text editor or a DBC editing tool (like Kvaser Database Editor, Vector CANdb++, or a VSCode DBC extension).
2. For every signal you discovered in Step 3, define a new Message (`BO_`) and Signal (`SG_`).
   - Example for the brake discovery above:
     ```text
     BO_ 420 BRAKE_SYSTEM: 8 Vector__XXX
      SG_ Brake_Switch : 24|1@1+ (1,0) [0|1] "" Vector__XXX
      SG_ Brake_Pedal_Pos : 40|8@1+ (0.392,0) [0|100] "%" Vector__XXX
     ```
3. Save the DBC file.

---

## Step 5: Live Decoding Validation
*Goal: Prove that your DBC file correctly decodes live vehicle traffic.*

1. Connect back to the active vehicle.
2. Run the live decoder:
   ```bash
   python src/reverse_engineering/decode.py --dbc dbc/custom_vehicle.dbc
   ```
3. Physically interact with the vehicle (e.g., press the brakes, turn the steering wheel).
4. Watch the console output. You should see human-readable updates like:
   `[14:32:05] BRAKE_SYSTEM: {'Brake_Switch': 1, 'Brake_Pedal_Pos': 45.2}`
