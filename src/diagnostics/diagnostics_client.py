import can
import isotp
from udsoncan.connections import PythonIsoTpConnection
from udsoncan.client import Client
from udsoncan.exceptions import NegativeResponseException
import udsoncan
import time

class DiagnosticsClient:
    def __init__(self, interface='slcan', port='/dev/cu.usbmodem209B368539451', baud=500000, tx_id=0x7DF, rx_id=0x7E8):
        self.interface = interface
        self.port = port
        self.baud = baud
        self.tx_id = int(str(tx_id), 0)
        self.rx_id = int(str(rx_id), 0)
        self.bus = None
        self.tplayer = None
        self.conn = None

    def connect(self):
        print(f"Connecting to {self.interface} at {self.port} ({self.baud} baud)...")
        self.bus = can.interface.Bus(interface=self.interface, channel=self.port, bitrate=self.baud)
        
        if self.tx_id > 0x7FF or self.rx_id > 0x7FF:
            address_mode = isotp.AddressingMode.Normal_29bits
        else:
            address_mode = isotp.AddressingMode.Normal_11bits
            
        addr = isotp.Address(address_mode, rxid=self.rx_id, txid=self.tx_id)
        self.tplayer = isotp.CanStack(bus=self.bus, address=addr, error_handler=self._isotp_error_handler, params={'tx_padding': 0x00})
        
        self.conn = PythonIsoTpConnection(self.tplayer)
        self.conn.open()

    def _isotp_error_handler(self, error):
        pass

    def disconnect(self):
        if self.conn:
            self.conn.close()
        if self.tplayer:
            self.tplayer.stop()
        if self.bus:
            self.bus.shutdown()
            
    def decode_obd2_dtc(self, high_byte, low_byte):
        system = (high_byte >> 6) & 0x03
        sys_char = ['P', 'C', 'B', 'U'][system]
        digit1 = (high_byte >> 4) & 0x03
        digit2 = high_byte & 0x0F
        digit3 = (low_byte >> 4) & 0x0F
        digit4 = low_byte & 0x0F
        return f"{sys_char}{digit1}{digit2:X}{digit3:X}{digit4:X}"

    def read_pid(self, pid: int) -> bytes:
        try:
            req = b'\x01' + bytes([pid])
            self.tplayer.send(req)
            timeout = time.time() + 2.0
            while time.time() < timeout:
                if self.tplayer.available():
                    payload = self.tplayer.recv()
                    if payload and len(payload) >= 2 and payload[0] == 0x41 and payload[1] == pid:
                        return payload[2:]
                time.sleep(0.01)
        except Exception as e:
            print(f"Error reading PID {pid:02X}: {e}")
        return None

    def get_supported_pids(self) -> list:
        supported_pids = []
        # Availability PIDs are 0x00, 0x20, 0x40, 0x60, 0x80, 0xA0, 0xC0
        for base_pid in range(0x00, 0xE0, 0x20):
            data = self.read_pid(base_pid)
            if data and len(data) >= 4:
                # 32-bit bitmask
                bitmask = int.from_bytes(data[:4], byteorder='big')
                for i in range(32):
                    if (bitmask >> (31 - i)) & 1:
                        supported_pids.append(base_pid + i + 1)
                # If the bitmask for the NEXT availability PID is 0, we can stop
                if not (bitmask & 1):
                    break
            else:
                break
        return supported_pids

    def read_dtcs(self, status_mask=0xFF):
        dtcs = []
        try:
            print("Attempting UDS Service 0x19 (ReadDTCInformation)...")
            with Client(self.conn, request_timeout=2) as client:
                response = client.get_dtc_by_status_mask(status_mask)
                for dtc in response.dtcs:
                    dtcs.append(f"{dtc.id:06X} (Status: {dtc.status:02X})")
            print("Successfully read DTCs using UDS.")
            return dtcs
        except NegativeResponseException as e:
            print(f"UDS Request Rejected by ECU: {e}")
        except Exception as e:
            print(f"UDS Request failed: {e}")

        print("Falling back to ISO 15031 (Standard OBD2 Mode 03)...")
        try:
            self.tplayer.send(b'\x03')
            timeout = time.time() + 2.0
            payload = None
            while time.time() < timeout:
                if self.tplayer.available():
                    payload = self.tplayer.recv()
                    break
                time.sleep(0.01)
                
            if payload:
                if len(payload) >= 2 and payload[0] == 0x43:
                    num_dtcs = payload[1]
                    print(f"ISO 15031 Response indicates {num_dtcs} DTC(s).")
                    
                    idx = 2
                    for i in range(num_dtcs):
                        if idx + 1 < len(payload):
                            dtc_str = self.decode_obd2_dtc(payload[idx], payload[idx+1])
                            dtcs.append(dtc_str)
                            idx += 2
                        else:
                            break
                    print("Successfully read DTCs using ISO 15031 fallback.")
                    return dtcs
                else:
                    print(f"Invalid or negative OBD2 response: {payload.hex()}")
            else:
                print("No response received for Mode 03 fallback.")
        except Exception as e:
            print(f"ISO 15031 Fallback failed: {e}")
            
        return dtcs

    def clear_dtcs(self):
        try:
            print("Attempting UDS Service 0x14 (ClearDiagnosticInformation)...")
            with Client(self.conn, request_timeout=2) as client:
                client.clear_dtc(0xFFFFFF)
            print("Successfully cleared DTCs using UDS.")
            return True
        except NegativeResponseException as e:
            print(f"UDS Request Rejected by ECU: {e}")
        except Exception as e:
            print(f"UDS Request failed: {e}")

        print("Falling back to ISO 15031 (Standard OBD2 Mode 04)...")
        try:
            self.tplayer.send(b'\x04')
            timeout = time.time() + 2.0
            payload = None
            while time.time() < timeout:
                if self.tplayer.available():
                    payload = self.tplayer.recv()
                    break
                time.sleep(0.01)
                
            if payload:
                if payload[0] == 0x44:
                    print("Successfully cleared DTCs using ISO 15031 fallback.")
                    return True
                else:
                    print(f"Invalid or negative OBD2 response: {payload.hex()}")
            else:
                print("No response received for Mode 04 fallback.")
        except Exception as e:
            print(f"ISO 15031 Fallback failed: {e}")
            
        return False
