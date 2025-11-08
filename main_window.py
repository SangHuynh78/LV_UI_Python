import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QTextEdit, QRadioButton, QMessageBox,
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QTimer, Qt
import pyqtgraph as pg

import global_var
from ssh_handler import SSHHandler
from exp_manual import create_manual_box

DEFAULT_HOST = "192.168.1.11"
DEFAULT_USER = "spec_cam"
DEFAULT_PASS = "cam"
DEFAULT_SCRIPT = "/home/spec_cam/SangHuynh_Dev/sang_temp.py"


class CubeSat_Monitor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("img/S_logo.png"))
        self.setWindowTitle("CubeSat System")
        self.resize(1920, 1080)

        # --- Dữ liệu nhiệt độ ---
        self.x_data = []
        self.index = 0
        self.curves = []

        # --- Bố cục chính ---
        main_layout = QHBoxLayout(self)
        col1_layout, col2_layout, col3_layout = QVBoxLayout(), QVBoxLayout(), QVBoxLayout()
        main_layout.addLayout(col1_layout, 1)
        main_layout.addLayout(col2_layout, 3)
        main_layout.addLayout(col3_layout, 1)

        # ========= CỘT 1 =========
        self.init_col1(col1_layout)

        # ========= CỘT 2 =========
        self.init_col2(col2_layout)

        # ========= CỘT 3 =========
        self.init_col3(col3_layout)

        # --- SSH handler ---
        self.ssh_handler = SSHHandler(self.log_box.append)

        # --- Timer cập nhật biểu đồ ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_graph)

    # ----------------------------
    # CỘT 1: Nhiệt độ + Log
    # ----------------------------
    def init_col1(self, layout):
        temp_group = QGroupBox("🌡️ Nhiệt độ Hiện tại")
        temp_layout = QHBoxLayout()
        col_a, col_b = QVBoxLayout(), QVBoxLayout()
        self.temp_labels = []

        for i in range(4):
            lbl = QLabel(f"NTC{i+1}: {global_var.ntc_temp[i]} °C")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size:16px;")
            col_a.addWidget(lbl)
            self.temp_labels.append(lbl)

        for i in range(4, 8):
            lbl = QLabel(f"NTC{i+1}: {global_var.ntc_temp[i]} °C")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size:16px;")
            col_b.addWidget(lbl)
            self.temp_labels.append(lbl)

        temp_layout.addLayout(col_a)
        temp_layout.addLayout(col_b)
        temp_group.setLayout(temp_layout)

        log_group = QGroupBox("📝 Log / Trạng thái")
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        v = QVBoxLayout()
        v.addWidget(self.log_box)
        log_group.setLayout(v)

        layout.addWidget(temp_group, 1)
        layout.addWidget(log_group, 4)

    # ----------------------------
    # CỘT 2: Biểu đồ + Điều khiển
    # ----------------------------
    def init_col2(self, layout):
        # --- Biểu đồ ---
        graph_group = QGroupBox("📊 Biểu đồ nhiệt độ 8 NTC")
        graph_layout = QVBoxLayout()
        self.graph = pg.PlotWidget(title="Nhiệt độ 8 NTC theo thời gian (°C)")
        self.graph.showGrid(x=True, y=True)
        self.graph.setLabel('left', 'Nhiệt độ (°C)')
        self.graph.setLabel('bottom', 'Thời gian (chu kỳ)')
        self.graph.addLegend(offset=(10, 10))
        graph_layout.addWidget(self.graph)
        graph_group.setLayout(graph_layout)

        # --- Điều khiển ---
        exp_group = QGroupBox("🛠️ Điều khiển thí nghiệm")
        exp_layout = QVBoxLayout()

        # Menu Manual/Auto
        menu_group = QGroupBox()
        menu_layout = QHBoxLayout()
        self.manual_radio = QRadioButton("Manual Mode")
        self.auto_radio = QRadioButton("Auto Mode")
        self.manual_radio.setChecked(True)
        self.manual_radio.toggled.connect(self.switch_mode)
        menu_layout.addWidget(self.manual_radio)
        menu_layout.addWidget(self.auto_radio)
        menu_group.setLayout(menu_layout)
        exp_layout.addWidget(menu_group)

        # Manual box
        self.manual_box, self.manual_buttons = create_manual_box(self)
        exp_layout.addWidget(self.manual_box, 8)

        # Auto box
        from PyQt5.QtWidgets import QPushButton
        self.auto_box = QGroupBox("🤖 Auto Control")
        auto_layout = QVBoxLayout()
        auto_layout.addWidget(QPushButton("Chạy chu trình thí nghiệm"))
        auto_layout.addWidget(QPushButton("Dừng chu trình"))
        self.auto_box.setLayout(auto_layout)
        self.auto_box.hide()
        exp_layout.addWidget(self.auto_box, 8)

        exp_group.setLayout(exp_layout)
        layout.addWidget(graph_group, 2)
        layout.addWidget(exp_group, 3)

        for i in range(8):
            color = pg.intColor(i, 8)
            curve = self.graph.plot(pen=pg.mkPen(color=color, width=2), name=f"NTC{i+1}")
            self.curves.append(curve)

    # ----------------------------
    # CỘT 3: SSH + Ảnh
    # ----------------------------
    def init_col3(self, layout):
        conn_group = QGroupBox("🔌 Kết nối SSH")
        v = QVBoxLayout()
        self.host_input = QLineEdit(DEFAULT_HOST)
        self.user_input = QLineEdit(DEFAULT_USER)
        self.pass_input = QLineEdit(DEFAULT_PASS)
        self.pass_input.setEchoMode(QLineEdit.Password)
        v.addWidget(QLabel("Host IP:"))
        v.addWidget(self.host_input)
        v.addWidget(QLabel("Username:"))
        v.addWidget(self.user_input)
        v.addWidget(QLabel("Password:"))
        v.addWidget(self.pass_input)

        self.connect_btn = QPushButton("Connect SSH")
        self.connect_btn.clicked.connect(self.connect_ssh)
        v.addWidget(self.connect_btn)
        self.status_label = QLabel("⏳ Chưa kết nối.")
        v.addWidget(self.status_label)
        conn_group.setLayout(v)

        img_group = QGroupBox("📷 Hình ảnh hệ thống")
        img_layout = QVBoxLayout()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        pix = QPixmap("img/S_logo.png").scaled(500, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(pix)
        img_layout.addWidget(self.image_label)
        img_group.setLayout(img_layout)

        layout.addWidget(conn_group, 2)
        layout.addWidget(img_group, 4)

    # ----------------------------
    # SSH
    # ----------------------------
    def connect_ssh(self):
        host, user, pw = self.host_input.text(), self.user_input.text(), self.pass_input.text()
        self.ssh_handler.connect(host, user, pw, DEFAULT_SCRIPT)
        self.connect_btn.setText("Disconnect SSH")
        self.connect_btn.clicked.disconnect()
        self.connect_btn.clicked.connect(self.disconnect_ssh)
        self.timer.start(500)

    def disconnect_ssh(self):
        self.ssh_handler.disconnect()
        self.connect_btn.setText("Connect SSH")
        self.connect_btn.clicked.disconnect()
        self.connect_btn.clicked.connect(self.connect_ssh)
        self.timer.stop()

    # ----------------------------
    # Biểu đồ
    # ----------------------------
    def update_graph(self):
        self.ssh_handler.update_temps(self.x_data, global_var.ntc_temp, self.curves, self.temp_labels)

    def closeEvent(self, event):
        self.timer.stop()
        self.ssh_handler.disconnect()
        event.accept()

    # ----------------------------
    # Manual + Auto
    # ----------------------------
    def switch_mode(self):
        if self.manual_radio.isChecked():
            self.manual_box.show()
            self.auto_box.hide()
            self.log_box.append("[⚙️] Chuyển sang chế độ MANUAL.")
        else:
            self.manual_box.hide()
            self.auto_box.show()
            self.log_box.append("[⚙️] Chuyển sang chế độ AUTO.")
     
    # ----------------------------
    # Manual Function
    # ----------------------------
    def manual_exp_with_pos(self, pos, percent, btn):
        """
        Thực hiện thao tác thí nghiệm tại vị trí 'pos' với giá trị DAC 'percent'.

        Args:
            pos (int): Vị trí nút (1..36)
            percent (int): Giá trị DAC hiện tại (%)
            btn (QPushButton): Nút vừa nhấn

        Hành vi:
            - Bật hoặc tắt thí nghiệm tại vị trí 'pos'.
            - Thay đổi màu nút dựa trên trạng thái (checked/unchecked).
            - Ghi log trạng thái + giá trị DAC vào log_box.
        """

        state = btn.isChecked()  # True nếu đang được chọn
        # Log ra thông tin vị trí + DAC
        if state:
            if global_var.dac_value == 0:
                QMessageBox.warning(None, "Invalid Input", "Please enter a numeric value.")
                # Reset nút về trạng thái unchecked
                btn.setChecked(False)
                return
            self.log_box.append(f"[🧭] Bật thí nghiệm tại vị trí {pos}, DAC={percent}%")
        else:
            self.log_box.append(f"[🧭] Tắt thí nghiệm tại vị trí {pos}")
        
        # Cập nhật màu nút theo trạng thái
        if state:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #45a049;
                    color: white;
                    font-weight: bold;
                    border-radius: 30px;
                    border: 2px solid black;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: black;
                    font-weight: bold;
                    border-radius: 30px;
                    border: 2px solid black;
                }
            """)
        
        # TODO: Gửi lệnh thực tế đến thiết bị nếu cần
        # self.ssh_handler.send_exp_command(pos, state, percent)