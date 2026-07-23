import argparse
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from diagnostics_client import DiagnosticsClient

def load_dtc_db():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, 'data', 'obd2_codes.json')
    if os.path.exists(db_path):
        with open(db_path, 'r') as f:
            try:
                return json.load(f)
            except Exception as e:
                print(f"Failed to parse obd2_codes.json: {e}")
                return []
    return []

def lookup_dtc_desc(dtc_db, code_str):
    search_code = ""
    if "(Status:" in code_str:
        raw_hex = code_str.split(" ")[0]
        if len(raw_hex) == 6:
            high_byte = int(raw_hex[0:2], 16)
            low_byte = int(raw_hex[2:4], 16)
            system = (high_byte >> 6) & 0x03
            sys_char = ['P', 'C', 'B', 'U'][system]
            digit1 = (high_byte >> 4) & 0x03
            digit2 = high_byte & 0x0F
            digit3 = (low_byte >> 4) & 0x0F
            digit4 = low_byte & 0x0F
            search_code = f"{sys_char}{digit1}{digit2:X}{digit3:X}{digit4:X}"
    else:
        search_code = code_str

    if not search_code:
        return None
        
    for entry in dtc_db:
        db_code = entry.get('Code', '')
        # some codes in db look like "P0001/SAE" or "P0001"
        if db_code.startswith(search_code):
            return entry.get('Description', 'Unknown Description')
            
    return None

def parse_args():
    parser = argparse.ArgumentParser(description="OBD2/UDS Diagnostic Trouble Code (DTC) Client.")
    parser.add_argument("action", choices=['read', 'clear'], help="Action to perform: 'read' or 'clear'")
    parser.add_argument("--interface", default="slcan", help="CAN interface type")
    parser.add_argument("--port", default="/dev/cu.usbmodem209B368539451", help="CAN interface port")
    parser.add_argument("--baud", type=int, default=500000, help="CAN bus baudrate")
    parser.add_argument("--tx", default="0x7DF", help="Transmitter ID (default: 0x7DF for broadcast OBD2)")
    parser.add_argument("--rx", default="0x7E8", help="Receiver ID (default: 0x7E8 for Engine ECU)")
    parser.add_argument("--status_mask", default="0xFF", help="UDS status mask for reading DTCs (default 0xFF)")
    return parser.parse_args()

def main():
    args = parse_args()
    
    tx_id = int(args.tx, 0)
    rx_id = int(args.rx, 0)
    status_mask = int(args.status_mask, 0)
    
    dtc_db = load_dtc_db()
    
    client = DiagnosticsClient(
        interface=args.interface,
        port=args.port,
        baud=args.baud,
        tx_id=tx_id,
        rx_id=rx_id
    )
    
    try:
        client.connect()
        print(f"\n--- OBD2/UDS DTC CLIENT ---")
        print(f"Target: TX=0x{tx_id:03X} -> RX=0x{rx_id:03X}")
        
        if args.action == 'read':
            print("\nReading DTCs...")
            dtcs = client.read_dtcs(status_mask=status_mask)
            if dtcs:
                print("\n=== Found DTCs ===")
                for dtc in dtcs:
                    desc = lookup_dtc_desc(dtc_db, dtc)
                    if desc:
                        print(f" - {dtc} : {desc}")
                    else:
                        print(f" - {dtc} : (No standard definition found)")
                print("==================\n")
            else:
                print("\nNo DTCs found or request failed.\n")
                
        elif args.action == 'clear':
            print("\nClearing DTCs...")
            success = client.clear_dtcs()
            if success:
                print("\nClear command executed successfully.\n")
            else:
                print("\nFailed to clear DTCs.\n")
                
    except Exception as e:
        print(f"\nFatal Error: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
