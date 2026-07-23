import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from diagnostics import DiagnosticsClient

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
                    print(f" - {dtc}")
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
