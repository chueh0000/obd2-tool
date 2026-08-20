import sys
import os
import argparse

# Ensure src directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.cli <command> [<args>]")
        print("\nAvailable subcommands:")
        print("  live-data   OBD2 Service 01 Live Data Polling & PID Discovery Server")
        print("  dtc         Diagnostic Trouble Codes (Read / Clear)")
        print("  sniff       Raw CAN bus traffic sniffer (.asc log generator)")
        print("  analyze     Compare action ASC logs against baselines")
        print("  decode      Live decode CAN traffic using custom DBC file")
        print("  log         Run guided action logger sessions (brakes, steering, throttle, etc.)")
        sys.exit(1)
        
    cmd = sys.argv[1]
    
    if cmd in ['-h', '--help']:
        print("OBD2 / CAN Bus Analysis & Diagnostics Suite")
        print("\nUsage: python -m src.cli <command> [<args>]")
        print("\nAvailable subcommands:")
        print("  live-data   OBD2 Service 01 Live Data Polling & PID Discovery Server")
        print("  dtc         Diagnostic Trouble Codes (Read / Clear)")
        print("  sniff       Raw CAN bus traffic sniffer (.asc log generator)")
        print("  analyze     Compare action ASC logs against baselines")
        print("  decode      Live decode CAN traffic using custom DBC file")
        print("  log         Run guided action logger sessions")
        sys.exit(0)

    # Re-slice sys.argv for the target module
    sys.argv = [f"{sys.argv[0]} {cmd}"] + sys.argv[2:]

    if cmd == "live-data":
        from diagnostics import live_data
        live_data.main()
    elif cmd == "dtc":
        from diagnostics import dtc
        dtc.main()
    elif cmd == "sniff":
        from reverse_engineering import sniff
        sniff.main()
    elif cmd == "analyze":
        from reverse_engineering import analyze
        analyze.main()
    elif cmd == "decode":
        from reverse_engineering import decode
        decode.main()
    elif cmd == "log":
        if len(sys.argv) < 2:
            print("Usage: python -m src.cli log <target>")
            print("Targets: brakes, steering, throttle, shifting, turn_signals, doors")
            sys.exit(1)
        target = sys.argv[1]
        sys.argv = [f"{sys.argv[0]} {target}"] + sys.argv[2:]
        if target == 'brakes':
            from loggers import brakes
            brakes.main()
        elif target == 'steering':
            from loggers import steering
            steering.main()
        elif target == 'throttle':
            from loggers import throttle
            throttle.main()
        elif target == 'shifting':
            from loggers import shifting
            shifting.main()
        elif target == 'turn_signals':
            from loggers import turn_signals
            turn_signals.main()
        elif target == 'doors':
            from loggers import doors
            doors.main()
        else:
            print(f"Unknown log target '{target}'. Choices are: brakes, steering, throttle, shifting, turn_signals, doors.")
    else:
        print(f"Unknown command '{cmd}'. Run 'python -m src.cli --help' for usage.")
        sys.exit(1)

if __name__ == "__main__":
    main()
