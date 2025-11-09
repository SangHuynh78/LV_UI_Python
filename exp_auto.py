# exp_auto.py
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QGridLayout, QLineEdit, QLabel

import global_var

def create_auto_group_box(parent):
    """
    Tạo group box cho chế độ Auto Mode.
    """
    exp_auto_group = QGroupBox("🤖 Auto Control")

    exp_auto_layout = QGridLayout()

    # --- Các ô nhập liệu ---
    parent.exp_sample_rate = QLineEdit()
    parent.exp_position = QLineEdit()
    parent.exp_laser_percent = QLineEdit()
    parent.exp_pre_time = QLineEdit()
    parent.exp_experiment_time = QLineEdit()
    parent.exp_post_time = QLineEdit()

    # Placeholder giúp gợi ý nội dung nhập
    parent.exp_sample_rate.setPlaceholderText("1000 sps")
    parent.exp_position.setPlaceholderText("1-36")
    parent.exp_laser_percent.setPlaceholderText("0-100%")
    parent.exp_pre_time.setPlaceholderText("1000 ms")
    parent.exp_experiment_time.setPlaceholderText("2000 ms")
    parent.exp_post_time.setPlaceholderText("1000 ms")

    # --- Nút START ---
    start_btn = QPushButton("START")
    # Gắn sự kiện cho nút START
    start_btn.clicked.connect(start_experiment)

    # --- Bố trí exp_auto_layout ---
    exp_auto_layout.addWidget(QLabel("Sample Rate:"),          0, 0)
    exp_auto_layout.addWidget(parent.exp_sample_rate,          0, 1)

    exp_auto_layout.addWidget(QLabel("Position:"),              1, 0)
    exp_auto_layout.addWidget(parent.exp_position,              1, 1)

    exp_auto_layout.addWidget(QLabel("Laser Percent:"),         2, 0)
    exp_auto_layout.addWidget(parent.exp_laser_percent,         2, 1)

    exp_auto_layout.addWidget(QLabel("Pre Time:"),             3, 0)
    exp_auto_layout.addWidget(parent.exp_pre_time,              3, 1)
    exp_auto_layout.addWidget(QLabel("Experiment Time:"),      4, 0)
    exp_auto_layout.addWidget(parent.exp_experiment_time,      4, 1)
    exp_auto_layout.addWidget(QLabel("Post Time:"),            5, 0)
    exp_auto_layout.addWidget(parent.exp_post_time,             5, 1)
    exp_auto_layout.addWidget(start_btn,                        7, 0, 1, 2)

    # Ẩn group box ban đầu
    exp_auto_group.hide()

    exp_auto_group.setLayout(exp_auto_layout)
    return exp_auto_group

def start_experiment(self):
    """
    Bắt đầu thí nghiệm với các tham số đã nhập.
    """
    # Lấy giá trị từ các ô nhập liệu lưu vào global_var

    global_var.exp_sample_rate = self.exp_sample_rate.text()
    global_var.exp_position = self.exp_position.text()
    global_var.exp_laser_percent = self.exp_laser_percent.text()
    global_var.exp_pre_time = self.exp_pre_time.text()
    global_var.exp_experiment_time = self.exp_experiment_time.text()
    global_var.exp_post_time = self.exp_post_time.text()

    # Ghi log các tham số đã nhập
    self.log_box.append(f"[🤖] Bắt đầu thí nghiệm với các tham số:")
    self.log_box.append(f"    Sample Rate: {global_var.exp_sample_rate}")
    self.log_box.append(f"    Position: {global_var.exp_position}")
    self.log_box.append(f"    Laser Percent: {global_var.exp_laser_percent}")
    self.log_box.append(f"    Pre Time: {global_var.exp_pre_time}")
    self.log_box.append(f"    Experiment Time: {global_var.exp_experiment_time}")
    self.log_box.append(f"    Post Time: {global_var.exp_post_time}")
    # Thêm mã để gửi các tham số này đến thiết bị qua SSH hoặc thực hiện thí nghiệm ở đây
