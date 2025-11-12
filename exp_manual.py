from PyQt5.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton,
    QLineEdit, QMessageBox, QSizePolicy, QLabel
)
from PyQt5.QtCore import Qt
import global_var


def create_manual_group_box(parent):
    manual_box = QGroupBox("🧭 Manual Control")
    layout_laser = QHBoxLayout()

    # --- Nhóm điều khiển Laser Intensity ---
    manual_laser_percent_group = QGroupBox("Laser Intensity")
    manual_laser_percent_layout = QVBoxLayout()

    # Vdac info
    manual_laser_vDAC_max = QLabel("Vdac(max) = 3.3V")
    manual_laser_vDAC_max.setAlignment(Qt.AlignCenter)

    # Label
    manual_laser_percent_label = QLabel("Laser Percent")
    manual_laser_percent_label.setAlignment(Qt.AlignCenter)

    # Nhóm nhập giá trị và đơn vị
    input_layout = QHBoxLayout()
    manual_laser_percent_text_line = QLineEdit()
    manual_laser_percent_text_line.setFixedWidth(160)
    manual_laser_percent_text_line.setFixedHeight(35)
    manual_laser_percent_text_line.setPlaceholderText("Type laser percent")
    manual_laser_percent_text_line.setAlignment(Qt.AlignCenter)
    manual_laser_percent_unit = QLabel("%")
    manual_laser_percent_unit.setAlignment(Qt.AlignVCenter)
    input_layout.addStretch()
    input_layout.addWidget(manual_laser_percent_text_line)
    input_layout.addWidget(manual_laser_percent_unit)
    input_layout.addStretch()

    # Nút bấm
    manual_laser_percent_btn = QPushButton("Set Intensity")
    manual_laser_percent_btn.setFixedSize(200, 50)
    manual_laser_percent_btn.setStyleSheet("""
        QPushButton {
            background-color: #64B5F6;  /* Xanh nhạt */
            color: white;
            font-weight: bold;
            border-radius: 20px;
            border: 2px solid #1E88E5;
        }
        QPushButton:hover {
            background-color: #42A5F5;  /* Khi rê chuột vào */
        }
        QPushButton:pressed {
            background-color: #1E88E5;  /* Khi nhấn */
            border: 2px solid #1565C0;
        }
    """)
    manual_laser_percent_btn.clicked.connect(lambda: on_set_dac(manual_laser_percent_text_line, parent))

    # Ghép bố cục tổng
    manual_laser_percent_layout.addSpacing(5)
    manual_laser_percent_layout.addWidget(manual_laser_vDAC_max)
    manual_laser_percent_layout.addSpacing(15)
    manual_laser_percent_layout.addWidget(manual_laser_percent_label)
    manual_laser_percent_layout.addSpacing(15)
    manual_laser_percent_layout.addLayout(input_layout)
    manual_laser_percent_layout.addSpacing(20)
    manual_laser_percent_layout.addWidget(manual_laser_percent_btn, alignment=Qt.AlignCenter)
    manual_laser_percent_layout.addStretch()

    manual_laser_percent_group.setLayout(manual_laser_percent_layout)


    # --- Grid các nút vị trí laser ---
    grid_group = QGroupBox("Laser Positions")
    grid = QGridLayout()
    # buttons = []
    parent.manual_buttons_list = []

    for i in range(6):
        for j in range(6):
            idx = i * 6 + j + 1
            btn = QPushButton(str(idx))
            btn.setFixedSize(40, 40)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    border-radius: 20px;
                    border: 2px solid black;
                    background-color: white;
                    color: black;
                    font-weight: bold;
                }
                QPushButton:checked {
                    background-color: #45a049;
                    border: 2px solid black;
                    color: white;
                }
            """)
            # Kết nối đến hàm manual_exp_with_pos
            btn.clicked.connect(lambda _, pos=idx, b=btn: manual_exp_with_pos(parent, pos, global_var.manual_laser_percent, b))
            # btn.clicked.connect(lambda _: abc(parent, 1, 2, 3))
            
            # Chèn vào grid, đảo cột: 5-j để cột 0 bên trái → cột 5 bên phải
            grid.addWidget(btn, i, 5 - j)
            # buttons.append(btn)
            parent.manual_buttons_list.append(btn)


    grid_group.setLayout(grid)

    layout_laser.addWidget(manual_laser_percent_group, 2)
    layout_laser.addWidget(grid_group, 8)

    manual_box.setLayout(layout_laser)
    # return manual_box, buttons
    return manual_box

def exp_manual_reset(parent):
    """
    Reset all manual laser position buttons to unchecked and update their style.
    """
    for btn in getattr(parent, "manual_buttons_list", []):
        btn.setChecked(False)
        btn.setStyleSheet("""
            border-radius: 20px;
            border: 2px solid black;
            font-weight: bold;
            background-color: white;
            color: black;
        """)
        btn.setChecked(False)
    
    # Gửi lệnh TCP
    if hasattr(parent, "tcp_server") and parent.tcp_server:
        parent.tcp_server.send_command(
            "laser_manual_turn_off_all"
        )

def on_set_dac(manual_laser_percent_text_line, parent):
    """
    Xử lý khi nhấn nút Set DAC
    """
    try:
        val = int(manual_laser_percent_text_line.text())

        if 0 <= val <= 100:
            global_var.manual_laser_percent = val
            print(f"Setting DAC value to {val}%")
            parent.log_box.append(f"[🎛️] DAC value set to {val}%")
            # Gửi lệnh TCP
            if hasattr(parent, "tcp_server") and parent.tcp_server:
                parent.tcp_server.send_command(
                    "laser_manual_set_percent",
                    laser_percent = global_var.manual_laser_percent
                )
        else:
            QMessageBox.warning(None, "Invalid Input", "Please enter a value between 0 and 100.")
    except ValueError:
        QMessageBox.warning(None, "Invalid Input", "Please enter a numeric value.")


def manual_exp_with_pos(parent, pos, percent, btn):
    """
    Thực hiện thao tác thí nghiệm tại vị trí 'pos' với giá trị DAC 'percent'.
    """
    state = btn.isChecked()

    if state:
        if percent == 0:
            QMessageBox.warning(None, "Invalid Input", "DAC value is 0%. Please set a valid value.")
            btn.setChecked(False)
            return
        else:
            parent.log_box.append(f"[🧭] Bật thí nghiệm tại vị trí {pos}, DAC={percent}%")
            # Gửi lệnh TCP
            if hasattr(parent, "tcp_server") and parent.tcp_server:
                parent.tcp_server.send_command(
                    "laser_manual_turn_on",
                    laser_pos = pos
                )
    else:
        parent.log_box.append(f"[🧭] Tắt thí nghiệm tại vị trí {pos}")
        # Gửi lệnh TCP
        if hasattr(parent, "tcp_server") and parent.tcp_server:
            parent.tcp_server.send_command(
                "laser_manual_turn_off",
                laser_pos = pos
            )

    # Cập nhật lại màu nút
    btn.setStyleSheet(f"""
        border-radius: 20px;
        border: 2px solid black;
        font-weight: bold;
        background-color: {'#45a049' if state else 'white'};
        color: {'white' if state else 'black'};
    """)

    # TODO: gửi lệnh thực tế đến thiết bị nếu cần
    # self.ssh_handler.send_exp_command(pos, state, percent)

def abc(parent, x, y, z):
    # Nếu server đang chạy → gửi lệnh cho client
    if hasattr(parent, "tcp_server") and parent.tcp_server:
        parent.tcp_server.send_command("abc", x=x, y=y, z=z)