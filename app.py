import sys
import threading
import paramiko
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QTextCursor, QFont
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox, QTextEdit, QMessageBox
)


class PuttyLikeSSH(QWidget):
    output_received = pyqtSignal(str)  # ✅ Signal để nhận dữ liệu SSH

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PuTTY-like SSH Terminal for CM4")
        self.setGeometry(0, 0, 1920, 1080)
        self.client = None
        self.channel = None
        self.cursor_visible = True

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # === Khung bên trái: SSH ===
        conn_group = QGroupBox("🔌 SSH Connection")
        conn_layout = QVBoxLayout()

        self.host_input = QLineEdit("192.168.1.10")
        self.port_input = QLineEdit("22")
        self.user_input = QLineEdit("pi")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)

        conn_layout.addWidget(QLabel("Host/IP:"))
        conn_layout.addWidget(self.host_input)
        conn_layout.addWidget(QLabel("Port:"))
        conn_layout.addWidget(self.port_input)
        conn_layout.addWidget(QLabel("Username:"))
        conn_layout.addWidget(self.user_input)
        conn_layout.addWidget(QLabel("Password:"))
        conn_layout.addWidget(self.pass_input)

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_ssh)
        conn_layout.addWidget(self.connect_btn)
        conn_layout.addStretch()
        conn_group.setLayout(conn_layout)

        main_layout.addWidget(conn_group, 1)

        # === Khung terminal ===
        term_group = QGroupBox("💻 SSH Terminal (PuTTY style)")
        term_layout = QVBoxLayout()

        self.terminal = QTextEdit()
        self.terminal.setReadOnly(False)
        self.terminal.setFont(QFont("Consolas", 12))
        self.terminal.setStyleSheet(
            "background-color: black; color: #00FF00; border: 2px solid #444;"
        )
        self.terminal.installEventFilter(self)
        term_layout.addWidget(self.terminal)
        term_group.setLayout(term_layout)
        main_layout.addWidget(term_group, 3)

        # --- Kết nối tín hiệu output_received ---
        self.output_received.connect(self.append_output)  # ✅

        # --- Blink con trỏ giả ---
        self.cursor_timer = QTimer()
        self.cursor_timer.timeout.connect(self.blink_cursor)
        self.cursor_timer.start(500)

    def blink_cursor(self):
        self.cursor_visible = not self.cursor_visible
        self.terminal.setStyleSheet(
            f"background-color: black; color: {'#00FF00' if self.cursor_visible else '#00AA00'}; border: 2px solid #444;"
        )

    def connect_ssh(self):
        host = self.host_input.text()
        port = int(self.port_input.text())
        user = self.user_input.text()
        passwd = self.pass_input.text()

        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(host, port, user, passwd)
            self.channel = self.client.invoke_shell()
            self.channel.settimeout(0.0)
            self.output_received.emit(f"✅ Connected to {host}\n")
            threading.Thread(target=self.read_data, daemon=True).start()
        except Exception as e:
            QMessageBox.critical(self, "SSH Error", str(e))

    def read_data(self):
        """Luồng phụ: đọc dữ liệu từ SSH, gửi về GUI qua signal."""
        while self.channel and not self.channel.closed:
            try:
                data = self.channel.recv(1024)
                if data:
                    text = data.decode("utf-8", errors="ignore")
                    self.output_received.emit(text)  # ✅ an toàn thread
            except Exception:
                pass

    def append_output(self, text):
        """Slot: cập nhật giao diện GUI (chạy trên main thread)."""
        self.terminal.moveCursor(QTextCursor.End)
        self.terminal.insertPlainText(text)
        self.terminal.ensureCursorVisible()

    def eventFilter(self, source, event):
        if source is self.terminal and self.channel:
            if event.type() == event.KeyPress:
                key = event.text()
                if key:
                    try:
                        self.channel.send(key)
                    except Exception:
                        pass
                elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    self.channel.send("\n")
                    return True
                elif event.key() == Qt.Key_Backspace:
                    self.channel.send("\b")
                    return True
        return super().eventFilter(source, event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PuttyLikeSSH()
    win.show()
    sys.exit(app.exec_())