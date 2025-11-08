from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLineEdit, QMessageBox, QSizePolicy
from PyQt5.QtCore import Qt
import global_var

def create_manual_box(parent):
    manual_box = QGroupBox("🧭 Manual Control")
    layout_laser = QHBoxLayout()

    # Grid of buttons
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
            btn.clicked.connect(lambda _, pos=idx, b=btn: parent.manual_exp_with_pos(pos, global_var.dac_value, b))
            grid.addWidget(btn, i, j)
            buttons.append(btn)

    grid_group.setLayout(grid)
    layout_laser.addWidget(grid_group, 7)

    # DAC Control
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

    def on_set_dac():
        try:
            val = int(dac_text_line.text())
            if 0 <= val <= 100:
                global_var.dac_value = val
                parent.log_box.append(f"[🎛️] DAC value set to {val}%")
                print(f"Setting DAC value to {val}%")
            else:
                QMessageBox.warning(None, "Invalid Input", "Please enter a value between 0 and 100.")
        except ValueError:
            QMessageBox.warning(None, "Invalid Input", "Please enter a numeric value.")

    dac_button.clicked.connect(on_set_dac)

    dac_layout.addWidget(dac_text_line, alignment=Qt.AlignHCenter)
    dac_layout.addWidget(dac_button, alignment=Qt.AlignHCenter)
    dac_layout.setAlignment(Qt.AlignCenter)
    dac_layout.setSpacing(15)
    dac_group.setLayout(dac_layout)
    layout_laser.addWidget(dac_group, 3)

    manual_box.setLayout(layout_laser)
    return manual_box, buttons

