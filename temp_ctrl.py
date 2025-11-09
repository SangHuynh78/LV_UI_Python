from PyQt5.QtWidgets import (
    QGroupBox, QGridLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
import global_var


def create_temperature_show_box(parent):
    """
    Tạo giao diện hiển thị nhiệt độ
    """
    temp_show_group = QGroupBox("🌡️ Nhiệt độ Hiện tại")
    temp_show_layout = QHBoxLayout()
    col_a, col_b = QVBoxLayout(), QVBoxLayout()
    parent.temp_labels = []

    for i in range(4):
        lbl = QLabel(f"NTC{i+1}: {global_var.ntc_temp[i]} °C")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size:16px;")
        col_a.addWidget(lbl)
        parent.temp_labels.append(lbl)

    for i in range(4, 8):
        lbl = QLabel(f"NTC{i+1}: {global_var.ntc_temp[i]} °C")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size:16px;")
        col_b.addWidget(lbl)
        parent.temp_labels.append(lbl)

    temp_show_layout.addLayout(col_a)
    temp_show_layout.addLayout(col_b)
    temp_show_group.setLayout(temp_show_layout)
    return temp_show_group


def create_temperature_control_box(parent):
    """
    Tạo giao diện điều khiển nhiệt độ
    """
    temp_ctrl_group = QGroupBox("🌡️ Điều khiển Nhiệt độ")
    temp_ctrl_layout = QGridLayout()

    # --- Các ô nhập liệu ---
    parent.tec_voltage = QLineEdit()
    parent.temp_target = QLineEdit()
    parent.temp_limit_min = QLineEdit()
    parent.temp_limit_max = QLineEdit()
    parent.ntc_pri = QLineEdit()
    parent.ntc_sec = QLineEdit()

    # Placeholder giúp gợi ý nội dung nhập
    parent.tec_voltage.setPlaceholderText("VTEC (mV)")
    parent.temp_target.setPlaceholderText("Target (°C)")
    parent.temp_limit_min.setPlaceholderText("Min (°C)")
    parent.temp_limit_max.setPlaceholderText("Max (°C)")
    parent.ntc_pri.setPlaceholderText("NTC pri")
    parent.ntc_sec.setPlaceholderText("NTC sec")

    # --- Nút START ---
    parent.start_temp_ctrl_btn = QPushButton("START")
    parent.start_temp_ctrl_btn.clicked.connect(lambda: start_control_temperature(parent))

    # --- Layout ---
    temp_ctrl_layout.addWidget(QLabel("TEC Voltage:"),          0, 0)
    temp_ctrl_layout.addWidget(parent.tec_voltage,              0, 1)

    temp_ctrl_layout.addWidget(QLabel("Temperature Target:"),   1, 0)
    temp_ctrl_layout.addWidget(parent.temp_target,              1, 1)

    temp_ctrl_layout.addWidget(QLabel("Temperature Limit:"),    2, 0)
    temp_ctrl_layout.addWidget(parent.temp_limit_min,           2, 1)
    temp_ctrl_layout.addWidget(QLabel("to"),                    2, 2)
    temp_ctrl_layout.addWidget(parent.temp_limit_max,           2, 3)

    temp_ctrl_layout.addWidget(QLabel("NTC Reference:"),        3, 0)
    temp_ctrl_layout.addWidget(QLabel("Pri:"),                  3, 1)
    temp_ctrl_layout.addWidget(parent.ntc_pri,                  3, 2)
    temp_ctrl_layout.addWidget(QLabel("Sec:"),                  3, 3)
    temp_ctrl_layout.addWidget(parent.ntc_sec,                  3, 4)

    temp_ctrl_layout.addWidget(parent.start_temp_ctrl_btn,      4, 1)

    temp_ctrl_group.setLayout(temp_ctrl_layout)
    return temp_ctrl_group


def start_control_temperature(parent):
    """
    Xử lý khi nhấn nút START điều khiển nhiệt độ
    """
    try:
        global_var.temp_tec_voltage = int(parent.tec_voltage.text())
        global_var.temp_target = float(parent.temp_target.text())
        global_var.temp_limit_min = float(parent.temp_limit_min.text())
        global_var.temp_limit_max = float(parent.temp_limit_max.text())
        global_var.ntc_pri_ref = float(parent.ntc_pri.text())
        global_var.ntc_sec_ref = float(parent.ntc_sec.text())
    except ValueError:
        QMessageBox.warning(parent, "⚠️ Cảnh báo", "Dữ liệu nhập không hợp lệ. Vui lòng kiểm tra lại.")
        return

    # --- Kiểm tra giới hạn ---
    if not (0 <= global_var.temp_tec_voltage <= 5000):
        QMessageBox.warning(parent, "⚠️ Cảnh báo", "TEC Voltage vượt giới hạn (0–5000 mV).")
        return

    if not (-40 <= global_var.temp_target <= 150):
        QMessageBox.warning(parent, "⚠️ Cảnh báo", "Temperature Target vượt giới hạn (-40–150 °C).")
        return

    if not (-40 <= global_var.temp_limit_min <= 150):
        QMessageBox.warning(parent, "⚠️ Cảnh báo", "Temperature Limit Min vượt giới hạn (-40–150 °C).")
        return

    if not (-40 <= global_var.temp_limit_max <= 150):
        QMessageBox.warning(parent, "⚠️ Cảnh báo", "Temperature Limit Max vượt giới hạn (-40–150 °C).")
        return

    if global_var.temp_limit_min >= global_var.temp_limit_max:
        QMessageBox.warning(parent, "⚠️ Cảnh báo", "Temperature Limit Min phải nhỏ hơn Max.")
        return

    if not (0 <= global_var.ntc_pri_ref <= 100000):
        QMessageBox.warning(parent, "⚠️ Cảnh báo", "NTC Pri Reference vượt giới hạn (0–100kΩ).")
        return

    if not (0 <= global_var.ntc_sec_ref <= 100000):
        QMessageBox.warning(parent, "⚠️ Cảnh báo", "NTC Sec Reference vượt giới hạn (0–100kΩ).")
        return

    parent.log_box.append(f"[🌡️] Bắt đầu điều khiển nhiệt độ.")
    parent.start_temp_ctrl_btn.setText("STOP")

    # Đổi hành vi nút sang STOP
    parent.start_temp_ctrl_btn.clicked.disconnect()
    parent.start_temp_ctrl_btn.clicked.connect(lambda: stop_control_temperature(parent))

    # TODO: gửi lệnh điều khiển đến CM4 hoặc MCU
    # parent.ssh_handler.send_command(f"START_TEMP_CTRL {global_var.temp_target}")


def stop_control_temperature(parent):
    """
    Xử lý khi nhấn nút STOP điều khiển nhiệt độ
    """
    global_var.temp_auto_state = 0
    parent.log_box.append("[🌡️] Dừng điều khiển nhiệt độ.")
    parent.start_temp_ctrl_btn.setText("START")

    # Đổi hành vi nút trở lại START
    parent.start_temp_ctrl_btn.clicked.disconnect()
    parent.start_temp_ctrl_btn.clicked.connect(lambda: start_control_temperature(parent))

    # TODO: gửi lệnh điều khiển đến CM4 hoặc MCU
    # parent.ssh_handler.send_command(f"STOP_TEMP_CTRL")