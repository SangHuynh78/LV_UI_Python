import os
import numpy as np
import matplotlib.pyplot as plt

def read_adc_data(file_path):
    # Đọc file .bin với định dạng 16-bit unsigned integer, little-endian
    data = np.fromfile(file_path, dtype=np.uint16)
    return data

def plot_time_domain(data, sample_rate=1000, title=""):
    # Tạo trục thời gian dựa trên tần số lấy mẫu
    time = np.arange(len(data)) / sample_rate
    
    plt.figure(figsize=(10, 6))
    plt.plot(time, data)
    plt.title(f'ADC Data - Time Domain\n{title}')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    # final fw
    folder_path = "./20251127/014104"

    sample_rate = 500_000  # Hz

    # Lọc file có tên bắt đầu bằng "dls_" và kết thúc bằng ".bin"
    bin_files = [
        f for f in os.listdir(folder_path)
        if f.lower().startswith("dls_") and f.lower().endswith(".bin")
    ]
    # bin_files = os.listdir(folder_path)
    bin_files.sort()  # Sắp xếp tên file theo thứ tự

    for file_name in bin_files:
        file_path = os.path.join(folder_path, file_name)
        print(f"Đang xử lý file: {file_path}")
        adc_data = read_adc_data(file_path)
        plot_time_domain(adc_data, sample_rate, title=file_name)