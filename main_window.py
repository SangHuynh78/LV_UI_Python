# main_window.py

import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,  QPushButton,
    QGroupBox, QTextEdit,
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QTimer, Qt
import pyqtgraph as pg

from temp_ctrl import create_temperature_show_box, create_temperature_graph_box, create_temperature_control_box, update_graph, create_temperature_override_box
from exp_manual import create_manual_group_box, exp_manual_reset
from exp_auto import create_auto_group_box

import queue
from socket_handler import create_socket_group_box
import global_var

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
        self.setWindowTitle("Sang Huynh")
        self.resize(1920, 1080)
        self.full_secreen = True

        self.state = {
            "tcp_connected": False,
            "temp_control_running": False,
            # sau này có thể thêm các trạng thái khác
        }

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
        self.tcp_server = None

        # ========= CỘT 1 =========
        self.init_col1(col1_layout)

        # ========= CỘT 2 =========
        self.init_col2(col2_layout)

        # ========= CỘT 3 =========
        self.init_col3(col3_layout)

        # --- Timer check tcp_connect ---
        self.app_block_timer = QTimer()
        self.app_block_timer.timeout.connect(self.tcp_connect_block_app_check)
        self.app_block_timer.start(100)  # cập nhật mỗi 100ms

        # --- Timer cập nhật biểu đồ ---
        self.graph_timer = QTimer()
        self.graph_timer.timeout.connect(lambda: update_graph(self))
        self.graph_timer.start(100)  # cập nhật mỗi 100ms

        # # Timer check queue
        # self.queue_timer = QTimer(self)
        # self.queue_timer.timeout.connect(lambda: self.process_queue())
        # self.queue_timer.start(100)  # 100ms/lần
    
    def closeEvent(self, event):
        self.app_block_timer.stop()
        self.tigraph_timermer.stop()
        # self.queue_timer.stop()
        if hasattr(self, "tcp_server") and self.tcp_server:
            try:
                self.tcp_server.stop()
            except:
                pass
        event.accept()

    def tcp_connect_block_app_check(self):
        if global_var.tcp_connect_changed == True:
            if global_var.tcp_connected == True: # UNLOCK
                self.start_temp_ctrl_btn.setEnabled(True)
                self.start_temp_override_btn.setEnabled(True)


            else: # LOCK
                self.start_temp_ctrl_btn.setEnabled(False)
                self.start_temp_override_btn.setEnabled(False)

                
            global_var.tcp_connect_changed = False




    # ----------------------------
    # CỘT 1: Nhiệt độ + Log
    # ----------------------------
    def init_col1(self, layout):
        # Cột 1 Hàng 1
        self.temp_show_group = create_temperature_show_box(self)

        # Cột 1 Hàng 2
        self.temp_ctrl_group = create_temperature_control_box(self)

        # Cột 1 Hàng 3
        self.temp_override_group = create_temperature_override_box(self)

        # Cột 1 Hàng 4
        log_group = QGroupBox("📝 Log")
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        conn_ssh_layout = QVBoxLayout()
        conn_ssh_layout.addWidget(self.log_box)
        log_group.setLayout(conn_ssh_layout)

        layout.addWidget(self.temp_show_group)
        layout.addWidget(self.temp_ctrl_group)
        layout.addWidget(self.temp_override_group)
        layout.addWidget(log_group)

    # ----------------------------
    # CỘT 2: Biểu đồ + Điều khiển
    # ----------------------------
    def init_col2(self, layout):
        # --- Cột 2 hàng 1: Đồ thị nhiệt độ ---
        temp_graph_group = create_temperature_graph_box(self)

        # --- Cột 2 hàng 2: Điều khiển ---
        exp_group = QGroupBox("🛠️ Experiment Control")
        exp_layout = QHBoxLayout()

        # # --- Cột 2 hàng 2 cột 1: Manual or Auto ---
        exp_choice_mode_group = self.create_mode_toggle_box()

        # --- Cột 2 hàng 2 Cột 2: Manual + Auto ---
        exp_control_group = QGroupBox()
        exp_control_layout = QHBoxLayout()
        
        # --- Cột 2 hàng 2 Cột 2 Option 1: Manual box ---
        # self.manual_box, self.manual_buttons_list = create_manual_group_box(self)
        self.manual_box = create_manual_group_box(self)
        exp_control_layout.addWidget(self.manual_box, 8)

        # --- Cột 2 hàng 2 Cột 2 Option 2: Auto box ---
        self.auto_box = create_auto_group_box(self)
        exp_control_layout.addWidget(self.auto_box, 8)

        exp_control_group.setLayout(exp_control_layout)
        
        exp_layout.addWidget(exp_choice_mode_group, 1)
        exp_layout.addWidget(exp_control_group, 11)
        exp_group.setLayout(exp_layout)

        layout.addWidget(temp_graph_group, 1)
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
        conn_ssh_group = create_socket_group_box(self)

        # --- Cột 3 hàng 2: Ảnh hệ thống ---
        img_group = QGroupBox("📷 System Image")
        img_layout = QVBoxLayout()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        pix = QPixmap("img/S_logo.png").scaled(500, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(pix)
        img_layout.addWidget(self.image_label)
        img_group.setLayout(img_layout)

        layout.addWidget(conn_ssh_group, 1)
        layout.addWidget(img_group, 5)




    # ----------------------------
    # Manual + Auto
    # ----------------------------
    def create_mode_toggle_box(self):
        """
        Tạo group box chứa 2 nút Manual / Auto dạng toggle.
        """
        mode_group = QGroupBox("Chế độ Thí nghiệm")
        layout = QVBoxLayout()
        # --- Manual button ---
        self.manual_toggle_btn = QPushButton("Manual")
        self.manual_toggle_btn.setFixedSize(60, 200)
        self.manual_toggle_btn.setCheckable(True)
        self.manual_toggle_btn.setChecked(True)
        self.manual_toggle_btn.clicked.connect(lambda: self.toggle_mode(True))
        # --- Auto button ---
        self.auto_toggle_btn = QPushButton("Auto")
        self.auto_toggle_btn.setFixedSize(60, 200)
        self.auto_toggle_btn.setCheckable(True)
        self.auto_toggle_btn.setChecked(False)
        self.auto_toggle_btn.clicked.connect(lambda: self.toggle_mode(False))
        # --- Thêm vào layout ---
        layout.addWidget(self.manual_toggle_btn, alignment=Qt.AlignTop)
        layout.addWidget(self.auto_toggle_btn, alignment=Qt.AlignTop)
        mode_group.setLayout(layout)
        # --- Khởi tạo style và hiển thị lần đầu ---
        self.toggle_mode(True)
        return mode_group


    def toggle_mode(self, manual_active: bool):
        """
        Bật/tắt chế độ Manual / Auto
        """
        # Cập nhật trạng thái checked
        self.manual_toggle_btn.setChecked(manual_active)
        self.auto_toggle_btn.setChecked(not manual_active)
        # --- Cập nhật style nút ---
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
        # --- Hiển thị box tương ứng ---
        if hasattr(self, "manual_box") and hasattr(self, "auto_box"):
            self.manual_box.setVisible(manual_active)
            self.auto_box.setVisible(not manual_active)

        # --- Reset manual nếu chuyển sang auto ---
        if not manual_active:
            exp_manual_reset(self)
