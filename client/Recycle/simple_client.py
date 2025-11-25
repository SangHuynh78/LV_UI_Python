# =========================================================
# 📡 TCP Client — Print only + handshake + periodic update
# Huỳnh Thanh Sang, 2025
# =========================================================
import socket
import time
import json
import threading
from pathlib import Path
from datetime import datetime
from serial_driver import SerialAPI
from spi_driver import SPIAPI

BASE_DATA_DIR = Path.home() / "SangHuynh_Dev/Data/Raw"
BASE_DATA_DIR.mkdir(parents=True, exist_ok=True)  # Tạo thư mục Data nếu chưa tồn tại

CONFIG_DIR = Path.home() / ".app_src/02_ConfigSystem"
CAMERA_SWITCH_SCRIPT = Path.home() / ".app_src/03_Source/camera"

LOG_FILE = Path(__file__).parent / "handler.log"

# Global variable to track current timepoint folder
current_timepoint_folder = None

def get_daily_folder():
    today = datetime.now().strftime("%Y%m%d")
    daily_folder = BASE_DATA_DIR / today
    daily_folder.mkdir(parents=True, exist_ok=True)
    return daily_folder

def get_timepoint_folder():
    """Get current timepoint folder, create temp folder if none exists"""
    global current_timepoint_folder
    
    if current_timepoint_folder is None:
        # Create default temp folder if no timepoint has been set
        daily_folder = get_daily_folder()
        temp_folder = daily_folder / "temp"
        temp_folder.mkdir(parents=True, exist_ok=True)
        return temp_folder
    
    return current_timepoint_folder

def save_data_file(filename, content, append=False, use_timepoint=True):
    """Save data file to appropriate location"""
    if use_timepoint:
        # Save to timepoint folder for experiment data
        folder = get_timepoint_folder()
    else:
        # Save to daily folder for logs
        folder = get_daily_folder()
    
    filepath = folder / filename
    mode = "ab" if append else "wb"
    with open(filepath, mode) as f:
        f.write(content)
    # if append == False:
    #     logger.info(f"[+] Saved to {filepath}")
    print(f"[+] Saved to {filepath} ({'append' if append else 'write'})")

# =========================================================
# 🧩 GLOBAL DEFINES
# =========================================================
# HOST = "127.0.0.1"
HOST = "192.168.137.1"
PORT = 5000

# =========================================================
# 🧩 GLOBAL VARIABLE
# =========================================================
ntc_temp = [0] * 8

# =========================================================
# 🧩 HANDLERS
# =========================================================

def handle_ntc_temp(params):
    """
    params = list các giá trị đọc được từ NTC
    ví dụ: [20,20,20,20,20,20,20,21]
    """
    global ntc_temp
    values = list(map(float, params))
    ntc_temp = values

def handle_data_chunk(params):
    try:
        print("[CMD] CHUNK")

        # Convert all params to integers
        params = [int(x) for x in params]

        if len(params) != 13:
            print("[!] Invalid CHUNK payload")
            return
        
        # Parse fields
        chunk_id = (params[0] << 8) | params[1]

        crc_received = (
            (params[2] << 24) |
            (params[3] << 16) |
            (params[4] << 8)  |
            params[5]
        )

        year   = params[6]
        month  = params[7]
        day    = params[8]
        hour   = params[9]
        minute = params[10]
        second = params[11]
        index  = params[12]

        # Receive SPI data
        data = spi.read_spi_block()
        print(f"data: {data[0]}, {data[1]}, {data[2]}, {data[3]}, {data[4]}")
        # crc = calculate_crc32(data)

        print(f"Chunk ID: {chunk_id}")
        print(f"Timestamp: 20{year:02d}-{month:02d}-{day:02d} "
              f"{hour:02d}:{minute:02d}:{second:02d}")

        # Save data chunk into file
        filename = f"dls_i{index:02d}_20{year:02d}{month:02d}{day:02d}_{hour:02d}{minute:02d}{second:02d}.bin"
        save_data_file(filename, data, append=True, use_timepoint=True)

        print(f"[v] Finish chunk: {chunk_id}")

    except Exception as e:
        print(f"[!] Exception in CHUNK handler: {e}")

    return

def handle_current_chunk(params):
    return
def handle_log_chunk(params):
    return

