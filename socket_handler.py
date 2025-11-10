# socket_handler.py

import socket
import threading
import json
import queue
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

# -----------------------------
# TCP Server class (threaded)
# -----------------------------
class TCPServer:
    def __init__(self, host="0.0.0.0", port=5000, out_queue=None):
        self.host = host
        self.port = int(port)
        self.out_queue = out_queue or queue.Queue()
        self._stop_event = threading.Event()
        self._thread = None
        self._server_sock = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        try:
            if self._server_sock:
                self._server_sock.close()
        except Exception:
            pass

    def _run(self):
        try:
            self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_sock.bind((self.host, self.port))
            self._server_sock.listen(5)

            self._log(f"[🖥️] Server started on {self.host}:{self.port}")

            while not self._stop_event.is_set():
                self._server_sock.settimeout(1)
                try:
                    client_sock, addr = self._server_sock.accept()
                except socket.timeout:
                    continue
                threading.Thread(
                    target=self._handle_client, args=(client_sock, addr), daemon=True
                ).start()

        except Exception as e:
            self._log(f"[❌] Server error: {e}")

    def _handle_client(self, client_sock, addr):
        try:
            self._log(f"[+] Client connected: {addr}")
            f = client_sock.makefile("r")

            for line in f:
                if not line.strip():
                    continue
                try:
                    msg = json.loads(line.strip())
                    self.out_queue.put_nowait(msg)
                except json.JSONDecodeError:
                    continue

        except Exception as e:
            self._log(f"[⚠️] Client {addr} error: {e}")
        finally:
            client_sock.close()
            self._log(f"[-] Client disconnected: {addr}")

    def _log(self, msg):
        if self.out_queue:
            try:
                self.out_queue.put_nowait({"__meta__": msg})
            except Exception:
                pass


# -----------------------------
# GUI: group box cho server
# -----------------------------
def create_socket_group_box(parent):
    conn_group = QGroupBox("🔌 TCP Server")
    v = QVBoxLayout()

    parent.host_input = QLineEdit(parent.tcp_host)
    parent.port_input = QLineEdit(str(parent.tcp_port))

    v.addWidget(QLabel("Host IP:"))
    v.addWidget(parent.host_input)
    v.addWidget(QLabel("Port:"))
    v.addWidget(parent.port_input)

    parent.connect_btn = QPushButton("Start Server")
    parent.connect_btn.clicked.connect(lambda: start_server(parent))
    v.addWidget(parent.connect_btn)

    parent.conn_status = QLabel("⏳ Chưa khởi động.")
    v.addWidget(parent.conn_status)

    conn_group.setLayout(v)
    return conn_group


def start_server(parent):
    host = parent.host_input.text().strip()
    try:
        port = int(parent.port_input.text().strip())
    except ValueError:
        QMessageBox.warning(parent, "Invalid Port", "Please enter a valid port number.")
        return

    parent.tcp_server = TCPServer(host, port, parent.data_queue)
    parent.tcp_server.start()

    parent.conn_status.setText(f"🖥️ Server đang lắng nghe {host}:{port}")
    parent.connect_btn.setText("Stop Server")

    try:
        parent.connect_btn.clicked.disconnect()
    except Exception:
        pass
    parent.connect_btn.clicked.connect(lambda: stop_server(parent))


def stop_server(parent):
    try:
        parent.tcp_server.stop()
        del parent.tcp_server
    except Exception:
        pass

    parent.conn_status.setText("⏳ Server đã dừng.")
    parent.connect_btn.setText("Start Server")

    try:
        parent.connect_btn.clicked.disconnect()
    except Exception:
        pass
    parent.connect_btn.clicked.connect(lambda: start_server(parent))