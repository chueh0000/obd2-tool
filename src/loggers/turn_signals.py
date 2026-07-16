import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger_base import GuidedLogger

def parse_args():
    parser = argparse.ArgumentParser(description="Guided CAN logger for Turn Signals and Hazards.")
    parser.add_argument("--interface", default="slcan", help="CAN interface type")
    parser.add_argument("--port", default="/dev/cu.usbmodem209B368539451", help="CAN interface port")
    parser.add_argument("--baud", type=int, default=500000, help="CAN bus baudrate")
    parser.add_argument("--output", default="logs/turn_signals_guided.asc", help="Output ASC file path")
    return parser.parse_args()

def main():
    args = parse_args()
    logger = GuidedLogger(args.interface, args.port, args.baud, args.output)
    
    try:
        logger.start()
        print("\n--- TURN SIGNALS & HAZARDS LOGGING ---")
        print("Prerequisite: Key ON (Accessory or Active) mode.")
        
        logger.prompt_and_log("Turn LEFT signal ON.", "START: Left Signal ON")
        logger.prompt_and_log("Turn LEFT signal OFF.", "END: Left Signal OFF")
        
        logger.prompt_and_log("Turn RIGHT signal ON.", "START: Right Signal ON")
        logger.prompt_and_log("Turn RIGHT signal OFF.", "END: Right Signal OFF")
        
        logger.prompt_and_log("Turn HAZARD lights ON.", "START: Hazards ON")
        logger.prompt_and_log("Turn HAZARD lights OFF.", "END: Hazards OFF")
        
        print("\nLogging complete. Log saved to", args.output)
        
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        logger.stop()

if __name__ == "__main__":
    main()
