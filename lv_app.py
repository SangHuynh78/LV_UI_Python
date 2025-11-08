import sys
import paramiko
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox, QMessageBox, QTextEdit
)
from PyQt5.QtCore import QTimer, Qt
import pyqtgraph as pg
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QIcon

# ---------- Cấu hình mặc định ----------
DEFAULT_HOST = "192.168.1.11"
DEFAULT_USER = "spec_cam"
DEFAULT_PASS = "cam"
DEFAULT_SCRIPT = "/home/spec_cam/SangHuynh_Dev/sang_temp.py"

class CubeSat_Monitor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("img/S_logo.png"))
        self.setWindowTitle("CubeSat System")
        self.resize(1920, 1080)

        # --- Dữ liệu nhiệt độ ---
        self.x_data = []
        self.ntc_temp = [[] for _ in range(8)]
        self.index = 0
        self.curves = []

        # --- Bố cục chính ---
        main_layout = QHBoxLayout(self)
        col1_layout = QVBoxLayout()
        col2_layout = QVBoxLayout()
        col3_layout = QVBoxLayout()
        main_layout.addLayout(col1_layout, 1)
        main_layout.addLayout(col2_layout, 3)
        main_layout.addLayout(col3_layout, 1)

        # ========= CỘT 1 =========
        # --- Hàng 1: Nhiệt độ hiện tại ---
        temp_group = QGroupBox("🌡️ Nhiệt độ Hiện tại")
        temp_layout = QHBoxLayout()
        temp_group_sub1 = QVBoxLayout()
        temp_group_sub2 = QVBoxLayout()
        
        self.temp_labels = []
        for i in range(4):
            label = QLabel(f"NTC{i+1}: {self.ntc_temp[i]} °C")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 16px;")
            self.temp_labels.append(label)
            temp_group_sub1.addWidget(label)

        for i in range(4, 8):
            label = QLabel(f"NTC{i+1}: {self.ntc_temp[i]} °C")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 16px;")
            self.temp_labels.append(label)
            temp_group_sub2.addWidget(label)

        temp_layout.addLayout(temp_group_sub1)
        temp_layout.addLayout(temp_group_sub2)
        temp_group.setLayout(temp_layout)

        # --- Hàng 2: Log trạng thái ---
        log_group = QGroupBox("📝 Log / Trạng thái")
        log_layout = QVBoxLayout()
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        log_layout.addWidget(self.log_box)
        log_group.setLayout(log_layout)

        # Thêm 2 groupbox vào cột 1
        col1_layout.addWidget(temp_group, 1)
        col1_layout.addWidget(log_group, 4)

        # ========= CỘT 2 =========
        # --- Hàng 1: Biểu đồ nhiệt độ ---
        graph_group = QGroupBox("📊 Biểu đồ nhiệt độ 8 NTC")
        graph_layout = QVBoxLayout()
        self.graph = pg.PlotWidget(title="Nhiệt độ 8 NTC theo thời gian (°C)")
        self.graph.showGrid(x=True, y=True)
        self.graph.setLabel('left', 'Nhiệt độ (°C)')
        self.graph.setLabel('bottom', 'Thời gian (chu kỳ)')
        self.graph.addLegend(offset=(10, 10))
        graph_layout.addWidget(self.graph)
        graph_group.setLayout(graph_layout)

        # --- Hàng 2: Điều khiển thí nghiệm ---
        exp_control_group = QGroupBox("🛠️ Điều khiển thí nghiệm")
        exp_control_layout = QVBoxLayout()
        self.start_exp_btn = QPushButton("Bắt đầu thí nghiệm")
        self.stop_exp_btn = QPushButton("Dừng thí nghiệm")
        exp_control_group.setLayout(exp_control_layout)

        # --- Hàng 2.1: Chế độ điều khiển ---
        menu_exp_group = QGroupBox()
        menu_exp_layout = QHBoxLayout()

        # Dùng RadioButton cho trực quan
        from PyQt5.QtWidgets import QRadioButton
        self.manual_radio = QRadioButton("Manual Mode")
        self.auto_radio = QRadioButton("Auto Mode")

        self.manual_radio.setChecked(True)  # Mặc định Manual
        self.manual_radio.toggled.connect(self.switch_mode)


        menu_exp_layout.addWidget(self.manual_radio)
        menu_exp_layout.addWidget(self.auto_radio)
        menu_exp_group.setLayout(menu_exp_layout)

        # Thêm menu_exp vào layout exp_control_layout
        exp_control_layout.addWidget(menu_exp_group, 1)

        # --- Hàng 2.2: Manual Mode Box ---
        self.manual_box = QGroupBox("🧭 Manual Control")
        manual_layout = QVBoxLayout()
        grid_layout = QGridLayout()
        self.manual_buttons = []  # Lưu danh sách nút để quản lý trạng thái
        for i in range(6):
            for j in range(6):
                idx = i * 6 + j + 1
                btn = QPushButton(str(idx))
                btn.setFixedSize(60, 60)
                btn.setCheckable(True)  # Cho phép toggle ON/OFF
                btn.setStyleSheet("""
                    QPushButton {
                        border-radius: 30px;
                        border: 2px solid black;
                        background-color: white;
                        color: black;
                        font-weight: bold;
                        font-size: 14px;
                    }
                    QPushButton:checked {
                        background-color: #45a049;
                        border: 2px solid black;
                        color: white;
                    }
                """)
                btn.clicked.connect(lambda _, pos=idx, b=btn: self.manual_exp_with_pos(pos, b))
                self.manual_buttons.append(btn)
                grid_layout.addWidget(btn, i, j)
        manual_layout.addLayout(grid_layout)
        self.manual_box.setLayout(manual_layout)

        # --- Hàng 2.3: Auto Mode Box ---
        self.auto_box = QGroupBox("🤖 Auto Control")
        auto_layout = QVBoxLayout()
        auto_layout.addWidget(QPushButton("Chạy chu trình thí nghiệm"))
        auto_layout.addWidget(QPushButton("Dừng chu trình"))
        self.auto_box.setLayout(auto_layout)

        # Mặc định ẩn Auto Box
        self.auto_box.hide()

        # Thêm 2 box vào layout vào exp_control_group
        exp_control_layout.addWidget(self.manual_box, 8)
        exp_control_layout.addWidget(self.auto_box, 8)

        # Thêm 2 groupbox vào cột 2
        col2_layout.addWidget(graph_group, 2)
        col2_layout.addWidget(exp_control_group, 3)

        # ========= CỘT 3 =========
        # --- Hàng 1: Kết nối SSH ---
        conn_group = QGroupBox("🔌 Kết nối SSH")
        conn_layout = QVBoxLayout()
        self.host_input = QLineEdit(DEFAULT_HOST)
        self.user_input = QLineEdit(DEFAULT_USER)
        self.pass_input = QLineEdit(DEFAULT_PASS)
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.script_input = QLineEdit(DEFAULT_SCRIPT)

        conn_layout.addWidget(QLabel("Host IP:"))
        conn_layout.addWidget(self.host_input)
        conn_layout.addWidget(QLabel("Username:"))
        conn_layout.addWidget(self.user_input)
        conn_layout.addWidget(QLabel("Password:"))
        conn_layout.addWidget(self.pass_input)
        # conn_layout.addWidget(QLabel("Đường dẫn script trên CM4:"))
        # conn_layout.addWidget(self.script_input)

        self.connect_btn = QPushButton("Connect SSH")
        self.connect_btn.clicked.connect(self.connect_ssh)
        conn_layout.addWidget(self.connect_btn)

        self.status_label = QLabel("⏳ Chưa kết nối.")
        conn_layout.addWidget(self.status_label)
        conn_group.setLayout(conn_layout)

        # --- Hàng 2: hiển thị hình ảnh ---
        image_group = QGroupBox("📷 Hình ảnh hệ thống")
        image_layout = QVBoxLayout()

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        # Tải ảnh từ file
        pixmap = QPixmap("img/S_logo.png")

        # Thu nhỏ ảnh cho vừa khung hiển thị
        pixmap = pixmap.scaled(500, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.image_label.setPixmap(pixmap)
        image_layout.addWidget(self.image_label)

        image_group.setLayout(image_layout)

        # Thêm 2 groupbox vào cột 3
        col3_layout.addWidget(conn_group, 2)
        col3_layout.addWidget(image_group, 4)

        for i in range(8):
            color = pg.intColor(i, 8)
            curve = self.graph.plot(pen=pg.mkPen(color=color, width=2), name=f"NTC{i+1}")
            self.curves.append(curve)

        # --- Biến SSH ---
        self.ssh = None
        self.stdout = None

        # --- Timer cập nhật ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_graph)

    def connect_ssh(self):
        host = self.host_input.text().strip()
        user = self.user_input.text().strip()
        password = self.pass_input.text().strip()
        script = self.script_input.text().strip()

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.ssh.connect(host, username=user, password=password, timeout=5)
            self.status_label.setText(f"✅ Đã kết nối tới {host}")
            self.log_box.append(f"[+] Đã kết nối tới {host}")

            # ✅ Chạy script trên CM4
            self.stdin, self.stdout, self.stderr = self.ssh.exec_command(f"python3 {script}", get_pty=True)
            self.thread = threading.Thread(target=self.read_remote_output, daemon=True)
            self.thread.start()
            self.timer.start(500)

            # ✅ Đổi nút thành Disconnect
            self.connect_btn.setText("Disconnect SSH")
            self.connect_btn.clicked.disconnect()          # Hủy kết nối sự kiện cũ
            self.connect_btn.clicked.connect(self.disconnect_ssh)

        except Exception as e:
            QMessageBox.critical(self, "Lỗi SSH", f"Không thể kết nối:\n{e}")
            self.status_label.setText("❌ Lỗi kết nối SSH.")
            self.log_box.append(f"[!] Lỗi kết nối: {e}")
            return
    
    def disconnect_ssh(self):
        """Ngắt kết nối SSH và khôi phục nút."""
        try:
            if self.ssh:
                self.ssh.close()
                self.ssh = None
                self.status_label.setText("🔌 Đã ngắt kết nối SSH.")
                self.log_box.append("[!] SSH disconnected.")

                # ✅ Đổi nút về Connect
                self.connect_btn.setText("Connect SSH")
                self.connect_btn.clicked.disconnect()
                self.connect_btn.clicked.connect(self.connect_ssh)

                self.timer.stop()

        except Exception as e:
            self.log_box.append(f"[!] Lỗi ngắt kết nối: {e}")

    def switch_mode(self):
        """Chuyển hiển thị giữa Manual và Auto box"""
        if self.manual_radio.isChecked():
            self.manual_box.show()
            self.auto_box.hide()
            self.log_box.append("[⚙️] Chuyển sang chế độ MANUAL.")
        else:
            self.manual_box.hide()
            self.auto_box.show()
            self.log_box.append("[⚙️] Chuyển sang chế độ AUTO.")


    def manual_exp_with_pos(self, idx: int, button: QPushButton):
        """Xử lý khi click nút manual vị trí idx"""
        if button.isChecked():
            self.log_box.append(f"[🧭] Bật thí nghiệm tại vị trí {idx}")
        else:
            self.log_box.append(f"[🧭] Tắt thí nghiệm tại vị trí {idx}")
        print(f"Manual experiment toggle: {idx}, state={button.isChecked()}")
        # 👉 Ở đây bạn có thể gửi lệnh điều khiển thực tế qua SSH nếu cần


    def read_remote_output(self):
        for line in iter(self.stdout.readline, ""):
            try:
                temp = float(line.strip())
                self.latest_temp = temp  # ✅ cập nhật giá trị mới nhất
                self.index += 1
                self.x_data.append(self.index)

                # Chỉ NTC1 có giá trị thật, các NTC khác = 0
                for i in range(8):
                    if i == 0:
                        self.ntc_temp[i].append(temp)
                    else:
                        self.ntc_temp[i].append(i)

                    if len(self.ntc_temp[i]) > 120:
                        self.ntc_temp[i] = self.ntc_temp[i][-120:]
                if len(self.x_data) > 120:
                    self.x_data = self.x_data[-120:]

                self.log_box.append(f"NTC1: {temp:.2f} °C")
            except ValueError:
                continue

    def update_graph(self):
        """Cập nhật biểu đồ và nhãn nhiệt độ."""
        for i in range(8):
            if self.ntc_temp[i]:
                self.curves[i].setData(self.x_data, self.ntc_temp[i])

        # ✅ Hiển thị giá trị thật của NTC1 trên nhãn và trạng thái
        self.temp_labels[0].setText(f"NTC1: {self.ntc_temp[0][-1]:.2f} °C")
        for i in range(1, 8):
            self.temp_labels[i].setText(f"NTC{i+1}: {self.ntc_temp[i][-1]:.2f} °C")

    def closeEvent(self, event):
        self.timer.stop()
        try:
            if self.ssh:
                self.ssh.close()
        except:
            pass
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CubeSat_Monitor()
    window.show()
    sys.exit(app.exec_())
