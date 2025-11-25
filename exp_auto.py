# exp_auto.py
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout, QLineEdit, QLabel, QWidget
from PyQt5.QtCore import Qt
import global_var

def create_auto_group_box(parent):
    """
    Tạo group box cho chế độ Auto Mode.
    """
    global_var.exp_auto_parent = parent

    exp_auto_group = QGroupBox("🤖 Auto Control")
    exp_auto_layout = QHBoxLayout()
    # --- Cột 1: Bố trí các ô nhập liệu và nút START ---
    exp_auto_profile_group = QGroupBox("Experiment Profile")
    exp_auto_profile_layout = QGridLayout()
    exp_auto_profile_layout.setSpacing(5)  # Giảm khoảng cách giữa các widget

    # --- Các ô nhập liệu ---
    parent.exp_sample_rate = QLineEdit("1000000")
    parent.exp_sample_rate.setMaximumWidth(120)
    parent.exp_first_position = QLineEdit("1")
    parent.exp_first_position.setMaximumWidth(55)
    parent.exp_end_position = QLineEdit("36")
    parent.exp_end_position.setMaximumWidth(55)
    parent.exp_laser_percent = QLineEdit("50")
    parent.exp_laser_percent.setMaximumWidth(120)
    parent.exp_pre_time = QLineEdit("100")
    parent.exp_pre_time.setMaximumWidth(120)
    parent.exp_experiment_time = QLineEdit("3800")
    parent.exp_experiment_time.setMaximumWidth(120)
    parent.exp_post_time = QLineEdit("100")
    parent.exp_post_time.setMaximumWidth(120)

    # Placeholder giúp gợi ý nội dung nhập
    parent.exp_sample_rate.setPlaceholderText("1000000")
    parent.exp_first_position.setPlaceholderText("1")
    parent.exp_end_position.setPlaceholderText("36")
    parent.exp_laser_percent.setPlaceholderText("0-100")
    parent.exp_pre_time.setPlaceholderText("1000")
    parent.exp_experiment_time.setPlaceholderText("2000")
    parent.exp_post_time.setPlaceholderText("1000")

    # --- Nút START ---
    parent.start_btn = QPushButton("START EXPERIMENT")
    parent.start_btn.setFixedSize(200, 40)
    parent.start_btn.setStyleSheet("""
        QPushButton {
            background-color: white;
            color: black;
            font-weight: bold;
            border-radius: 20px;
            border: 2px solid black;
        }
        QPushButton:hover:!disabled {
            background-color: grey;
        }
        QPushButton:pressed:!disabled {
            background-color: black;
            color: white;
            border: 2px solid black;
        }
        QPushButton:disabled {
            background-color: #f0f0f0;
            color: #808080;
            border: 2px solid #d0d0d0;
        }
    """)
    parent.start_btn.setEnabled(False)
    parent.start_btn.clicked.connect(lambda: start_experiment(parent))

    # --- Bố trí exp_auto_profile_layout ---
    label_sample_rate = QLabel("Sample Rate:")
    label_sample_rate.setMaximumWidth(120)
    exp_auto_profile_layout.addWidget(label_sample_rate, 0, 0)
    exp_auto_profile_layout.addWidget(parent.exp_sample_rate, 0, 1)
    exp_auto_profile_layout.addWidget(QLabel("bsp"), 0, 2)
    
    # 1: Position
    label_position = QLabel("Position:")
    label_position.setMaximumWidth(120)
    exp_auto_profile_layout.addWidget(label_position, 1, 0)
    pos_layout = QHBoxLayout()
    pos_layout.setAlignment(Qt.AlignLeft)
    pos_layout.setContentsMargins(0, 0, 0, 0)
    pos_layout.addWidget(parent.exp_first_position)
    arrow_label = QLabel("→")
    arrow_label.setFixedWidth(20)
    arrow_label.setAlignment(Qt.AlignCenter)
    pos_layout.addWidget(arrow_label)
    pos_layout.addWidget(parent.exp_end_position)
    pos_layout.addStretch(1)
    exp_auto_profile_layout.addLayout(pos_layout, 1, 1, 1, 2)

    label_laser = QLabel("Laser Percent:")
    label_laser.setMaximumWidth(120)
    exp_auto_profile_layout.addWidget(label_laser, 2, 0)
    exp_auto_profile_layout.addWidget(parent.exp_laser_percent, 2, 1)
    exp_auto_profile_layout.addWidget(QLabel("%"), 2, 2)

    label_pre = QLabel("Pre Time:")
    label_pre.setMaximumWidth(120)
    exp_auto_profile_layout.addWidget(label_pre, 3, 0)
    exp_auto_profile_layout.addWidget(parent.exp_pre_time, 3, 1)
    exp_auto_profile_layout.addWidget(QLabel("mS"), 3, 2)

    label_exp = QLabel("Experiment Time:")
    label_exp.setMaximumWidth(120)
    exp_auto_profile_layout.addWidget(label_exp, 4, 0)
    exp_auto_profile_layout.addWidget(parent.exp_experiment_time, 4, 1)
    exp_auto_profile_layout.addWidget(QLabel("mS"), 4, 2)

    label_post = QLabel("Post Time:")
    label_post.setMaximumWidth(120)
    exp_auto_profile_layout.addWidget(label_post, 5, 0)
    exp_auto_profile_layout.addWidget(parent.exp_post_time, 5, 1)
    exp_auto_profile_layout.addWidget(QLabel("mS"), 5, 2)

    # Căn giữa nút START
    start_btn_layout = QHBoxLayout()
    start_btn_layout.addStretch()
    start_btn_layout.addWidget(parent.start_btn)
    start_btn_layout.addStretch()
    exp_auto_profile_layout.addLayout(start_btn_layout, 6, 0, 1, 3)

    exp_auto_profile_group.setLayout(exp_auto_profile_layout)

    # --- Cột 2: Bố trí exp_auto_view_group ---
    # 36 ô hiển thị trạng thái vị trí laser
    exp_auto_view_group = QGroupBox("Experiment View")
    exp_auto_view_layout = QGridLayout()
    parent.exp_auto_position_labels = []

    for i in range(6):
        for j in range(6):
            idx = i * 6 + j + 1  # số từ 1->36
            btn = QPushButton(str(idx))
            btn.setFixedSize(40, 40)
            btn.setCheckable(False)
            btn.setEnabled(False)  # KHÔNG thể bấm vào
            btn.setStyleSheet("""
                QPushButton {
                    border-radius: 20px;
                    border: 2px solid black;
                    background-color: white;
                    color: black;
                    font-weight: bold;
                }
                QPushButton:disabled {
                background-color: #f0f0f0;
                color: #808080;
                border: 2px solid #d0d0d0;
            }
            """)
            exp_auto_view_layout.addWidget(btn, i, 5-j)
            parent.exp_auto_position_labels.append(btn)

    exp_auto_view_group.setLayout(exp_auto_view_layout)
    # --- Bố trí chính cho exp_auto_group ---
    
    exp_auto_layout.addWidget(exp_auto_profile_group, 3)
    exp_auto_layout.addWidget(exp_auto_view_group, 7)
    exp_auto_group.setLayout(exp_auto_layout)
    
    # Ẩn group box ban đầu
    exp_auto_group.hide()
    return exp_auto_group

