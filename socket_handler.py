import socket
import threading
import json
import queue
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QGridLayout
from PyQt5.QtCore import Qt
import time
import global_var


# =========================================================
# 🧭 BẢNG ÁNH XẠ LỆNH → HÀM XỬ LÝ
# =========================================================
def handle_ntc_temp_update(params):
    NTC0 = params.get("NTC0")
    NTC1 = params.get("NTC1")
    NTC2 = params.get("NTC2")
    NTC3 = params.get("NTC3")
    NTC4 = params.get("NTC4")
    NTC5 = params.get("NTC5")
    NTC6 = params.get("NTC6")
    NTC7 = params.get("NTC7")

    # Cập nhật giá trị nhiệt độ vào global_var
    global_var.ntc_temp = {
        "NTC0": NTC0,
        "NTC1": NTC1,
        "NTC2": NTC2,
        "NTC3": NTC3,
        "NTC4": NTC4,
        "NTC5": NTC5,
        "NTC6": NTC6,
        "NTC7": NTC7
    }

    # print(f"ntc_temp_update: "
    #       f"NTC0={NTC0}, NTC1={NTC1}, "
    #       f"NTC4={NTC4}, NTC5={NTC5}, "
    #       f"NTC2={NTC2}, NTC3={NTC3}, "
    #       f"NTC6={NTC6}, NTC7={NTC7}")

COMMAND_TABLE = {
    "ntc_temp_update": handle_ntc_temp_update,
}

# =========================================================
# 🧭 TCP SERVER CLASS (Threaded + Handshake mỗi 1s)
# =========================================================
class TCPServer:
    def __init__(self, host="0.0.0.0", port=5000, out_queue=None):
        self.host = host
        self.port = int(port)
        self.out_queue = out_queue or queue.Queue()
        self._stop_event = threading.Event()
        self._thread = None
        self._server_sock = None
        self.clients = []  # list of (client_sock, addr)
        self.handshake_done = {}  # client_sock -> True/False

    # -----------------------------------------------------
    # 🚀 Start server
    # -----------------------------------------------------
    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print(f"[✅ Server started on {self.host}:{self.port}]")

    # -----------------------------------------------------
    # 🛑 Stop server
    # -----------------------------------------------------
    def stop(self):
        self._stop_event.set()
        for client_sock, _ in self.clients:
            try:
                client_sock.sendall(b"reject\n")
                client_sock.close()
            except:
                pass
        self.clients.clear()
        self.handshake_done.clear()
        if self._server_sock:
            try:
                self._server_sock.close()
            except:
                pass
        print("[🛑 Server stopped]")

    # -----------------------------------------------------
    # 🧩 Main server loop
    # -----------------------------------------------------
    def _run(self):
        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_sock.bind((self.host, self.port))
        self._server_sock.listen(5)

        while not self._stop_event.is_set():
            try:
                self._server_sock.settimeout(1.0)
                client_sock, addr = self._server_sock.accept()
                print(f"[✅ Client connected: {addr}]")
                self.clients.append((client_sock, addr))
                self.handshake_done[client_sock] = False

                # Start handshake thread
                threading.Thread(target=self._handshake_loop, args=(client_sock, addr), daemon=True).start()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[⚠️ Accept error]: {e}")

    # -----------------------------------------------------
    # 🔄 Handshake loop: gửi server_hello_client mỗi 1s
    # -----------------------------------------------------
    def _handshake_loop(self, client_sock, addr):
        client_sock.settimeout(1.0)
        try:
            while not self.handshake_done[client_sock] and not self._stop_event.is_set():
                try:
                    client_sock.sendall(b"server_hello_client\n")
                    print(f"[🤝 Gửi handshake tới {addr}]")
                    if self.out_queue:
                        self.out_queue.put_nowait({"__meta__": f"handshake_sent_{addr}"})
                except Exception as e:
                    print(f"[⚠️ Gửi handshake lỗi {addr}]: {e}")
                    break

                # Đợi phản hồi 1s
                try:
                    data = client_sock.recv(1024)
                    if b"client_hello_server" in data:
                        self.handshake_done[client_sock] = True
                        print(f"[🤝 Handshake OK với {addr}]")
                        if self.out_queue:
                            self.out_queue.put_nowait({"__meta__": f"client_connected_{addr}"})
                            
                            # Sang them biến trạng thái để mở khóa chức năng
                            global_var.tcp_connect_changed = True
                            global_var.tcp_connected = True

                        # Start main client loop
                        threading.Thread(target=self._handle_client, args=(client_sock, addr), daemon=True).start()
                        return
                except socket.timeout:
                    pass
                except Exception as e:
                    print(f"[⚠️ Nhận dữ liệu handshake lỗi {addr}]: {e}")
                    break

                time.sleep(1)

            if not self.handshake_done.get(client_sock, False):
                print(f"[❌ Handshake thất bại với {addr}]")
                client_sock.close()
                self.clients = [(c, a) for c, a in self.clients if c != client_sock]
        except Exception as e:
            print(f"[⚠️ Lỗi handshake loop {addr}]: {e}")

    # -----------------------------------------------------
    # 📝 Main client loop (nhận dữ liệu JSON, chỉ in ra)
    # -----------------------------------------------------
    def _handle_client(self, client_sock, addr):
        print(f"[✅ Client {addr} ready to send/receive]")
        try:
            client_sock.settimeout(None)
            f = client_sock.makefile("r")
            for line in f:
                line = line.strip()
                if not line:
                    continue

                if line == "client_hello_server":
                    print(f"[📩 Nhận handshake từ client {addr}]: {line}")
                    continue

                else:
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
                # try:
                #     msg = json.loads(line)
                #     self.out_queue.put_nowait(msg)
                #     print(f"[📩 Nhận từ client {addr}]: {msg}")
                # except json.JSONDecodeError:
                #     print(f"[⚠️ Dữ liệu lỗi từ {addr}]: {line}")

        except Exception as e:
            print(f"[⚠️ Client {addr} lỗi]: {e}")
        finally:
            print(f"[-] Client disconnected: {addr}")
            client_sock.close()
            self.clients = [(c, a) for c, a in self.clients if c != client_sock]
            self.handshake_done.pop(client_sock, None)
    
    # Gửi xuống client
    def send_command(self, cmd, **params):
        """
        Gửi lệnh tới tất cả client đã kết nối dưới dạng JSON.
        cmd: tên lệnh (string)
        params: dict các tham số
        """
        msg = {"cmd": cmd, "params": params}
        msg_str = json.dumps(msg) + "\n"  # nhớ xuống dòng để client đọc line-by-line
        for client_sock, addr in self.clients:
            try:
                client_sock.sendall(msg_str.encode("utf-8"))
                print(f"[📤 Gửi tới {addr}]: {msg}")
            except Exception as e:
                print(f"[⚠️ Gửi tới {addr} lỗi]: {e}")


