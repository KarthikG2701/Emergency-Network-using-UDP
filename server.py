import socket

HOST = '127.0.0.1'
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST,PORT))

registered_client = set()

print(f"[*] Emergency UDP server started on { HOST}:{PORT}")
print("[*] waiting  for  incoming  emergency alerts...\n")

try:
  while True:
    data, client_address = server_socket.recvfrom(1024)
    message = data.decode('utf-8').strip()

    if message == "REGISTER":
         registered_client.add(client_address)
         print(f"[REGISTER] new client added : {client_address}")
         response = "ACK: Registration successful!"
         server_socket.sendto(response.encode('utf-8'), client_address)


    elif message.startswith("ALERT"):
         print(f"[ALERT RECEIVED] from {client_address}: {message}")
         response = "ACK: Emergency alert  received!"
         server_socket.sendto(response.encode('utf-8'), client_address)

    else:
         response = "ERR: Unkown command"
         srver_socket.sendto(response.encode('utf-8'),  client_address)

except KeyboardInterrupt:
   print("\n[-] shutting down server...")
finally:
   server_socket.close()