def start_experiment(self):
    """
    Bắt đầu thí nghiệm với các tham số đã nhập.
    """
    # Lấy giá trị từ các ô nhập liệu lưu vào global_var
    global_var.exp_sample_rate = self.exp_sample_rate.text()
    global_var.exp_first_position = self.exp_first_position.text()
    global_var.exp_end_position = self.exp_end_position.text()
    global_var.exp_laser_percent = self.exp_laser_percent.text()
    global_var.exp_pre_time = self.exp_pre_time.text()
    global_var.exp_experiment_time = self.exp_experiment_time.text()
    global_var.exp_post_time = self.exp_post_time.text()

    # Ghi log các tham số đã nhập
    self.log_box.append(f"[🤖] Bắt đầu thí nghiệm với các tham số:")
    self.log_box.append(f"    Sample Rate: {global_var.exp_sample_rate}")
    self.log_box.append(f"    Position: {global_var.exp_first_position} to {global_var.exp_end_position}")
    self.log_box.append(f"    Laser Percent: {global_var.exp_laser_percent}")
    self.log_box.append(f"    Pre Time: {global_var.exp_pre_time}")
    self.log_box.append(f"    Experiment Time: {global_var.exp_experiment_time}")
    self.log_box.append(f"    Post Time: {global_var.exp_post_time}")

    # Gửi lệnh TCP
    if hasattr(self, "tcp_server") and self.tcp_server:
        self.tcp_server.send_command(
            "exp_start",
            exp_sample_rate = global_var.exp_sample_rate,
            exp_first_position = global_var.exp_first_position,
            exp_end_position = global_var.exp_end_position,
            exp_laser_percent = global_var.exp_laser_percent,
            exp_pre_time = global_var.exp_pre_time,
            exp_experiment_time = global_var.exp_experiment_time,
            exp_post_time = global_var.exp_post_time,
        )

# def exp_auto_turn_on_led(position):
#     idx = position - 1
#     parent = global_var.exp_auto_parent
#     parent.exp_auto_position_labels[idx].setStyleSheet("""
#         border-radius: 20px;
#         border: 2px solid black;
#         background-color: #45a049;
#         color: white;
#         font-weight: bold;
#     """)
#     print("exp_auto_turn_on_led\n")

# def exp_auto_turn_off_led(position):
#     # idx = position - 1
#     parent = global_var.exp_auto_parent
#     for i in range(6):
#         for j in range(6):
#             k = i * 6 + j
#             if 0 <= k < len(parent.exp_auto_position_labels):
#                 parent.exp_auto_position_labels[k].setStyleSheet("""
#                     border-radius: 20px;
#                     border: 2px solid black;
#                     background-color: white;
#                     color: black;
#                     font-weight: bold;
#                 """)
#     # parent.exp_auto_position_labels[idx].setStyleSheet("""
#     #     border-radius: 20px;
#     #     border: 2px solid black;
#     #     background-color: white;
#     #     color: black;
#     #     font-weight: bold;
#     # """)
#     print("exp_auto_turn_on_led\n")