# =========================================================
# 🧭 GUI PHẦN: GroupBox TCP Server
# =========================================================
def create_socket_group_box(parent):
    conn_group = QGroupBox("🔌 TCP Server")
    conn_layout = QGridLayout()
    conn_layout.setColumnStretch(0, 1)
    conn_layout.setColumnStretch(1, 3)

    # --- Host & Port ---
    parent.host_input = QLineEdit(parent.tcp_host)
    parent.port_input = QLineEdit(str(parent.tcp_port))
    parent.host_input.setPlaceholderText("VD: 192.168.0.0")
    parent.port_input.setPlaceholderText("VD: 5000")

    conn_layout.addWidget(QLabel("Host IP:"), 0, 0, Qt.AlignRight)
    conn_layout.addWidget(parent.host_input, 0, 1)
    conn_layout.addWidget(QLabel("Port:"), 1, 0, Qt.AlignRight)
    conn_layout.addWidget(parent.port_input, 1, 1)

    # --- Start/Stop button ---
    parent.connect_btn = QPushButton("Start Server")
    parent.connect_btn.setFixedHeight(30)
    parent.connect_btn.clicked.connect(lambda: start_server_event(parent))
    conn_layout.addWidget(parent.connect_btn, 2, 0, 1, 2, Qt.AlignCenter)

    # --- Status label ---
    parent.conn_status = QLabel("⏳ Chưa khởi động.")
    parent.conn_status.setAlignment(Qt.AlignCenter)
    conn_layout.addWidget(parent.conn_status, 3, 0, 1, 2)

    conn_group.setLayout(conn_layout)
    return conn_group


def start_server_event(parent):
    if hasattr(parent, "tcp_server") and parent.tcp_server:
        return

    host = parent.host_input.text().strip() or "0.0.0.0"
    try:
        port = int(parent.port_input.text().strip())
    except ValueError:
        QMessageBox.warning(parent, "Lỗi", "Port phải là số.")
        return

    try:
        parent.tcp_server = TCPServer(host, port, parent.data_queue)
        parent.tcp_server.start()
    except OSError as e:
        QMessageBox.critical(parent, "Lỗi", f"Không thể khởi động server:\n{e}")
        return

    parent.conn_status.setText(f"Đang lắng nghe {host}:{port}")
    parent.connect_btn.setText("Stop Server")

    try:
        parent.connect_btn.clicked.disconnect()
    except:
        pass
    parent.connect_btn.clicked.connect(lambda: stop_server_event(parent))


def stop_server_event(parent):
    if not hasattr(parent, "tcp_server"):
        return

    # Sang thêm
    global_var.tcp_connect_changed = True
    global_var.tcp_connected = False
    
    parent.tcp_server.stop()

    while not parent.data_queue.empty():
        try:
            parent.data_queue.get_nowait()
        except:
            break

    del parent.tcp_server
    parent.tcp_server = None

    parent.state["tcp_connected"] = False
    parent.state["temp_control_running"] = False
    if hasattr(parent, "start_temp_ctrl_btn"):
        parent.start_temp_ctrl_btn.setEnabled(False)

    parent.conn_status.setText("Server đã dừng.")
    parent.connect_btn.setText("Start Server")
    parent.log_box.append("[Server stopped]")

    try:
        parent.connect_btn.clicked.disconnect()
    except:
        pass
    parent.connect_btn.clicked.connect(lambda: start_server_event(parent))