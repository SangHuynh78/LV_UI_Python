# =========================================================
# 📡 TCP Client — Print only + handshake + periodic update
# Huỳnh Thanh Sang, 2025
# =========================================================
import socket
import time
import json
import threading
import random

HOST = "127.0.0.1"
PORT = 5000


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
def handle_auto_temp_start(params):
    tec_voltage = params.get("tec_vol")
    temp_target = params.get("temp_target")
    temp_lim_min = params.get("temp_lim_min")
    temp_lim_max = params.get("temp_lim_max")
    ntc_ref_pri = params.get("ntc_ref_pri")
    ntc_ref_sec = params.get("ntc_ref_sec")

    print(f"[⚙️] auto_temp_start: "
          f"(tec_voltage={tec_voltage}, temp_target={temp_target}, "
          f"temp_lim_min={temp_lim_min}, temp_lim_max={temp_lim_max}, "
          f"ntc_ref_pri={ntc_ref_pri}, ntc_ref_sec={ntc_ref_sec})")

def handle_auto_temp_stop(params):
    print(f"[⚙️] auto_temp_stop")

def handle_temp_override_start(params):
    tec_override_voltage = params.get("tec_override_vol")
    tec_override_interval = params.get("tec_override_interval")
    print(f"temp_override_start: "
          f"tec_override_voltage={tec_override_voltage} "
          f"tec_override_interval={tec_override_interval} ")
    
def handle_temp_override_stop(params):
    print(f"temp_override_stop")
    
def handle_laser_manual_set_percent(params):
    laser_percent = params.get("laser_percent")
    print(f"laser_manual_set_percent: percent={laser_percent}")

def handle_laser_manual_turn_on(params):
    laser_position = params.get("laser_pos")
    print(f"laser_manual_turn_on: pos={laser_position}")

def handle_laser_manual_turn_off(params):
    laser_position = params.get("laser_pos")
    print(f"laser_manual_turn_off: pos={laser_position}")

def handle_laser_manual_turn_off_all(params):
    print("laser_manual_turn_off_all")

COMMAND_TABLE = {
    "auto_temp_start": handle_auto_temp_start,
    "auto_temp_stop": handle_auto_temp_stop,
    "temp_override_start": handle_temp_override_start,
    "temp_override_stop": handle_temp_override_stop,
    "laser_manual_set_percent": handle_laser_manual_set_percent,
    "laser_manual_turn_on": handle_laser_manual_turn_on,
    "laser_manual_turn_off": handle_laser_manual_turn_off,
    "laser_manual_turn_off_all": handle_laser_manual_turn_off_all,
}


# =========================================================
# 📤 GỬI DỮ LIỆU NTC MỖI 1 GIÂY
# =========================================================
def ntc_update_thread(sock):
    while True:
        try:
            # Giả lập dữ liệu NTC0...NTC7
            params = {f"NTC{i}": round(20.0 + i * 10 + random.uniform(-2.0, 2.0), 2) for i in range(8)}
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

        # Khởi chạy thread gửi NTC update
        sender_thread = threading.Thread(target=ntc_update_thread, args=(sock,), daemon=True)
        sender_thread.start()

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
    main()