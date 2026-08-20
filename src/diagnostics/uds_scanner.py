import can
import time
import argparse

def scan_uds(baudrate):
    print(f"\n--- Scanning for UDS endpoints at {baudrate} baud (IDs 0x700 - 0x7FF) ---")
    try:
        bus = can.interface.Bus(interface='slcan', channel='/dev/cu.usbmodem209B368539451', bitrate=baudrate)
        
        # Clear out any old messages
        for _ in range(100):
            if not bus.recv(0.01):
                break

        found_endpoints = []

        # Scan standard 11-bit diagnostic range
        for tx_id in range(0x700, 0x800):
            # UDS Service 0x10 (Diagnostic Session Control), Sub-function 0x01 (Default Session)
            data = [0x02, 0x10, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00]
            msg = can.Message(arbitration_id=tx_id, data=data, is_extended_id=False)
            bus.send(msg)

            # Listen briefly for a response
            timeout = time.time() + 0.05
            while time.time() < timeout:
                recv_msg = bus.recv(0.01)
                if recv_msg:
                    msg_id = recv_msg.arbitration_id
                    # Expect response on tx_id + 8 (standard offset) or any ID in 0x700-0x7FF that isn't what we sent
                    if not recv_msg.is_extended_id and 0x700 <= msg_id <= 0x7FF and msg_id != tx_id:
                        if len(recv_msg.data) >= 3 and recv_msg.data[1] in [0x50, 0x7F]:
                            print(f"[+] Found UDS Endpoint! Request ID: {hex(tx_id)} -> Response ID: {hex(msg_id)} (Data: {recv_msg.data.hex()})")
                            found_endpoints.append((tx_id, msg_id))
                            break

        if not found_endpoints:
            print("No UDS endpoints found in 11-bit range.")
        else:
            print(f"\nTotal endpoints found: {len(found_endpoints)}")
            
        bus.shutdown()
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baud", type=int, default=500000, help="CAN bus baudrate")
    args = parser.parse_args()

    scan_uds(args.baud)

if __name__ == "__main__":
    main()
