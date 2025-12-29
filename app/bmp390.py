from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QLabel

def create_bmp390_show_box(parent):
    group = QGroupBox("📊 BMP390")
    layout = QVBoxLayout()

    # Create labels for temperature and pressure

    parent.bmp390_temp_label = QLabel("Temperature: 0.0 °C")
    parent.bmp390_press_label = QLabel("Pressure: 0.0 hPa")

    layout.addWidget(parent.bmp390_temp_label)
    layout.addWidget(parent.bmp390_press_label)

    group.setLayout(layout)
    return group

def update_bmp390_ui(parent, temp, press):
    parent.bmp390_temp_label.setText(f"Temperature: {temp:.2f} °C")
    parent.bmp390_press_label.setText(f"Pressure: {press:.2f} hPa")