import argparse
import sys
import os
import time
import threading
import json
import asyncio
import uvicorn
import math
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from diagnostics_client import DiagnosticsClient
from obd2_pids import decode_pid, get_pid_info, OBD2_PIDS

def parse_args():
    parser = argparse.ArgumentParser(description="OBD2 Live Data (Service 01) Client.")
    parser.add_argument("action", choices=['discover', 'monitor'], help="Action to perform")
    parser.add_argument("--pids", help="Comma-separated list of hex PIDs to monitor. If omitted, discovers and monitors all supported PIDs.")
    parser.add_argument("--interval", type=float, default=0.1, help="Polling interval in seconds")
    parser.add_argument("--interface", default="slcan", help="CAN interface type")
    parser.add_argument("--port", default="/dev/cu.usbmodem209B368539451", help="CAN interface port")
    parser.add_argument("--baud", type=int, default=500000, help="CAN bus baudrate")
    parser.add_argument("--tx", default="0x7DF", help="Transmitter ID (default: 0x7DF)")
    parser.add_argument("--rx", default="0x7E8", help="Receiver ID (default: 0x7E8)")
    parser.add_argument("--mock", action="store_true", help="Enable mock mode to test the UI without a car")
    return parser.parse_args()

from contextlib import asynccontextmanager

global_loop = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global global_loop
    global_loop = asyncio.get_running_loop()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_connections = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

def broadcast_data(data: dict):
    global global_loop
    if global_loop and global_loop.is_running():
        message = json.dumps(data)
        async def _broadcast():
            disconnected = []
            for connection in active_connections:
                try:
                    await connection.send_text(message)
                except Exception:
                    disconnected.append(connection)
            for c in disconnected:
                if c in active_connections:
                    active_connections.remove(c)
        asyncio.run_coroutine_threadsafe(_broadcast(), global_loop)

# Mount frontend dist if it exists
frontend_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'frontend', 'dist')
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")

def generate_mock_value(pid: int, t: float):
    if pid == 0x0C: # Engine RPM
        return round(1800 + 1200 * math.sin(t * 0.3) + 50 * math.sin(t * 1.5), 1)
    elif pid == 0x0D: # Vehicle speed
        return round(max(0, 45 + 35 * math.sin(t * 0.15)), 1)
    elif pid in (0x04, 0x43): # Engine Load
        return round(20 + 50 * (0.5 + 0.5 * math.sin(t * 0.3)), 1)
    elif pid in (0x05, 0x67): # Coolant Temp 1 & 2
        offset = 0 if pid == 0x05 else -1.5
        return round(88 + offset + 4 * math.sin(t * 0.03), 1)
    elif pid == 0x5C: # Oil Temp
        return round(95 + 3 * math.sin(t * 0.02), 1)
    elif pid == 0x0F: # Intake Air Temp
        return round(28 + 2 * math.sin(t * 0.05), 1)
    elif pid == 0x46: # Ambient Air Temp
        return 22.0
    elif pid in (0x3C, 0x3D, 0x3E, 0x3F): # Catalyst Temps
        offset = (pid - 0x3C) * 15
        return round(420 + offset + 60 * math.sin(t * 0.1), 1)
    elif pid in (0x06, 0x08): # STFT
        return round(3.0 * math.sin(t * 0.8), 2)
    elif pid in (0x07, 0x09): # LTFT
        return round(1.2 + 0.5 * math.sin(t * 0.05), 2)
    elif 0x14 <= pid <= 0x1B: # O2 Sensor Voltages
        phase = (pid - 0x14) * 0.5
        return round(0.45 + 0.38 * math.sin(t * 1.5 + phase), 3)
    elif pid == 0x24:
        return f"{1.00 + 0.02 * math.sin(t):.3f} ratio, {0.70 + 0.05 * math.sin(t):.3f} V"
    elif pid == 0x34:
        return f"{1.00 + 0.02 * math.sin(t):.3f} ratio, {0.05 * math.sin(t):.3f} mA"
    elif pid == 0x42: # Control Module Voltage
        return round(13.9 + 0.25 * math.sin(t * 0.1), 2)
    elif pid in (0x11, 0x45, 0x47, 0x48, 0x49, 0x4A, 0x4B, 0x4C, 0x5A): # Throttle & Pedal
        return round(12 + 35 * (0.5 + 0.5 * math.sin(t * 0.3)), 1)
    elif pid == 0x10: # MAF
        return round(4.5 + 18 * (0.5 + 0.5 * math.sin(t * 0.3)), 2)
    elif pid == 0x0B: # MAP
        return round(35 + 45 * (0.5 + 0.5 * math.sin(t * 0.3)), 1)
    elif pid == 0x33: # Barometric Pressure
        return 101.3
    elif pid == 0x0A: # Fuel Pressure
        return round(380 + 15 * math.sin(t * 0.2), 1)
    elif pid in (0x22, 0x23, 0x59): # High Fuel Pressures
        return round(3800 + 200 * math.sin(t * 0.2), 1)
    elif pid == 0x2F: # Fuel Tank Level
        return 68.5
    elif pid == 0x0E: # Timing Advance
        return round(14 + 10 * math.sin(t * 0.4), 1)
    elif pid in (0x2C, 0x2E): # Commanded EGR / Purge
        return round(15 + 20 * (0.5 + 0.5 * math.sin(t * 0.2)), 1)
    elif pid == 0x2D: # EGR Error
        return round(0.5 * math.sin(t * 0.5), 2)
    elif pid in (0x32, 0x54): # Evap Vapor Pressure
        return round(12 * math.sin(t * 0.1), 1)
    elif pid == 0x53:
        return 101.3
    elif pid == 0x1F: # Run time
        return int(t)
    elif pid == 0x21: # Distance with MIL
        return 0
    elif pid == 0x30: # Warm-ups
        return 14
    elif pid == 0x31: # Distance since cleared
        return 452
    elif pid == 0x4D: # Time with MIL
        return 0
    elif pid == 0x4E: # Time since cleared
        return 1280
    elif pid == 0x51: # Fuel Type
        return "Gasoline"
    elif pid == 0x1C: # OBD Standards
        return "OBD-II (CARB)"
    elif pid == 0x5F: # Emission requirements
        return "EOBD, OBD-II"
    elif pid == 0x52:
        return 10.0
    elif pid == 0x5B:
        return 82.0
    elif pid in (0x61, 0x62): # Torque %
        return round(25 + 40 * (0.5 + 0.5 * math.sin(t * 0.3)), 1)
    elif pid == 0x63: # Torque Nm
        return 350
    else:
        info = get_pid_info(pid)
        if not info.get("dynamic", True):
            return "00FF00FF"
        return round(50 + 10 * math.sin(t), 2)

