import os
import numpy as np
import matplotlib.pyplot as plt

def read_adc_data(file_path):
    # Đọc file .bin với định dạng 16-bit unsigned integer, little-endian
    data = np.fromfile(file_path, dtype=np.uint16)
    return data

def plot_time_domain(data, sample_rate=000, title=""):
    # Chỉ lấy đúng 1 giây đầu (1000 mẫu nếu sample_rate = 1000 Hz)
    time_line = 4
    data = data[:sample_rate*time_line]

    # Tạo trục thời gian trong 1 giây
    time = np.arange(len(data)) / sample_rate
    
    plt.figure(figsize=(10, 6))
    plt.plot(time, data)
    plt.title(f'ADC Data - Time Domain\n{title}')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    folder_path = "./20251127/014104"

    sample_rate = 1000  # Hz

    # Lọc file có tên bắt đầu bằng "current_" và kết thúc bằng ".bin"
    bin_files = [
        f for f in os.listdir(folder_path)
        if f.lower().startswith("current_") and f.lower().endswith(".bin")
    ]
    bin_files.sort()  # Sắp xếp tên file theo thứ tự

    for file_name in bin_files:
        file_path = os.path.join(folder_path, file_name)
        print(f"Đang xử lý file: {file_path}")
        
        adc_data = read_adc_data(file_path)
        plot_time_domain(adc_data, sample_rate, title=file_name)
