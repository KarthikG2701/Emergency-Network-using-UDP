import socket
import threading
import time

HOST, PORT = '127.0.0.1', 5000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def receive_messages():
    while True:
        try:
            data, _ = client_socket.recvfrom(1024)
            recv_time = time.time()
            msg = data.decode('utf-8')

            if "::" in msg:
                alert_text, send_time = msg.rsplit("::", 1)
                latency_ms = (recv_time - float(send_time)) * 1000
                print(f"\n[BROADCAST RECEIVED] {alert_text} | Latency: {latency_ms:.2f} ms\n> ", end="")
            else:
                print(f"\n[SERVER] {msg}\n> ", end="")
        except:
            break

try:
    print("[*] Registering with server...")
    client_socket.sendto(b"REGISTER", (HOST, PORT))
    resp, _ = client_socket.recvfrom(1024)
    print(f"[SERVER RESPONSE] {resp.decode('utf-8')}")

    threading.Thread(target=receive_messages, daemon=True).start()

    print("\n[*] Enter alert text (or 'exit' to quit):")
    while True:
        msg = input("> ")
        if msg.lower() == 'exit':
            break
        if msg.strip():
            payload = f"ALERT: {msg}::{time.time()}"
            client_socket.sendto(payload.encode('utf-8'), (HOST, PORT))

except Exception as e:
    print(f"[!] Error: {e}")
finally:
    client_socket.close()
