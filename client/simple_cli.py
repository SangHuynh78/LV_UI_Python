# =========================================================
# 📡 TCP Client — Print only + handshake + timeout-safe
# Huỳnh Thanh Sang, 2025
# =========================================================
import socket
import time

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
# 🚀 MAIN LOOP
# =========================================================
def main():
    while True:
        sock = connect_to_server()
        buffer = ""

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
                            # ✅ Phản hồi handshake
                            print("[📩 Nhận handshake] server_hello_client — gửi client_hello_server")
                            try:
                                sock.sendall(b"client_hello_server\n")
                            except Exception as e:
                                print(f"[⚠️ Lỗi khi gửi handshake]: {e}")
                        elif line == "reject":
                            print("[⚠️ Server yêu cầu ngắt kết nối]")
                            raise ConnectionError("Server rejected")
                        else:
                            # Chỉ in ra dữ liệu nhận được
                            print(f"[📩 Nhận từ server]: {line}")

                except socket.timeout:
                    # 🔹 Timeout recv() bình thường, tiếp tục chờ dữ liệu
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