UART_DISPATCH_TABLE = {
    "ntc_temp": handle_ntc_temp,
    "data_chunk": handle_data_chunk,
    "current_chunk": handle_current_chunk,
    "log_chunk": handle_log_chunk,
}

# =========================================================
# 📥 UART RX callback
# =========================================================
def on_uart_rx(line):
    print(f"[📥 UART RX]: {line}")

    tokens = line.strip().split()
    if len(tokens) == 0:
        return

    cmd = tokens[0]
    params = tokens[1:]

    handler = UART_DISPATCH_TABLE.get(cmd)

    if handler:
        handler(params)

# =========================================================
# ⚙️ KẾT NỐI TỚI SERVER (tự thử lại mỗi 2s)
# =========================================================
def connect_to_server():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(5.0)  # timeout 5s cho recv()
            sock.connect((HOST, PORT))
            print(f"[✅ Đã kết nối tới {HOST}:{PORT}]")
            return sock
        except Exception as e:
            print(f"[❌ Kết nối thất bại]: {e} — thử lại sau 2s...")
            time.sleep(2)


# =========================================================
# 🧭 BẢNG ÁNH XẠ LỆNH → HÀM XỬ LÝ
# =========================================================
def handle_temp_auto_start(params):
    tec_voltage = params.get("tec_vol")
    temp_target = params.get("temp_target")
    temp_lim_min = params.get("temp_lim_min")
    temp_lim_max = params.get("temp_lim_max")
    ntc_ref_pri = params.get("ntc_ref_pri")
    ntc_ref_sec = params.get("ntc_ref_sec")

    print(f"temp_auto_start: "
          f"(tec_voltage={tec_voltage}, temp_target={temp_target}, "
          f"temp_lim_min={temp_lim_min}, temp_lim_max={temp_lim_max}, "
          f"ntc_ref_pri={ntc_ref_pri}, ntc_ref_sec={ntc_ref_sec})")
    
    # -------------------------------
    # Gửi xuống UART dạng chuỗi kí tự
    # -------------------------------
    cmd = f"temp_auto_start {tec_voltage} {temp_target} {temp_lim_min} {temp_lim_max} {ntc_ref_pri} {ntc_ref_sec}\n"
    uart.send(cmd)

def handle_temp_auto_stop(params):
    print("temp_auto_stop")
    cmd = "temp_auto_stop\n"
    uart.send(cmd)

def handle_temp_override_start(params):
    tec_override_voltage = params.get("tec_override_vol")
    tec_override_interval = params.get("tec_override_interval")
    print(f"temp_override_start: "
          f"{tec_override_voltage} {tec_override_interval}")
    cmd = f"temp_override_start {tec_override_voltage} {tec_override_interval}\n"
    uart.send(cmd)
    
def handle_temp_override_stop(params):
    print("temp_override_stop")
    uart.send("temp_override_stop\n")

def handle_laser_manual_set_percent(params):
    laser_percent = params.get("laser_percent")
    print(f"laser_manual_set_percent: {laser_percent}")
    cmd = f"laser_manual_set_percent {laser_percent}\n"
    uart.send(cmd)

def handle_laser_manual_turn_on(params):
    laser_position = params.get("laser_pos")
    print(f"laser_manual_turn_on: {laser_position}")
    cmd = f"laser_manual_turn_on {laser_position}\n"
    uart.send(cmd)

def handle_laser_manual_turn_off(params):
    laser_position = params.get("laser_pos")
    print(f"laser_manual_turn_off: {laser_position}")
    cmd = f"laser_manual_turn_off {laser_position}\n"
    uart.send(cmd)

def handle_laser_manual_turn_off_all(params):
    print("laser_manual_turn_off_all")
    uart.send("laser_manual_turn_off_all\n")

