from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QLabel

def create_aht20_show_box(parent):
    group = QGroupBox("📊 AHT20")
    layout = QVBoxLayout()

    # Create labels for temperature and humidity

    parent.aht20_temp_label = QLabel("Temperature: 0.0 °C")
    parent.aht20_hum_label = QLabel("Humidity: 0.0 %")

    layout.addWidget(parent.aht20_temp_label)
    layout.addWidget(parent.aht20_hum_label)

    group.setLayout(layout)
    return group

def update_aht20_ui(parent, temp, hum):
    parent.aht20_temp_label.setText(f"Temperature: {temp:.2f} °C")
    parent.aht20_hum_label.setText(f"Humidity: {hum:.2f} %")