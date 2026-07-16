import argparse
import sys
import os

# Add src/ to python path so we can import logger_base
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger_base import GuidedLogger

def parse_args():
    parser = argparse.ArgumentParser(description="Guided CAN logger for Braking System.")
    parser.add_argument("--interface", default="slcan", help="CAN interface type")
    parser.add_argument("--port", default="/dev/cu.usbmodem209B368539451", help="CAN interface port")
    parser.add_argument("--baud", type=int, default=500000, help="CAN bus baudrate")
    parser.add_argument("--output", default="logs/brakes_guided.asc", help="Output ASC file path")
    return parser.parse_args()

def main():
    args = parse_args()
    logger = GuidedLogger(args.interface, args.port, args.baud, args.output)
    
    try:
        logger.start()
        print("\n--- BRAKES SYSTEM LOGGING ---")
        print("Prerequisite: Vehicle should be in Key ON (Accessory or Active) mode.")
        
        # Action A: Digital (Brake Switch)
        print("\n[ACTION A - DIGITAL: Brake Switch]")
        print("Goal: Look for a single bit flipping from 0 to 1.")
        logger.prompt_and_log(
            "Get ready. Next, you will tap the brake pedal lightly to turn on the brake lights.",
            "START: Brake Tap (Digital)"
        )
        logger.prompt_and_log(
            "Now release the brake pedal.",
            "END: Brake Tap (Digital)"
        )
        
        # Action B: Analog (Pedal Position/Pressure)
        print("\n[ACTION B - ANALOG: Pedal Position / Pressure]")
        print("Goal: Look for a byte or two representing percentage or pressure smoothly ramping up/down.")
        logger.prompt_and_log(
            "Get ready. Next, you will slowly press the brake pedal to the floor.",
            "START: Brake Press to Floor (Analog)"
        )
        logger.prompt_and_log(
            "Hold it on the floor for 3 seconds, then press Enter.",
            "HOLD: Brake on Floor"
        )
        logger.prompt_and_log(
            "Now slowly release the brake pedal completely.",
            "END: Brake Release (Analog)"
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
