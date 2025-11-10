from PyQt5.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton,
    QLineEdit, QMessageBox, QSizePolicy, QLabel
)
from PyQt5.QtCore import Qt
import global_var


def create_manual_group_box(parent):
    manual_box = QGroupBox("🧭 Manual Control")
    layout_laser = QHBoxLayout()

    # --- Grid các nút vị trí laser ---
    grid_group = QGroupBox("Laser Positions")
    grid = QGridLayout()
    buttons = []

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
            
            # Chèn vào grid, đảo cột: 5-j để cột 0 bên trái → cột 5 bên phải
            grid.addWidget(btn, i, 5 - j)
            buttons.append(btn)

    grid_group.setLayout(grid)
    layout_laser.addWidget(grid_group, 7)

    # --- Nhóm điều khiển Laser Intensity ---
    manual_laser_percent_group = QGroupBox("Laser Intensity Control")
    manual_laser_percent_layout = QGridLayout()

    manual_laser_percent_label = QLabel("Laser Intensity")

    manual_laser_percent_text_line = QLineEdit()
    manual_laser_percent_text_line.setFixedWidth(180)
    manual_laser_percent_text_line.setPlaceholderText("Type laser intensity (0-100)")

    manual_laser_percent_unit = QLabel("%")
    manual_laser_percent_unit.setFixedWidth(15)

    manual_laser_percent_btn = QPushButton("Set Intensity")
    manual_laser_percent_btn.setFixedWidth(100)
    manual_laser_percent_btn.setFixedHeight(60)
    manual_laser_percent_btn.setStyleSheet("""
        QPushButton {
            background-color: #2196F3;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            border: 2px solid black;
        }
        QPushButton:pressed {
            background-color: #0b7dda;
            border: 2px solid black;
        }
    """)
    manual_laser_percent_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    manual_laser_percent_btn.clicked.connect(lambda: on_set_dac(manual_laser_percent_text_line, parent))
    
    manual_laser_percent_layout.addWidget(manual_laser_percent_label, 0, 0, alignment=Qt.AlignCenter)
    manual_laser_percent_layout.addWidget(manual_laser_percent_text_line, 0, 1, alignment=Qt.AlignCenter)
    manual_laser_percent_layout.addWidget(manual_laser_percent_unit, 0, 2, alignment=Qt.AlignCenter)
    manual_laser_percent_layout.addWidget(manual_laser_percent_btn, 1, 0, 1, 3, alignment=Qt.AlignCenter)

    manual_laser_percent_group.setLayout(manual_laser_percent_layout)
    layout_laser.addWidget(manual_laser_percent_group, 3)

    manual_box.setLayout(layout_laser)
    return manual_box, buttons


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
        parent.log_box.append(f"[🧭] Bật thí nghiệm tại vị trí {pos}, DAC={percent}%")
    else:
        parent.log_box.append(f"[🧭] Tắt thí nghiệm tại vị trí {pos}")

    # Cập nhật lại màu nút
    btn.setStyleSheet(f"""
        border-radius: 25px;
        border: 2px solid black;
        font-weight: bold;
        background-color: {'#45a049' if state else 'white'};
        color: {'white' if state else 'black'};
    """)

    # TODO: gửi lệnh thực tế đến thiết bị nếu cần
    # self.ssh_handler.send_exp_command(pos, state, percent)