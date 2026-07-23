import can
import time
import os
import threading

class GuidedLogger:
    def __init__(self, interface, port, baud, output_file):
        self.interface = interface
        self.port = port
        self.baud = baud
        self.output_file = output_file
        
        os.makedirs(os.path.dirname(os.path.abspath(self.output_file)), exist_ok=True)
        # Using ASCWriter explicitly to ensure log_event is available
        self.logger = can.ASCWriter(self.output_file)
        self.bus = None
        self._stop_event = threading.Event()
        self._receive_thread = None
        self.start_time = None

    def start(self):
        print(f"Connecting to {self.interface} at {self.port} ({self.baud} baud)...")
        try:
            self.bus = can.interface.Bus(interface=self.interface, channel=self.port, bitrate=self.baud)
        except Exception as e:
            print(f"Failed to connect: {e}")
            raise e
        print(f"Logging to {self.output_file}...")
        
        self.start_time = time.time()
        self._receive_thread = threading.Thread(target=self._receive_loop)
        self._receive_thread.start()

    def _receive_loop(self):
        while not self._stop_event.is_set():
            msg = self.bus.recv(timeout=0.5)
            if msg is not None:
                self.logger.on_message_received(msg)

    def log_action(self, action_description):
        if self.start_time is None:
            return
        # In ASCWriter, log_event expects text
        self.logger.log_event(f"ACTION: {action_description}", timestamp=time.time())
        print(f"\n---> RECORDED EVENT: {action_description}\n")

    def prompt(self, instruction):
        input(f"\n[INSTRUCTION] {instruction} (Press Enter to continue)")

    def prompt_and_log(self, instruction, event_text):
        self.prompt(instruction)
        self.log_action(event_text)

    def stop(self):
        print("Stopping logger...")
        self._stop_event.set()
        if self._receive_thread:
            self._receive_thread.join()
        
        self.logger.stop()
        if self.bus:
            self.bus.shutdown()
        print("Logger stopped.")
