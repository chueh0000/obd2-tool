import argparse
import can
import cantools
import time

def parse_args():
    parser = argparse.ArgumentParser(description="Live decode CAN traffic using a DBC file.")
    parser.add_argument("--interface", default="slcan", help="CAN interface type")
    parser.add_argument("--port", default="/dev/cu.usbmodem209B368539451", help="CAN interface port")
    parser.add_argument("--baud", type=int, default=500000, help="CAN bus baudrate")
    parser.add_argument("--dbc", default="dbc/custom_vehicle.dbc", help="Path to DBC file")
    return parser.parse_args()

def main():
    args = parse_args()
    
    print(f"Loading DBC file: {args.dbc}")
    try:
        db = cantools.database.load_file(args.dbc)
    except Exception as e:
        print(f"Failed to load DBC: {e}")
        return

    print(f"Connecting to {args.interface} at {args.port} ({args.baud} baud)...")
    try:
        bus = can.interface.Bus(interface=args.interface, channel=args.port, bitrate=args.baud)
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    print("Listening for messages... (Ctrl+C to stop)")
    
    try:
        while True:
            msg = bus.recv(timeout=1.0)
            if msg is not None:
                try:
                    # Attempt to decode the message
                    decoded = db.decode_message(msg.arbitration_id, msg.data)
                    msg_name = db.get_message_by_frame_id(msg.arbitration_id).name
                    print(f"[{time.strftime('%H:%M:%S')}] {msg_name}: {decoded}")
                except cantools.database.errors.DecodeError:
                    # Message matches DBC but data is invalid
                    pass
                except KeyError:
                    # Message ID not in DBC
                    pass
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        bus.shutdown()

if __name__ == "__main__":
    main()
