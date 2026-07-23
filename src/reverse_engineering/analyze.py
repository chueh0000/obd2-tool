import argparse
import can
from collections import defaultdict

def parse_args():
    parser = argparse.ArgumentParser(description="Analyze an action log against a baseline log to find changing bytes.")
    parser.add_argument("--baseline", required=True, help="Path to baseline ASC log")
    parser.add_argument("--action", required=True, help="Path to action ASC log")
    return parser.parse_args()

def analyze_baseline(baseline_file):
    print(f"Parsing baseline: {baseline_file}")
    # Dict of CAN ID -> List of min/max for each byte
    baseline_stats = defaultdict(lambda: [ {'min': 255, 'max': 0} for _ in range(8) ])
    
    log = can.ASCReader(baseline_file)
    count = 0
    for msg in log:
        if isinstance(msg, can.Message):
            count += 1
            for i, byte_val in enumerate(msg.data):
                if i < 8:
                    baseline_stats[msg.arbitration_id][i]['min'] = min(baseline_stats[msg.arbitration_id][i]['min'], byte_val)
                    baseline_stats[msg.arbitration_id][i]['max'] = max(baseline_stats[msg.arbitration_id][i]['max'], byte_val)
    print(f"Parsed {count} messages from baseline.")
    return baseline_stats

def analyze_action(action_file, baseline_stats):
    print(f"Parsing action log: {action_file}")
    
    # Store candidates: CAN ID -> byte index -> set of new values seen
    candidates = defaultdict(lambda: defaultdict(set))
    
    log = can.ASCReader(action_file)
    count = 0
    for msg in log:
        if isinstance(msg, can.Message):
            count += 1
            b_stats = baseline_stats.get(msg.arbitration_id)
            if b_stats is None:
                # Completely new ID not in baseline!
                candidates[msg.arbitration_id]['NEW_ID'] = True
                continue
                
            for i, byte_val in enumerate(msg.data):
                if i < 8:
                    b_min = b_stats[i]['min']
                    b_max = b_stats[i]['max']
                    # If the byte value is outside the baseline range, it's a candidate
                    if byte_val < b_min or byte_val > b_max:
                        candidates[msg.arbitration_id][i].add(byte_val)
                        
    print(f"Parsed {count} messages from action log.")
    return candidates

def report(candidates):
    print("\n--- ANALYSIS REPORT ---")
    if not candidates:
        print("No significant changes found compared to baseline.")
        return
        
    for can_id, byte_changes in sorted(candidates.items()):
        print(f"\nCAN ID: 0x{can_id:03X} ({can_id})")
        if 'NEW_ID' in byte_changes:
            print("  -> NEW ID (Did not exist in baseline)")
            continue
            
        for byte_idx, values in sorted(byte_changes.items()):
            # limit printing to 10 values so it doesn't flood the screen for analog signals
            val_list = list(values)
            if len(val_list) > 10:
                print(f"  -> Byte {byte_idx} changed to {len(val_list)} new distinct values (Analog signal?)")
            else:
                print(f"  -> Byte {byte_idx} changed to new values: {[hex(v) for v in val_list]}")

def main():
    args = parse_args()
    
    baseline_stats = analyze_baseline(args.baseline)
    candidates = analyze_action(args.action, baseline_stats)
    
    report(candidates)

if __name__ == "__main__":
    main()
