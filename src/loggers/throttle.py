import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.logger_base import GuidedLogger

def parse_args():
    parser = argparse.ArgumentParser(description="Guided CAN logger for Throttle System.")
    parser.add_argument("--interface", default="slcan", help="CAN interface type")
    parser.add_argument("--port", default="/dev/cu.usbmodem209B368539451", help="CAN interface port")
    parser.add_argument("--baud", type=int, default=500000, help="CAN bus baudrate")
    parser.add_argument("--output", default="logs/throttle_guided.asc", help="Output ASC file path")
    return parser.parse_args()

def main():
    args = parse_args()
    logger = GuidedLogger(args.interface, args.port, args.baud, args.output)
    
    try:
        logger.start()
        print("\n--- THROTTLE SYSTEM LOGGING ---")
        print("Prerequisite: Key ON, Engine OFF (Accessory Mode) is recommended for safety, though Engine ON works.")
        
        logger.prompt_and_log(
            "Get ready. Next, you will TAP the gas pedal lightly.",
            "START: Throttle Tap (Digital-ish)"
        )
        logger.prompt_and_log(
            "Release the pedal.",
            "END: Throttle Tap"
        )
        
        logger.prompt_and_log(
            "Next, you will SLOWLY press the pedal to the floor over ~3 seconds.",
            "START: Throttle Smooth Press to Floor"
        )
        logger.prompt_and_log(
            "Hold it at the floor for 3 seconds, then press Enter.",
            "HOLD: Throttle on Floor"
        )
        logger.prompt_and_log(
            "Now SLOWLY release the pedal completely.",
            "END: Throttle Release"
        )
        
        print("\nLogging complete. Log saved to", args.output)
        
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        logger.stop()

if __name__ == "__main__":
    main()
