import argparse
import can
import time
import os

def parse_args():
    parser = argparse.ArgumentParser(description="Capture raw CAN traffic to a file.")
    parser.add_argument("--interface", default="slcan", help="CAN interface type (e.g., slcan, virtual)")
    parser.add_argument("--port", default="/dev/cu.usbmodem209B368539451", help="CAN interface port/channel")
    parser.add_argument("--baud", type=int, default=500000, help="CAN bus baudrate")
    parser.add_argument("--duration", type=int, default=60, help="Duration to sniff in seconds")
    parser.add_argument("--output", default="logs/baseline_idle.asc", help="Output ASC file path")
    return parser.parse_args()

def main():
    args = parse_args()
    
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    print(f"Connecting to {args.interface} at {args.port} ({args.baud} baud)...")
    try:
        bus = can.interface.Bus(interface=args.interface, channel=args.port, bitrate=args.baud)
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    print(f"Logging to {args.output} for {args.duration} seconds...")
    
    logger = can.Logger(args.output)
    
    start_time = time.time()
    msg_count = 0
    
    try:
        while (time.time() - start_time) < args.duration:
            msg = bus.recv(timeout=1.0)
            if msg is not None:
                logger.on_message_received(msg)
                msg_count += 1
                if msg_count % 100 == 0:
                    print(f"Captured {msg_count} messages... ({(time.time() - start_time):.1f}s)", end='\r')
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    
    logger.stop()
    bus.shutdown()
    print(f"\nDone. Captured {msg_count} messages to {args.output}.")

if __name__ == "__main__":
    main()
