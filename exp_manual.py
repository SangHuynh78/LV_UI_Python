from PyQt5.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton,
    QLineEdit, QMessageBox, QSizePolicy
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
            btn.setFixedSize(60, 60)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    border-radius: 30px;
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
            # Kết nối đến hàm manual_exp_with_pos của parent
            btn.clicked.connect(lambda _, pos=idx, b=btn: manual_exp_with_pos(parent, pos, global_var.manual_laser_percent, b))
            grid.addWidget(btn, i, j)
            buttons.append(btn)

    grid_group.setLayout(grid)
    layout_laser.addWidget(grid_group, 7)

    # --- Nhóm điều khiển DAC ---
    dac_group = QGroupBox("DAC Control")
    dac_layout = QVBoxLayout()

    dac_text_line = QLineEdit()
    dac_text_line.setFixedWidth(200)
    dac_text_line.setPlaceholderText("Nhập giá trị DAC (0-100) %")

    dac_button = QPushButton("Set DAC")
    dac_button.setFixedWidth(100)
    dac_button.setFixedHeight(60)
    dac_button.setStyleSheet("""
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
    dac_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    # ✅ Sửa lỗi: dùng lambda để gọi đúng lúc click
    dac_button.clicked.connect(lambda: on_set_dac(dac_text_line, parent))

    dac_layout.addWidget(dac_text_line, alignment=Qt.AlignHCenter)
    dac_layout.addWidget(dac_button, alignment=Qt.AlignHCenter)
    dac_layout.setAlignment(Qt.AlignCenter)
    dac_layout.setSpacing(15)
    dac_group.setLayout(dac_layout)
    layout_laser.addWidget(dac_group, 3)

    manual_box.setLayout(layout_laser)
    return manual_box, buttons


def on_set_dac(dac_lineedit, parent):
    """
    Xử lý khi nhấn nút Set DAC
    """
    try:
        val = int(dac_lineedit.text())

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
        QPushButton {{
            border-radius: 30px;
            border: 2px solid black;
            font-weight: bold;
            background-color: {'#45a049' if state else 'white'};
            color: {'white' if state else 'black'};
        }}
    """)

    # TODO: gửi lệnh thực tế đến thiết bị nếu cần
    # self.ssh_handler.send_exp_command(pos, state, percent)