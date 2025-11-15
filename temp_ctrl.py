from PyQt5.QtWidgets import (
    QGroupBox, QGridLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox, QWidget
)
from PyQt5.QtCore import Qt
import queue
import global_var
import pyqtgraph as pg


def create_temperature_show_box(parent):
    """
    Tạo giao diện hiển thị nhiệt độ
    """
    temp_show_group = QGroupBox("🌡️ Temperature Monitor")
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


def create_temperature_graph_box(parent):
    """
    Tạo group box hiển thị biểu đồ nhiệt độ.
    """
    graph_group = QGroupBox("📊 Temperature Graph")
    graph_layout = QVBoxLayout()
    # --- Tạo widget biểu đồ ---
    parent.graph = pg.PlotWidget()
    parent.graph.showGrid(x=True, y=True)
    parent.graph.setLabel('left', 'Nhiệt độ (°C)')
    parent.graph.setLabel('bottom', 'Thời gian (s)')
    parent.graph.addLegend(offset=(10, 10))
    # --- Thêm vào layout ---
    graph_layout.addWidget(parent.graph)
    graph_group.setLayout(graph_layout)
    return graph_group

def create_temperature_control_box(parent):
    temp_ctrl_group = QGroupBox("🌡️ Temperature Control")
    temp_ctrl_layout = QGridLayout()

    def create_lineedit_with_unit(unit, default_value=""):
        container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        lineedit = QLineEdit()
        lineedit.setText(str(default_value))
        label_unit = QLabel(unit)
        label_unit.setFixedWidth(20)
        lineedit.setFixedWidth(100)
        layout.addWidget(lineedit)
        layout.addWidget(label_unit)
        container.setLayout(layout)
        return container, lineedit

    tec_widget, parent.tec_voltage = create_lineedit_with_unit("mV", 1500)
    target_widget, parent.temp_target = create_lineedit_with_unit("°C", 25)
    limit_min_widget, parent.temp_limit_min = create_lineedit_with_unit("°C", 20)
    limit_max_widget, parent.temp_limit_max = create_lineedit_with_unit("°C", 30)
    ntc_pri_widget, parent.ntc_pri = create_lineedit_with_unit("", 0)
    ntc_sec_widget, parent.ntc_sec = create_lineedit_with_unit("", 1)

    parent.start_temp_ctrl_btn = QPushButton("START AUTO")
    parent.start_temp_ctrl_btn.setEnabled(False)
    parent.start_temp_ctrl_btn.clicked.connect(lambda: start_control_temperature(parent))

    temp_ctrl_layout.addWidget(QLabel("TEC Voltage:"), 0, 0)
    temp_ctrl_layout.addWidget(tec_widget, 0, 1)
    temp_ctrl_layout.addWidget(QLabel("Temp Target:"), 1, 0)
    temp_ctrl_layout.addWidget(target_widget, 1, 1)
    temp_ctrl_layout.addWidget(QLabel("Temp Limit min:"), 2, 0)
    temp_ctrl_layout.addWidget(limit_min_widget, 2, 1)
    temp_ctrl_layout.addWidget(QLabel("Temp Limit max:"), 3, 0)
    temp_ctrl_layout.addWidget(limit_max_widget, 3, 1)
    temp_ctrl_layout.addWidget(QLabel("NTC Reference pri:"), 4, 0)
    temp_ctrl_layout.addWidget(ntc_pri_widget, 4, 1)
    temp_ctrl_layout.addWidget(QLabel("NTC Reference sec:"), 5, 0)
    temp_ctrl_layout.addWidget(ntc_sec_widget, 5, 1)
    temp_ctrl_layout.addWidget(parent.start_temp_ctrl_btn, 6, 0, 1, 2)

    temp_ctrl_group.setLayout(temp_ctrl_layout)
    return temp_ctrl_group


