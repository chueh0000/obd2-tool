import can
import time
import argparse

def test_obd(baudrate, tx_id, is_extended, padding_byte):
    print(f"\n--- Testing Baud: {baudrate}, TX: {hex(tx_id)}, Ext: {is_extended}, Pad: {hex(padding_byte)} ---")
    try:
        bus = can.interface.Bus(interface='slcan', channel='/dev/cu.usbmodem209B368539451', bitrate=baudrate)
        
        # Clear out any old messages (limit to 100 messages to prevent infinite loop)
        for _ in range(100):
            if not bus.recv(0.01):
                break

        # OBD2 Service 01 PID 00 (Discover PIDs)
        data = [0x02, 0x01, 0x00]
        while len(data) < 8:
            data.append(padding_byte)

        msg = can.Message(arbitration_id=tx_id, data=data, is_extended_id=is_extended)
        print(f"Sending: {msg}")
        bus.send(msg)

        # Listen for any responses for 2 seconds
        timeout = time.time() + 2.0
        responses = 0
        while time.time() < timeout:
            recv_msg = bus.recv(0.1)
            if recv_msg:
                # Filter for likely OBD2 responses
                msg_id = recv_msg.arbitration_id
                if not recv_msg.is_extended_id and 0x7E8 <= msg_id <= 0x7EF:
                    print(f"** OBD2 RESPONSE **: {recv_msg}")
                    responses += 1
                elif recv_msg.is_extended_id and 0x18DAF100 <= msg_id <= 0x18DAF1FF:
                    print(f"** OBD2 RESPONSE **: {recv_msg}")
                    responses += 1
        
        if responses == 0:
            print("No responses received.")
        
        bus.shutdown()
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen-only", action="store_true", help="Just listen to the bus without sending")
    args = parser.parse_args()

    if args.listen_only:
        for baud in [500000, 250000]:
            print(f"\n--- Listening at {baud} baud for 3 seconds ---")
            try:
                bus = can.interface.Bus(interface='slcan', channel='/dev/cu.usbmodem209B368539451', bitrate=baud)
                timeout = time.time() + 3.0
                msgs = 0
                while time.time() < timeout:
                    msg = bus.recv(0.1)
                    if msg:
                        print(f"Received: {msg}")
                        msgs += 1
                        if msgs > 10:
                            print("... (bus is active) ...")
                            break
                if msgs == 0:
                    print("No traffic detected.")
                bus.shutdown()
            except Exception as e:
                print(f"Error: {e}")
        return

    # Test standard 11-bit with 0x00 padding
    test_obd(500000, 0x7DF, False, 0x00)
    # Test standard 11-bit with 0xAA padding
    test_obd(500000, 0x7DF, False, 0xAA)
    
    # Test 29-bit with 0x00 padding
    test_obd(500000, 0x18DB33F1, True, 0x00)
    
    # Test standard 11-bit at 250k
    test_obd(250000, 0x7DF, False, 0x00)
    # Test 29-bit at 250k
    test_obd(250000, 0x18DB33F1, True, 0x00)

if __name__ == "__main__":
    main()
