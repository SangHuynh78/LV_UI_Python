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
from temp_ctrl import create_temperature_show_box, create_temperature_control_box
from exp_manual import create_manual_group_box
from exp_auto import create_auto_group_box



class CubeSat_Monitor(QWidget):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        if event.key() == Qt.Key_F11:
            if self.full_secreen == True:
                self.full_secreen = False
                self.showNormal()
            elif self.full_secreen == False:
                self.full_secreen = True
                self.showMaximized()
        

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
        exp_layout = QVBoxLayout()

        # --- Cột 2 hàng 2.1: Menu Manual/Auto ---
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

        # --- Cột 2 hàng 2.2: Manual box ---
        self.manual_box, self.manual_buttons = create_manual_group_box(self)
        exp_layout.addWidget(self.manual_box, 8)

        # --- Cột 2 hàng 2.3: Auto box ---
        self.auto_box = create_auto_group_box(self)
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
        # --- Cột 3 hàng 1: Kết nối SSH ---
        conn_ssh_group = create_ssh_group_box(self)

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