from PyQt5.QtWidgets import (
    QGroupBox, QGridLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox, QWidget
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
    Tạo giao diện điều khiển nhiệt độ với đơn vị hiển thị cuối ô
    """
    temp_ctrl_group = QGroupBox("🌡️ Điều khiển Nhiệt độ")
    temp_ctrl_layout = QGridLayout()

    # --- Hàm tiện lợi tạo ô nhập + đơn vị ---
    def create_lineedit_with_unit(unit):
        container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        lineedit = QLineEdit()
        label_unit = QLabel(unit)
        label_unit.setFixedWidth(20)  # hoặc một giá trị phù hợp
        lineedit.setFixedWidth(100)    # đảm bảo tất cả lineedit có cùng chiều ngang

        layout.addWidget(lineedit)
        layout.addWidget(label_unit)
        container.setLayout(layout)
        return container, lineedit

    # --- Các ô nhập liệu với đơn vị ---
    tec_widget, parent.tec_voltage = create_lineedit_with_unit("mV")
    target_widget, parent.temp_target = create_lineedit_with_unit("°C")
    limit_min_widget, parent.temp_limit_min = create_lineedit_with_unit("°C")
    limit_max_widget, parent.temp_limit_max = create_lineedit_with_unit("°C")
    ntc_pri_widget, parent.ntc_pri = create_lineedit_with_unit("")
    ntc_sec_widget, parent.ntc_sec = create_lineedit_with_unit("")

    # --- Nút START ---
    parent.start_temp_ctrl_btn = QPushButton("START")
    parent.start_temp_ctrl_btn.clicked.connect(lambda: start_control_temperature(parent))

    # --- Layout ---
    temp_ctrl_layout.addWidget(QLabel("TEC Voltage:"),          0, 0)
    temp_ctrl_layout.addWidget(tec_widget,                      0, 1)
    temp_ctrl_layout.addWidget(QLabel("Temp Target:"),          1, 0)
    temp_ctrl_layout.addWidget(target_widget,                   1, 1)
    temp_ctrl_layout.addWidget(QLabel("Temp Limit min:"),       2, 0)
    temp_ctrl_layout.addWidget(limit_min_widget,                2, 1)
    temp_ctrl_layout.addWidget(QLabel("Temp Limit max:"),       3, 0)
    temp_ctrl_layout.addWidget(limit_max_widget,                3, 1)
    temp_ctrl_layout.addWidget(QLabel("NTC Reference pri:"),    4, 0)
    temp_ctrl_layout.addWidget(ntc_pri_widget,                  4, 1)
    temp_ctrl_layout.addWidget(QLabel("NTC Reference sec:"),    5, 0)
    temp_ctrl_layout.addWidget(ntc_sec_widget,                  5, 1)
    temp_ctrl_layout.addWidget(parent.start_temp_ctrl_btn,      6, 0, 1, 2)

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
    if not (0 <= global_var.temp_tec_voltage <= 3000):
        QMessageBox.warning(parent, "⚠️ Cảnh báo", "TEC Voltage vượt giới hạn (0–3000 mV).")
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
        QMessageBox.warning(parent, "⚠️ Cảnh báo", "NTC Pri Reference vượt giới hạn (0–7).")
        return

    if not (0 <= global_var.ntc_sec_ref <= 100000):
        QMessageBox.warning(parent, "⚠️ Cảnh báo", "NTC Sec Reference vượt giới hạn (0–7).")
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