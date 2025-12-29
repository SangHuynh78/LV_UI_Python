import socket
import threading

def handle_client(conn, addr):
    print(f"[+] Client connected: {addr}")
    while True:
        cmd = input("Nhập lệnh để gửi tới client: ")
        if cmd.lower() == "exit":
            conn.sendall(b"exit")
            break
        conn.sendall(cmd.encode())
    conn.close()

# Tạo socket server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 5555))
server.listen(5)
print("[*] Server đang lắng nghe...")

while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()