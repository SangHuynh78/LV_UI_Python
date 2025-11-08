import paramiko
import threading

import global_var

class SSHHandler:
    def __init__(self, log_callback):
        self.ssh = None
        self.stdout = None
        self.log = log_callback

    def connect(self, host, user, password, script):
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(host, username=user, password=password, timeout=5)
            self.log(f"[+] Đã kết nối tới {host}")
            self.stdin, self.stdout, _ = self.ssh.exec_command(f"python3 {script}", get_pty=True)
            threading.Thread(target=self.read_remote_output, daemon=True).start()
        except Exception as e:
            self.log(f"[!] Lỗi SSH: {e}")

    def read_remote_output(self):
        for line in iter(self.stdout.readline, ""):
            try:
                temp = float(line.strip())
                self.latest_temp = temp
                self.log(f"NTC1: {temp:.2f} °C")
            except ValueError:
                continue

    def update_temps(self, x_data, ntc_temp, curves, labels):
        if not hasattr(self, "latest_temp"):
            return
        idx = len(x_data) + 1
        x_data.append(idx)
        for i in range(8):
            ntc_temp[i].append(self.latest_temp if i == 0 else 0)
            ntc_temp[i] = ntc_temp[i][-120:]
            curves[i].setData(x_data[-120:], ntc_temp[i])
            labels[i].setText(f"NTC{i+1}: {ntc_temp[i][-1]:.2f} °C")
            # labels[7].setText(f"DAC: {global_var.dac_value} °C")

    def disconnect(self):
        if self.ssh:
            self.ssh.close()
            self.log("[!] SSH disconnected.")
