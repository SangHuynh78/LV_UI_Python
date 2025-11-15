# serial_api.py
import threading
import time
import serial

class SerialAPI:
    def __init__(self, port="/dev/ttyAMA3", baudrate=115200, timeout=0.1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.rx_callback = None
        self.running = False

    def open(self):
        self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        self.running = True
        threading.Thread(target=self._rx_thread, daemon=True).start()

    def close(self):
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()

    def send(self, data: str):
        if self.ser and self.ser.is_open:
            self.ser.write(data.encode())

    def set_rx_callback(self, func):
        self.rx_callback = func

    def _rx_thread(self):
        while self.running:
            if self.ser.in_waiting > 0:
                try:
                    line = self.ser.readline().decode(errors="ignore").strip()
                    if self.rx_callback:
                        self.rx_callback(line)
                except:
                    pass
            time.sleep(0.01)
