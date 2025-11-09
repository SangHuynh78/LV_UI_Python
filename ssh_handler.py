import paramiko
import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QTextEdit, QRadioButton, QMessageBox
)
from PyQt5.QtCore import QTimer

import global_var

DEFAULT_HOST = "192.168.1.11"
DEFAULT_USER = "spec_cam"
DEFAULT_PASS = "cam"
DEFAULT_SCRIPT = "/home/spec_cam/SangHuynh_Dev/sang_temp.py"


# ---------------- SSH Handler ----------------
class SSHHandler:
    def __init__(self, log_callback):
        self.ssh = None
        self.stdout = None
        self.log = log_callback
        self.latest_temp = None

    def connect(self, host, user, password, script):
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(host, username=user, password=password, timeout=5)
            self.log(f"[+] Đã kết nối tới {host}")

            self.stdin, self.stdout, _ = self.ssh.exec_command(f"python3 {script}", get_pty=True)
            threading.Thread(target=self.read_remote_output, daemon=True).start()

        except Exception as e:
            self.log(f"[!] Lỗi SSH: {e}")

    def read_remote_output(self):
        for line in iter(self.stdout.readline, ""):
            try:
                temp = float(line.strip())
                self.latest_temp = temp
                self.log(f"NTC1: {temp:.2f} °C")
            except ValueError:
                continue

    def update_temps(self, x_data, ntc_temp, curves, labels):
        if self.latest_temp is None:
            return
        idx = len(x_data) + 1
        x_data.append(idx)
        for i in range(8):
            ntc_temp[i].append(self.latest_temp if i == 0 else 0)
            ntc_temp[i] = ntc_temp[i][-120:]
            curves[i].setData(x_data[-120:], ntc_temp[i])
            labels[i].setText(f"NTC{i+1}: {ntc_temp[i][-1]:.2f} °C")

    def disconnect(self):
        if self.ssh:
            self.ssh.close()
            self.log("[!] SSH disconnected.")
            self.ssh = None


# ---------------- UI Group Box ----------------
def create_ssh_group_box(parent):
    conn_ssh_group = QGroupBox("🔌 Kết nối SSH")
    conn_ssh_layout = QVBoxLayout()

    # Input fields
    parent.host_input = QLineEdit(DEFAULT_HOST)
    parent.user_input = QLineEdit(DEFAULT_USER)
    parent.pass_input = QLineEdit(DEFAULT_PASS)
    parent.pass_input.setEchoMode(QLineEdit.Password)

    conn_ssh_layout.addWidget(QLabel("Host IP:"))
    conn_ssh_layout.addWidget(parent.host_input)
    conn_ssh_layout.addWidget(QLabel("Username:"))
    conn_ssh_layout.addWidget(parent.user_input)
    conn_ssh_layout.addWidget(QLabel("Password:"))
    conn_ssh_layout.addWidget(parent.pass_input)

    # Connect button
    parent.connect_btn = QPushButton("Connect SSH")
    parent.connect_btn.clicked.connect(lambda: connect_ssh(parent))
    conn_ssh_layout.addWidget(parent.connect_btn)

    parent.status_label = QLabel("⏳ Chưa kết nối.")
    conn_ssh_layout.addWidget(parent.status_label)

    conn_ssh_group.setLayout(conn_ssh_layout)
    return conn_ssh_group


# ---------------- Logic connect/disconnect ----------------
def connect_ssh(parent):
    host = parent.host_input.text()
    user = parent.user_input.text()
    pw = parent.pass_input.text()

    parent.ssh_handler.connect(host, user, pw, DEFAULT_SCRIPT)
    parent.status_label.setText(f"✅ Đã kết nối tới {host}")
    parent.connect_btn.setText("Disconnect SSH")

    # Đổi nút sang disconnect
    parent.connect_btn.clicked.disconnect()
    parent.connect_btn.clicked.connect(lambda: disconnect_ssh(parent))

    # Bắt đầu timer cập nhật dữ liệu
    parent.timer.start(500)


def disconnect_ssh(parent):
    parent.ssh_handler.disconnect()
    parent.status_label.setText("⏳ Đã ngắt kết nối.")
    parent.connect_btn.setText("Connect SSH")

    # Đổi nút lại sang connect
    parent.connect_btn.clicked.disconnect()
    parent.connect_btn.clicked.connect(lambda: connect_ssh(parent))

    parent.timer.stop()