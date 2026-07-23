import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.logger_base import GuidedLogger

def parse_args():
    parser = argparse.ArgumentParser(description="Guided CAN logger for Door Locks and Keyless Entry.")
    parser.add_argument("--interface", default="slcan", help="CAN interface type")
    parser.add_argument("--port", default="/dev/cu.usbmodem209B368539451", help="CAN interface port")
    parser.add_argument("--baud", type=int, default=500000, help="CAN bus baudrate")
    parser.add_argument("--output", default="logs/doors_guided.asc", help="Output ASC file path")
    return parser.parse_args()

def main():
    args = parse_args()
    logger = GuidedLogger(args.interface, args.port, args.baud, args.output)
    
    try:
        logger.start()
        print("\n--- DOORS & LOCKS SYSTEM LOGGING ---")
        print("Prerequisite: Key OFF or Accessory mode. The Body Control Module is usually awake to listen for fobs.")
        print("Use the door panel switches, the physical key fob, or keyless touch handles as applicable to your car.")
        
        # Locks
        print("\n[ACTION A - LOCK/UNLOCK STATUS]")
        logger.prompt_and_log(
            "LOCK the doors (using fob, interior switch, or keyless touch).",
            "START: Doors Locked"
        )
        logger.prompt_and_log(
            "UNLOCK the doors.",
            "END: Doors Unlocked"
        )
        
        # Physical door states (ajar)
        print("\n[ACTION B - DOOR AJAR STATUS]")
        logger.prompt_and_log(
            "OPEN the Driver's Door.",
            "START: Driver Door Opened"
        )
        logger.prompt_and_log(
            "CLOSE the Driver's Door.",
            "END: Driver Door Closed"
        )
        
        logger.prompt_and_log(
            "OPEN the Passenger's Door.",
            "START: Passenger Door Opened"
        )
        logger.prompt_and_log(
            "CLOSE the Passenger's Door.",
            "END: Passenger Door Closed"
        )
        
        # Optional custom inputs
        print("\n[ACTION C - CUSTOM ACTIONS]")
        print("Use this section to test any specific fob buttons (e.g. Trunk, Panic) or rear doors.")
        while True:
            action = input("\nEnter a custom action to test (or 'q' to quit): ").strip()
            if action.lower() == 'q':
                break
            if action:
                logger.prompt_and_log(f"Execute action: {action}", f"ACTION: {action}")
        
        print("\nLogging complete. Log saved to", args.output)
        
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        logger.stop()

if __name__ == "__main__":
    main()