def handle_exp_start(params):
    exp_sample_rate = params.get("exp_sample_rate")
    exp_first_position = params.get("exp_first_position")
    exp_end_position = params.get("exp_end_position")
    exp_laser_percent = params.get("exp_laser_percent")
    exp_pre_time = params.get("exp_pre_time")
    exp_experiment_time = params.get("exp_experiment_time")
    exp_post_time = params.get("exp_post_time")

    print(f"exp_start: "
          f"(exp_sample_rate={exp_sample_rate}, "
          f"exp_first_position={exp_first_position}, "
          f"exp_end_position={exp_end_position}, "
          f"exp_laser_percent={exp_laser_percent}, "
          f"exp_pre_time={exp_pre_time}, "
          f"exp_experiment_time={exp_experiment_time}, "
          f"exp_post_time={exp_post_time})")
    
    cmd = f"exp_start {exp_sample_rate} {exp_first_position} {exp_end_position} {exp_laser_percent} {exp_pre_time} {exp_experiment_time} {exp_post_time}\n"
    uart.send(cmd)

COMMAND_TABLE = {
    "temp_auto_start": handle_temp_auto_start,
    "temp_auto_stop": handle_temp_auto_stop,
    "temp_override_start": handle_temp_override_start,
    "temp_override_stop": handle_temp_override_stop,
    "laser_manual_set_percent": handle_laser_manual_set_percent,
    "laser_manual_turn_on": handle_laser_manual_turn_on,
    "laser_manual_turn_off": handle_laser_manual_turn_off,
    "laser_manual_turn_off_all": handle_laser_manual_turn_off_all,
    "exp_start": handle_exp_start,
}


# =========================================================
# 📤 GỬI DỮ LIỆU NTC MỖI 1 GIÂY
# =========================================================
def ntc_update_thread(sock):
    while True:
        try:
            # Giả lập dữ liệu NTC0...NTC7
            params = {f"NTC{i}": ntc_temp[i] for i in range(8)}
            msg = {
                "cmd": "ntc_temp_update",
                "params": params
            }
            data = (json.dumps(msg) + "\n").encode('utf-8')
            sock.sendall(data)
            # print(f"[📤 Gửi]: {msg}")  # bật nếu muốn debug
        except Exception as e:
            print(f"[⚠️ Lỗi gửi NTC update]: {e}")
            break
        time.sleep(1)  # gửi mỗi 1 giây


# =========================================================
# 🚀 MAIN LOOP
# =========================================================
def main():
    while True:
        sock = connect_to_server()
        buffer = ""

        # Khởi chạy thread gửi tcp (NTC update)
        tcp_sender_thread = threading.Thread(target=ntc_update_thread, args=(sock,), daemon=True)
        tcp_sender_thread.start()

        try:
            while True:
                try:
                    data = sock.recv(1024)
                    if not data:
                        raise ConnectionError("Server đóng kết nối")

                    buffer += data.decode('utf-8', errors='ignore')

                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if not line:
                            continue

                        if line == "server_hello_client":
                            print("[📩 Nhận handshake] server_hello_client — gửi client_hello_server")
                            try:
                                sock.sendall(b"client_hello_server\n")
                            except Exception as e:
                                print(f"[⚠️ Lỗi khi gửi handshake]: {e}")

                        elif line == "reject":
                            print("[⚠️ Server yêu cầu ngắt kết nối]")
                            raise ConnectionError("Server rejected")

                        else:
                            print(f"[📩 Nhận từ server]: {line}")
                            try:
                                msg = json.loads(line)
                                if isinstance(msg, dict) and "cmd" in msg:
                                    cmd = msg["cmd"]
                                    params = msg.get("params", {})
                                    handler = COMMAND_TABLE.get(cmd)
                                    if handler:
                                        handler(params)
                                    else:
                                        print(f"[Lệnh không xác định]: {cmd}")
                            except json.JSONDecodeError:
                                print(f"[Dữ liệu không hợp lệ]: {line}")

                except socket.timeout:
                    continue

        except (ConnectionError, OSError) as e:
            print(f"[⚠️ Kết nối bị ngắt]: {e}")
        except Exception as e:
            print(f"[⚠️ Lỗi không xác định]: {e}")
        finally:
            try:
                sock.close()
            except:
                pass
            print("[🔁 Thử kết nối lại sau 2s...]")
            time.sleep(2)


# =========================================================
# 🚀 CHẠY CHƯƠNG TRÌNH
# =========================================================
if __name__ == "__main__":
    # UART từ CM4 đến OBC
    uart = SerialAPI("/dev/ttyAMA3", 115200)
    uart.set_rx_callback(on_uart_rx)
    uart.open()
    # SPI từ CM4(master) đến OBC(client)
    spi = SPIAPI()
    spi.open()


    main()