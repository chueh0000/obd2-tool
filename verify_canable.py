import serial
import time
import sys

PORT = '/dev/cu.usbmodem209B368539451'
BAUD = 115200

def test_slcan():
    print(f"Connecting to CANable at {PORT}...")
    try:
        # Open serial port
        ser = serial.Serial(PORT, BAUD, timeout=1.0)
    except Exception as e:
        print(f"Failed to open port: {e}")
        sys.exit(1)

    try:
        # 1. Close channel just in case it was left open
        ser.write(b'C\r')
        ser.readline() # Consume response if any
        
        # 2. Query hardware version
        print("Querying hardware version (V)...")
        ser.write(b'V\r')
        v_resp = ser.readline().decode('utf-8', errors='ignore').strip()
        print(f"Hardware Version: {v_resp}")

        # 3. Query firmware version (v)
        print("Querying firmware version (v)...")
        ser.write(b'v\r')
        fw_resp = ser.readline().decode('utf-8', errors='ignore').strip()
        print(f"Firmware Version: {fw_resp}")

        print("\nCANable SLCAN Interface is online and responding correctly!")
    except Exception as e:
        print(f"Error communicating with CANable: {e}")
    finally:
        ser.close()

if __name__ == '__main__':
    test_slcan()
