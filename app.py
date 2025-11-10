# app.py

import sys
from PyQt5.QtWidgets import QApplication
from main_window import CubeSat_Monitor
from PyQt5.QtCore import Qt

# CubeSat_App/
# │
# ├── app.py                 # ✅ file khởi động chính
# ├── main_window.py         # ✅ chứa class CubeSat_Monitor (UI chính)
# ├── ssh_handler.py         # ✅ quản lý SSH (connect, disconnect, đọc dữ liệu)
# ├── exp_manual.py          # ✅ tạo manual_box 6x6 và xử lý click
# ├── exp_auto.py           # ✅ tạo manual_box 6x6 và xử lý click
# ├── temp_ctrl.py          # ✅ tạo manual_box 6x6 và xử lý click
# ├── global_var.py          # ✅ tạo manual_box 6x6 và xử lý click
# ├── img/
# │   └── S_logo.png
# └── __init__.py            # (tùy chọn)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CubeSat_Monitor()
    # window.show()
    window.showMaximized()
    sys.exit(app.exec_())
