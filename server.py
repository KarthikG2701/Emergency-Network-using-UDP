from socket import *

serverIP = '10.0.0.1'
serverPort = 12000

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((serverIP, serverPort))

subscribers = set()

print(f"Emergency Notification Server started on {serverIP}:{serverPort}")
print("Waiting for 2 subscribers to register...")

while True:
    try:
        message, clientAddress = serverSocket.recvfrom(2048)
        decoded_msg = message.decode()
        
        # Accept the custom message and register the new client
        if clientAddress not in subscribers:
            subscribers.add(clientAddress)
            print(f"\n[+] New subscriber registered: {clientAddress}")
            print(f"[+] Client Message: {decoded_msg}")
            
            # Send confirmation back to unblock the client's timeout loop
            confirmation = "Registration Confirmed."
            serverSocket.sendto(confirmation.encode(), clientAddress)
            
            # Auto-Broadcast once both h2 and h3 connect
            if len(subscribers) == 2:
                print("\n[!] 2 Subscribers detected. Broadcasting emergency alert...")
                alert_payload = "CRITICAL: Facility breach detected. Evacuate immediately!"
                for sub in subscribers:
                    serverSocket.sendto(alert_payload.encode(), sub)
                
                # Clear the set so it doesn't endlessly broadcast if clients send more data
                subscribers.clear()
            
    except KeyboardInterrupt:
        print("\nShutting down server...")
        break
    except Exception as e:
        print(f"\nSocket error: {e}")

serverSocket.close()
