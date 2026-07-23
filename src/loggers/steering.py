import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.logger_base import GuidedLogger

def parse_args():
    parser = argparse.ArgumentParser(description="Guided CAN logger for Steering System.")
    parser.add_argument("--interface", default="slcan", help="CAN interface type")
    parser.add_argument("--port", default="/dev/cu.usbmodem209B368539451", help="CAN interface port")
    parser.add_argument("--baud", type=int, default=500000, help="CAN bus baudrate")
    parser.add_argument("--output", default="logs/steering_guided.asc", help="Output ASC file path")
    return parser.parse_args()

def main():
    args = parse_args()
    logger = GuidedLogger(args.interface, args.port, args.baud, args.output)
    
    try:
        logger.start()
        print("\n--- STEERING SYSTEM LOGGING ---")
        print("Prerequisite: Engine/Motor ON (Active mode) is recommended to enable power steering.")
        
        logger.prompt_and_log("Start with the steering wheel perfectly CENTERED.", "START: Steering Centered")
        
        # Left turns
        logger.prompt_and_log("Turn LEFT 90 degrees (1/4 turn) and hold.", "HOLD: Steering Left 90")
        logger.prompt_and_log("Turn LEFT 180 degrees (1/2 turn) and hold.", "HOLD: Steering Left 180")
        logger.prompt_and_log("Turn LEFT 360 degrees (1 full turn) and hold.", "HOLD: Steering Left 360")
        logger.prompt_and_log("Turn LEFT to FULL LOCK and hold.", "HOLD: Steering Left Lock")
        
        logger.prompt_and_log("Return to CENTER and hold.", "HOLD: Steering Centered")
        
        # Right turns
        logger.prompt_and_log("Turn RIGHT 90 degrees (1/4 turn) and hold.", "HOLD: Steering Right 90")
        logger.prompt_and_log("Turn RIGHT 180 degrees (1/2 turn) and hold.", "HOLD: Steering Right 180")
        logger.prompt_and_log("Turn RIGHT 360 degrees (1 full turn) and hold.", "HOLD: Steering Right 360")
        logger.prompt_and_log("Turn RIGHT to FULL LOCK and hold.", "HOLD: Steering Right Lock")
        
        logger.prompt_and_log("Return to CENTER.", "END: Steering Centered")
        
        print("\nLogging complete. Log saved to", args.output)
        
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        logger.stop()

if __name__ == "__main__":
    main()
