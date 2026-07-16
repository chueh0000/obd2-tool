import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger_base import GuidedLogger

def parse_args():
    parser = argparse.ArgumentParser(description="Guided CAN logger for Gear Shifting.")
    parser.add_argument("--interface", default="slcan", help="CAN interface type")
    parser.add_argument("--port", default="/dev/cu.usbmodem209B368539451", help="CAN interface port")
    parser.add_argument("--baud", type=int, default=500000, help="CAN bus baudrate")
    parser.add_argument("--output", default="logs/shifting_guided.asc", help="Output ASC file path")
    return parser.parse_args()

def main():
    args = parse_args()
    logger = GuidedLogger(args.interface, args.port, args.baud, args.output)
    
    try:
        logger.start()
        print("\n--- GEAR SHIFTING LOGGING ---")
        print("We will use a dynamic prompt to support PRNDL, PRND2L, buttons, etc.")
        
        logger.prompt_and_log("Ensure vehicle is currently in Park (or Neutral if manual).", "START: Baseline Gear")
        
        while True:
            gear = input("\nEnter the gear you are shifting to (e.g. P, R, N, D, 2, L) or 'q' to quit: ").strip().upper()
            if gear == 'Q':
                break
            if gear:
                logger.log_action(f"SHIFT TO: {gear}")
                input(f"Now safely shift to {gear} and press Enter when done...")
                logger.log_action(f"HOLD: In gear {gear}")
        
        print("\nLogging complete. Log saved to", args.output)
        
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        logger.stop()

if __name__ == "__main__":
    main()
