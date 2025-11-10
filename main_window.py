# main_window.py

import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QTextEdit, QRadioButton, QMessageBox,
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QTimer, Qt
import pyqtgraph as pg

import global_var
from ssh_handler import SSHHandler, create_ssh_group_box
from temp_ctrl import create_temperature_show_box, create_temperature_control_box, update_graph
from exp_manual import create_manual_group_box
from exp_auto import create_auto_group_box

import queue
from socket_handler import TCPServer, create_socket_group_box


class CubeSat_Monitor(QWidget):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        if event.key() == Qt.Key_F11:
            self.full_secreen = not self.full_secreen
            if self.full_secreen:
                self.showFullScreen()
            else:
                self.showNormal()

        

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("img/S_logo.png"))
        self.setWindowTitle("CubeSat System")
        self.resize(1920, 1080)
        self.full_secreen = True

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

        # --- Data queue + TCP server
        self.tcp_host = "0.0.0.0"
        self.tcp_port = 5000
        self.data_queue = queue.Queue()

        # ========= CỘT 1 =========
        self.init_col1(col1_layout)

        # ========= CỘT 2 =========
        self.init_col2(col2_layout)

        # ========= CỘT 3 =========
        self.init_col3(col3_layout)

        # --- Timer cập nhật biểu đồ ---
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: update_graph(self))
        self.timer.start(50)  # cập nhật mỗi 50ms

    # ----------------------------
    # CỘT 1: Nhiệt độ + Log
    # ----------------------------
    def init_col1(self, layout):
        # Cột 1 Hàng 1
        self.temp_show_group = create_temperature_show_box(self)

        # Cột 1 Hàng 2
        self.temp_ctrl_group = create_temperature_control_box(self)

        # Cột 1 Hàng 3
        log_group = QGroupBox("📝 Log / Trạng thái")
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        conn_ssh_layout = QVBoxLayout()
        conn_ssh_layout.addWidget(self.log_box)
        log_group.setLayout(conn_ssh_layout)

        layout.addWidget(self.temp_show_group, 1)
        layout.addWidget(self.temp_ctrl_group, 1)
        layout.addWidget(log_group, 2)

    # ----------------------------
    # CỘT 2: Biểu đồ + Điều khiển
    # ----------------------------
    def init_col2(self, layout):
        # --- Cột 2 hàng 1: Biểu đồ ---
        graph_group = QGroupBox("📊 Biểu đồ nhiệt độ 8 NTC")
        graph_layout = QVBoxLayout()
        self.graph = pg.PlotWidget(title="Nhiệt độ 8 NTC theo thời gian (°C)")
        self.graph.showGrid(x=True, y=True)
        self.graph.setLabel('left', 'Nhiệt độ (°C)')
        self.graph.setLabel('bottom', 'Thời gian (chu kỳ)')
        self.graph.addLegend(offset=(10, 10))
        graph_layout.addWidget(self.graph)
        graph_group.setLayout(graph_layout)

        # --- Cột 2 hàng 2: Điều khiển ---
        exp_group = QGroupBox("🛠️ Điều khiển thí nghiệm")
        exp_layout = QHBoxLayout()

        # --- Cột 2 hàng 2 cột 1: Manual or Auto ---
        exp_choice_mode_group = QGroupBox("Chế độ")
        exp_choice_mode_layout = QVBoxLayout()  
        self.manual_toggle_btn = QPushButton("Manual")
        self.manual_toggle_btn.setFixedSize(60, 200)
        self.manual_toggle_btn.setCheckable(True)
        self.manual_toggle_btn.setChecked(True)
        self.manual_toggle_btn.setStyleSheet(f"""
            border-radius: 20px;
            border: 2px solid black;
            font-weight: bold;
            background-color: {'#0b7dda'};
            color: {'white'};
        """)
        self.manual_toggle_btn.clicked.connect(lambda: self.toggle_mode(True))

        self.auto_toggle_btn = QPushButton("Auto")
        self.auto_toggle_btn.setFixedSize(60, 200)
        self.auto_toggle_btn.setCheckable(True)
        self.auto_toggle_btn.setChecked(False)
        self.auto_toggle_btn.setStyleSheet(f"""
            border-radius: 20px;
            border: 2px solid black;
            font-weight: bold;
            background-color: {'white'};
            color: {'black'};
        """)
        self.auto_toggle_btn.clicked.connect(lambda: self.toggle_mode(False))

        exp_choice_mode_layout.addWidget(self.manual_toggle_btn, alignment=Qt.AlignTop)
        exp_choice_mode_layout.addWidget(self.auto_toggle_btn, alignment=Qt.AlignTop)
        exp_choice_mode_group.setLayout(exp_choice_mode_layout)

        # --- Cột 2 hàng 2 Cột 2: Manual + Auto ---
        exp_control_group = QGroupBox("Chế độ Thí nghiệm")
        exp_control_layout = QHBoxLayout()
        
        # --- Cột 2 hàng 2 Cột 2 Option 1: Manual box ---
        self.manual_box, self.manual_buttons_list = create_manual_group_box(self)
        exp_control_layout.addWidget(self.manual_box, 8)

        # --- Cột 2 hàng 2 Cột 2 Option 2: Auto box ---
        self.auto_box = create_auto_group_box(self)
        exp_control_layout.addWidget(self.auto_box, 8)

        exp_control_group.setLayout(exp_control_layout)
        
        exp_layout.addWidget(exp_choice_mode_group, 1)
        exp_layout.addWidget(exp_control_group, 11)
        exp_group.setLayout(exp_layout)

        layout.addWidget(graph_group, 1)
        layout.addWidget(exp_group, 1)

        for i in range(8):
            color = pg.intColor(i, 8)
            curve = self.graph.plot(pen=pg.mkPen(color=color, width=2), name=f"NTC{i+1}")
            self.curves.append(curve)

    # ----------------------------
    # CỘT 3: SSH + Ảnh
    # ----------------------------
    def init_col3(self, layout):
        # --- Cột 3 hàng 1: Kết nối SSH ---
        # conn_ssh_group = create_ssh_group_box(self)
        conn_ssh_group = create_socket_group_box(self)

        # --- Cột 3 hàng 2: Ảnh hệ thống ---
        img_group = QGroupBox("📷 Hình ảnh hệ thống")
        img_layout = QVBoxLayout()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        pix = QPixmap("img/S_logo.png").scaled(500, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(pix)
        img_layout.addWidget(self.image_label)
        img_group.setLayout(img_layout)

        layout.addWidget(conn_ssh_group, 2)
        layout.addWidget(img_group, 4)



    # ----------------------------
    # Nhiệt độ
    # ----------------------------
    def start_control_temperature(self):
        try:
            target_temp = float(self.temp_target.text())
            global_var.target_temperature = target_temp
            self.log_box.append(f"[🌡️] Nhiệt độ mục tiêu được đặt thành {target_temp} °C")
            print(f"Target temperature set to {target_temp} °C")
        except ValueError:
            QMessageBox.warning(None, "Invalid Input", "Please enter a numeric value for temperature.") 


    def closeEvent(self, event):
        self.timer.stop()
        try:
            self.tcp_server.stop()
        except Exception:
            pass
        event.accept()

    # ----------------------------
    # Manual + Auto
    # ----------------------------
    def toggle_mode(self, manual_active: bool):
        self.manual_toggle_btn.setChecked(manual_active)
        self.auto_toggle_btn.setChecked(not manual_active)

        # Cập nhật style nút
        def update_style(button, active):
            button.setStyleSheet(f"""
                border-radius: 20px;
                border: 2px solid black;
                font-weight: bold;
                background-color: {'#0b7dda' if active else 'white'};
                color: {'white' if active else 'black'};
            """)

        update_style(self.manual_toggle_btn, manual_active)
        update_style(self.auto_toggle_btn, not manual_active)

        self.manual_box.setVisible(manual_active)
        self.auto_box.setVisible(not manual_active)

        mode_text = "MANUAL" if manual_active else "AUTO"
        self.log_box.append(f"[⚙️] Chuyển sang chế độ {mode_text}.")