def create_temperature_override_box(parent):
    temp_override_group = QGroupBox("🌡️ Temperature Override")
    temp_override_layout = QGridLayout()

    def create_lineedit_with_unit(unit, default_value=""):
        container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        lineedit = QLineEdit()
        lineedit.setText(str(default_value))
        label_unit = QLabel(unit)
        label_unit.setFixedWidth(20)
        lineedit.setFixedWidth(100)
        layout.addWidget(lineedit)
        layout.addWidget(label_unit)
        container.setLayout(layout)
        return container, lineedit

    tec_override_voltage_widget, parent.tec_override_voltage = create_lineedit_with_unit("mV", 1500)
    tec_override_interval_widget, parent.tec_override_interval = create_lineedit_with_unit("mS", 1000)

    parent.start_temp_override_btn = QPushButton("START OVERRIDE")
    parent.start_temp_override_btn.setEnabled(False)
    parent.start_temp_override_btn.clicked.connect(lambda: start_override_temperature(parent))

    temp_override_layout.addWidget(QLabel("TEC Override Voltage:"), 0, 0)
    temp_override_layout.addWidget(tec_override_voltage_widget,     0, 1)
    temp_override_layout.addWidget(QLabel("TEC Override Interval:"),1, 0)
    temp_override_layout.addWidget(tec_override_interval_widget,    1, 1)

    temp_override_layout.addWidget(parent.start_temp_override_btn,  2, 0, 1, 2)

    temp_override_group.setLayout(temp_override_layout)
    return temp_override_group

def start_control_temperature(parent):
    try:
        global_var.temp_tec_voltage = int(parent.tec_voltage.text())
        global_var.temp_target = float(parent.temp_target.text())
        global_var.temp_limit_min = float(parent.temp_limit_min.text())
        global_var.temp_limit_max = float(parent.temp_limit_max.text())
        global_var.temp_ntc_pri_ref = float(parent.ntc_pri.text())
        global_var.temp_ntc_sec_ref = float(parent.ntc_sec.text())
    except ValueError:
        QMessageBox.warning(parent, "⚠️ Cảnh báo", "Dữ liệu nhập không hợp lệ.")
        return

    # Khóa ô nhập liệu
    parent.tec_voltage.setEnabled(False)
    parent.temp_target.setEnabled(False)
    parent.temp_limit_min.setEnabled(False)
    parent.temp_limit_max.setEnabled(False)
    parent.ntc_pri.setEnabled(False)
    parent.ntc_sec.setEnabled(False)

    # Kiểm tra giới hạn...
    # (giữ nguyên như trước)

    parent.log_box.append("[🌡️] Bắt đầu điều khiển nhiệt độ.")

    # Đổi hành vi nút thành STOP
    parent.start_temp_ctrl_btn.setText("STOP AUTO")
    parent.start_temp_ctrl_btn.clicked.disconnect()
    parent.start_temp_ctrl_btn.clicked.connect(lambda: stop_control_temperature(parent))

    # Gửi lệnh TCP
    if hasattr(parent, "tcp_server") and parent.tcp_server:
        parent.tcp_server.send_command(
            "temp_auto_start",
            tec_vol=global_var.temp_tec_voltage,
            temp_target=global_var.temp_target,
            temp_lim_min=global_var.temp_limit_min,
            temp_lim_max=global_var.temp_limit_max,
            ntc_ref_pri=global_var.temp_ntc_pri_ref,
            ntc_ref_sec=global_var.temp_ntc_sec_ref
        )

def stop_control_temperature(parent):
    """
    Xử lý khi nhấn nút STOP điều khiển nhiệt độ
    """
    global_var.temp_auto_state = 0
    parent.log_box.append("[🌡️] Dừng điều khiển nhiệt độ.")

    # Mở khóa ô nhập liệu
    parent.tec_voltage.setEnabled(True)
    parent.temp_target.setEnabled(True)
    parent.temp_limit_min.setEnabled(True)
    parent.temp_limit_max.setEnabled(True)
    parent.ntc_pri.setEnabled(True)
    parent.ntc_sec.setEnabled(True)
    
    # Đổi hành vi nút trở lại START
    parent.start_temp_ctrl_btn.setText("START AUTO")
    parent.start_temp_ctrl_btn.clicked.disconnect()
    parent.start_temp_ctrl_btn.clicked.connect(lambda: start_control_temperature(parent))

    # TODO: gửi lệnh điều khiển đến CM4 hoặc MCU
    if hasattr(parent, "tcp_server") and parent.tcp_server:
        parent.tcp_server.send_command("temp_auto_stop")

