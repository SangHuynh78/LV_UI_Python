# spi_driver.py
import spidev
import threading

# SPI
SPI_BLOCK_SIZE = 32768
SPI_SUB_BLOCK_SIZE = 32768
NUM_SPI_BLOCKS = SPI_BLOCK_SIZE // SPI_SUB_BLOCK_SIZE
SPI_SPEED_HZ = 15000000
SPI_BUS = 1
SPI_DEVICE = 0
SPI_MODE = 0b10


class SPIAPI:
    def __init__(self, bus=SPI_BUS, device=SPI_DEVICE, speed=SPI_SPEED_HZ, mode=SPI_MODE, timeout=0.1):
        # Khởi tạo SPI
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = speed
        self.spi.mode = mode
        self.timeout = timeout
        self.running = False

    def open(self):
        self.running = True
        # threading.Thread(target=self._rx_thread, daemon=True).start()

    # Đọc SPI an toàn từng phần SPI_SUB_BLOCK_SIZE byte
    def read_spi_block(self):
        data = bytearray()
        for _ in range(max(1, NUM_SPI_BLOCKS)):
            dummy = [0xAA] * SPI_SUB_BLOCK_SIZE
            chunk = self.spi.xfer2(dummy)
            data.extend(chunk)
        return bytes(data)

    def close(self):
        try:
            self.running = False
            self.spi.close()
        except Exception:
            pass