def main():
    args = parse_args()
    
    tx_id = int(args.tx, 0)
    rx_id = int(args.rx, 0)
    
    client = DiagnosticsClient(
        interface=args.interface,
        port=args.port,
        baud=args.baud,
        tx_id=tx_id,
        rx_id=rx_id
    )
    
    try:
        if not args.mock:
            client.connect()
        print(f"\n--- OBD2 LIVE DATA CLIENT ---")
        
        if args.action == 'discover':
            print("Discovering supported PIDs...")
            supported = client.get_supported_pids()
            if supported:
                print("\n=== Supported PIDs ===")
                for pid in supported:
                    info = get_pid_info(pid)
                    print(f" - 0x{pid:02X} : {info['name']}")
                print("======================\n")
            else:
                print("No supported PIDs found or request failed.")
                
        elif args.action == 'monitor':
            if not args.pids:
                if args.mock:
                    print("Mock mode: Monitoring ALL defined PIDs")
                    # Exclude "PIDs supported" bitmasks and static string PIDs
                    pids = [p for p in OBD2_PIDS.keys() if p not in (0x00, 0x20, 0x40, 0x60, 0x80, 0xA0, 0xC0)]
                else:
                    print("No --pids specified. Discovering all supported PIDs to monitor...")
                    pids = client.get_supported_pids()
                    if not pids:
                        print("Failed to discover any supported PIDs or request failed. Exiting.")
                        return
            else:
                pids = [int(p.strip(), 16) for p in args.pids.split(',')]
                
            print(f"Monitoring PIDs: {[f'0x{p:02X}' for p in pids]}")
            print("Web dashboard available at: http://localhost:8000")
            print("Press Ctrl+C to stop.")
            
            def polling_thread_func(client_ref, pid_list, interval, is_mock):
                try:
                    print("\n" + "="*30)
                    for _ in pid_list:
                        print()
                    
                    start_time = time.time()
                    while True:
                        sys.stdout.write(f"\033[{len(pid_list)}A")
                        dashboard_data = {}
                        t = time.time() - start_time
                        
                        for pid in pid_list:
                            info = get_pid_info(pid)
                            if is_mock:
                                val = generate_mock_value(pid, t)
                                val_str = f"{val:.2f}" if isinstance(val, float) else str(val)
                                sys.stdout.write(f"\033[K{info['name']} (0x{pid:02X}): {val_str} (MOCK) {info['unit']}\n")
                                dashboard_data[info['name']] = {
                                    "value": val, 
                                    "unit": info['unit'], 
                                    "pid": f"0x{pid:02X}",
                                    "cluster": info.get("cluster", "Uncategorized"),
                                    "dynamic": info.get("dynamic", True),
                                    "group": info.get("group", info['name']),
                                    "min": info.get("min", None),
                                    "max": info.get("max", None)
                                }
                            else:
                                raw_data = client_ref.read_pid(pid)
                                if raw_data:
                                    val = decode_pid(pid, raw_data)
                                    if isinstance(val, float):
                                        val_str = f"{val:.2f}"
                                    else:
                                        val_str = str(val)
                                    sys.stdout.write(f"\033[K{info['name']} (0x{pid:02X}): {val_str} {info['unit']}\n")
                                    dashboard_data[info['name']] = {
                                        "value": val, 
                                        "unit": info['unit'], 
                                        "pid": f"0x{pid:02X}",
                                        "cluster": info.get("cluster", "Uncategorized"),
                                        "dynamic": info.get("dynamic", True),
                                        "group": info.get("group", info['name']),
                                        "min": info.get("min", None),
                                        "max": info.get("max", None)
                                    }
                                else:
                                    sys.stdout.write(f"\033[K{info['name']} (0x{pid:02X}): NO RESPONSE\n")
                        
                        sys.stdout.flush()
                        if dashboard_data:
                            dashboard_data["timestamp"] = time.time()
                            broadcast_data(dashboard_data)
                        
                        time.sleep(interval)
                except Exception as e:
                    pass
            
            polling_thread = threading.Thread(target=polling_thread_func, args=(client, pids, args.interval, args.mock), daemon=True)
            polling_thread.start()
            
            # Start FastAPI server on main thread
            uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")

    except Exception as e:
        print(f"\nFatal Error: {e}")
    finally:
        if not args.mock:
            client.disconnect()

if __name__ == "__main__":
    main()
