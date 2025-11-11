# =========================================================
# 📡 TCP Client — Handshake: server_hello_client ↔ client_hello_server
# Huỳnh Thanh Sang, 2025
# =========================================================
import socket
import time
import json

HOST = "127.0.0.1"
PORT = 5000

# =========================================================
# 🧭 Trạng thái kết nối
# =========================================================
tcp_connected = False      # True khi đã kết nối socket
handshake_done = False     # True sau khi nhận server_hello_client và phản hồi


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

COMMAND_TABLE = {
    "auto_temp_start": handle_auto_temp_start,
    "auto_temp_stop": handle_auto_temp_stop,
}


# =========================================================
# ⚙️ HÀM KẾT NỐI SERVER (thử lại mỗi 2s)
# =========================================================
def connect_to_server():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(5.0)  # Tăng timeout
            sock.connect((HOST, PORT))
            print(f"[Đã kết nối tới {HOST}:{PORT}]")
            return sock
        except Exception as e:
            print(f"[Kết nối thất bại]: {e}, thử lại sau 2s...")
            time.sleep(2)


# =========================================================
# ⚙️ PHÂN TÍCH DỮ LIỆU TỪ SERVER
# =========================================================
def handle_server_data(sock, data):
    global handshake_done

    data = data.strip()
    if not data:
        return

    print(f"[Server gửi]: {data}")

    if data == "reject":
        print("[Server yêu cầu ngắt kết nối]")
        raise ConnectionError("Server sent reject")

    if data == "server_hello_client":
        print("[Handshake] Gửi 'client_hello_server'")
        try:
            sock.sendall(b"client_hello_server\n")
            handshake_done = True
            tcp_connected = True
            print("[✅] Connected to server successfully.")
        except:
            raise ConnectionError("Gửi handshake thất bại")
        return

    try:
        msg = json.loads(data)
        if isinstance(msg, dict) and "cmd" in msg:
            cmd = msg["cmd"]
            params = msg.get("params", {})
            handler = COMMAND_TABLE.get(cmd)
            if handler:
                handler(params)
            else:
                print(f"[Lệnh không xác định]: {cmd}")
    except json.JSONDecodeError:
        print(f"[Dữ liệu không hợp lệ]: {data}")


# =========================================================
# 🚀 MAIN LOOP
# =========================================================
def main():
    global tcp_connected, handshake_done

    while True:
        sock = connect_to_server()
        tcp_connected = True
        handshake_done = False  # Reset mỗi lần reconnect

        try:
            buffer = ""
            while True:
                try:
                    data = sock.recv(1024)
                    if not data:
                        raise ConnectionError("No data")

                    buffer += data.decode('utf-8', errors='ignore')

                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if not line:
                            continue

                        # === CHỈ XỬ LÝ KHI CÓ DỮ LIỆU ===
                        if line == "server_hello_client":
                            sock.sendall(b"client_hello_server\n")
                            handshake_done = True
                            print("[Handshake] Gửi client_hello_server")
                        elif line == "reject":
                            print("[Server ngắt kết nối]")
                            raise ConnectionError("Server rejected")
                        else:
                            handle_server_data(sock, line)

                except socket.timeout:
                    continue

        except (ConnectionError, OSError, ConnectionResetError) as e:
            print(f"[Kết nối bị ngắt]: {e}")
        except Exception as e:
            print(f"[Lỗi]: {e}")
        finally:
            try:
                sock.close()
            except:
                pass
            tcp_connected = False
            handshake_done = False
            print("[Thử kết nối lại sau 2s...]")
            time.sleep(2)


# =========================================================
# 🚀 CHẠY CHƯƠNG TRÌNH
# =========================================================
if __name__ == "__main__":
    main()