def start_override_temperature(parent):
    """
    Xử lý khi nhấn nút START override
    """
    try:
        global_var.tec_override_voltage = int(parent.tec_override_voltage.text())
        global_var.tec_override_interval = float(parent.tec_override_interval.text())
    except ValueError:
        QMessageBox.warning(parent, "⚠️ Cảnh báo", "Dữ liệu nhập không hợp lệ.")
        return
    
    # Khóa ô nhập liệu
    parent.tec_override_voltage.setEnabled(False)
    parent.tec_override_interval.setEnabled(False)

    # Đổi hành vi nút thành STOP
    parent.start_temp_override_btn.setText("STOP OVERRIDE")
    parent.start_temp_override_btn.clicked.disconnect()
    parent.start_temp_override_btn.clicked.connect(lambda: stop_override_temperature(parent))

    # Gửi xuống CM4
    if hasattr(parent, "tcp_server") and parent.tcp_server:
        parent.tcp_server.send_command(
            "temp_override_start",
            tec_override_vol=global_var.tec_override_voltage,
            tec_override_interval=global_var.tec_override_interval
        )

def stop_override_temperature(parent):
    """
    Xử lý khi nhấn nút STOP override
    """
    # Mở khóa ô nhập liệu
    parent.tec_override_voltage.setEnabled(True)
    parent.tec_override_interval.setEnabled(True)

    # Đổi hành vi nút trở lại START
    parent.start_temp_override_btn.setText("START OVERRIDE")
    parent.start_temp_override_btn.clicked.disconnect()
    parent.start_temp_override_btn.clicked.connect(lambda: start_override_temperature(parent))

    # Gửi xuống CM4
    if hasattr(parent, "tcp_server") and parent.tcp_server:
        parent.tcp_server.send_command("temp_override_stop")

def update_graph(parent):
    """
    Cập nhật biểu đồ 8 NTC mỗi giây từ global_var.ntc_temp (dict có NTC0..NTC7).
    Dữ liệu được lưu thành danh sách cuộn để hiển thị biểu đồ thời gian.
    parent: instance CubeSat_Monitor
    """
    # Khởi tạo vùng lưu dữ liệu nếu chưa có
    if not hasattr(parent, "ntc_data_history"):
        parent.ntc_data_history = {f"NTC{i}": [] for i in range(8)}
        parent.x_data = []
        parent.index = 0

    # Lấy dữ liệu hiện tại từ global_var
    ntc_now = getattr(global_var, "ntc_temp", {})
    if not isinstance(ntc_now, dict) or not ntc_now:
        return

    # Mỗi lần update_graph (1s), thêm giá trị mới vào lịch sử
    for i in range(8):
        key = f"NTC{i}"
        try:
            val = float(ntc_now.get(key, 0.0))
        except (TypeError, ValueError):
            val = 0.0
        parent.ntc_data_history[key].append(val)
        parent.ntc_data_history[key] = parent.ntc_data_history[key][-120:]  # giữ 120 điểm (2 phút nếu 1 Hz)

    # Cập nhật trục x (thời gian hoặc điểm)
    parent.index += 1
    parent.x_data.append(parent.index)
    parent.x_data = parent.x_data[-120:]

    # Cập nhật từng đường đồ thị
    for i in range(8):
        y = parent.ntc_data_history[f"NTC{i}"]
        x_for_y = parent.x_data[-len(y):]
        try:
            parent.curves[i].setData(x_for_y, y)
        except Exception:
            pass

        # Cập nhật label nhiệt độ
        try:
            if y:
                parent.temp_labels[i].setText(f"NTC{i}: {y[-1]:.2f} °C")
            else:
                parent.temp_labels[i].setText(f"NTC{i}: -- °C")
        except Exception:
            pass
