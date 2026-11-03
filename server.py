import socket

HOST, PORT = '127.0.0.1', 5000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))

registered_clients = set()
print(f"[*] Emergency UDP server listening on {HOST}:{PORT}")

try:
    while True:
        data, addr = server_socket.recvfrom(1024)
        msg = data.decode('utf-8').strip()

        if msg == "REGISTER":
            registered_clients.add(addr)
            print(f"[+] Client registered from {addr}. Total clients: {len(registered_clients)}")
            server_socket.sendto(b"ACK: Registration successful!", addr)
        elif msg.startswith("ALERT:"):
            print(f"[!] Received alert from {addr}: {msg}")
            server_socket.sendto(b"ACK: Emergency alert received!", addr)
            # Forward the alert to all other registered clients
            for client in registered_clients:
                if client != addr:
                    server_socket.sendto(msg.encode('utf-8'), client)
except KeyboardInterrupt:
    print("\n[-] Shutting down server...")
finally:
    server_socket.close()
