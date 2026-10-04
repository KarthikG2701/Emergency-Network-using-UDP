import socket

HOST = '127.0.0.1'
PORT = 5000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(5.0)



try:
    print(f"[*] Registering ...")
    client_socket.sendto("REGISTER".encode('utf-8'), (HOST,PORT))
    response, _ = client_socket.recvefrom(1024)
    print(f"[SERVER RESPONSE] {response.decode('utf-8')}")

 
    print("[*] Sending Emergency Alert...")
    client_socket.sendto("ALERT: Fire in  Building A!".encode('utf-8'),(HOST,PORT))
    response, _ = client_socket.recvfrom(1024)
    print(f"[SERVER RESPONSE] {response.decode('utf-8')}")

except  Exception as e:
   print(f"[!] Error: {e}")
finally:
   client_socket.close()



