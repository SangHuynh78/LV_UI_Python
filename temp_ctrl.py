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
    temp_show_group = QGroupBox("🌡️ Temperature monitor")
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

    parent.start_temp_ctrl_btn = QPushButton("START")
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

    # Kiểm tra giới hạn...
    # (giữ nguyên như trước)

    parent.log_box.append("[🌡️] Bắt đầu điều khiển nhiệt độ.")
    parent.start_temp_ctrl_btn.setText("STOP")
    parent.start_temp_ctrl_btn.clicked.disconnect()
    parent.start_temp_ctrl_btn.clicked.connect(lambda: stop_control_temperature(parent))

    # Gửi lệnh TCP
    if hasattr(parent, "tcp_server") and parent.tcp_server:
        parent.tcp_server.send_command(
            "auto_temp_start",
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
    parent.start_temp_ctrl_btn.setText("START")

    # Đổi hành vi nút trở lại START
    parent.start_temp_ctrl_btn.clicked.disconnect()
    parent.start_temp_ctrl_btn.clicked.connect(lambda: start_control_temperature(parent))

    # TODO: gửi lệnh điều khiển đến CM4 hoặc MCU
    if hasattr(parent, "tcp_server") and parent.tcp_server:
        parent.tcp_server.send_command("auto_temp_stop")

def update_graph(parent):
    """
    Cập nhật biểu đồ 8 NTC từ data_queue.
    parent: instance CubeSat_Monitor
    """
    # if global_var.tcp_connected == True:
    #     print("trêu")
    # if global_var.tcp_connected == False:
    #     print("đùa")
    updated = False
    while True:
        try:
            msg = parent.data_queue.get_nowait()
        except queue.Empty:
            break

        if isinstance(msg, dict):
            # meta message: connection info
            if "__meta__" in msg:
                meta = msg.get("__meta__")
                if meta == "conn_error":
                    parent.log_box.append(f"[!] Kết nối lỗi: {msg.get('error')}")
                    parent.conn_status.setText("❌ Kết nối lỗi")
                elif meta == "connected":
                    parent.conn_status.setText("✅ Đã kết nối")
                continue

            temps = msg.get("temps")
            if temps and isinstance(temps, (list, tuple)):
                for i in range(8):
                    val = temps[i] if i < len(temps) else 0
                    global_var.ntc_temp[i].append(float(val))
                    global_var.ntc_temp[i] = global_var.ntc_temp[i][-120:]
            else:
                if "temp" in msg:
                    t = float(msg["temp"])
                    global_var.ntc_temp[0].append(t)
                    global_var.ntc_temp[0] = global_var.ntc_temp[0][-120:]
            updated = True

    if updated:
        if not hasattr(parent, "x_data") or parent.x_data is None:
            parent.x_data = []
        parent.index += 1
        parent.x_data.append(parent.index)
        x_slice = parent.x_data[-120:]

        for i in range(8):
            y = global_var.ntc_temp[i][-120:] if global_var.ntc_temp[i] else []
            parent.curves[i].setData(x_slice[-len(y):], y)
            try:
                parent.temp_labels[i].setText(f"NTC{i+1}: {y[-1]:.2f} °C")
            except Exception:
                pass