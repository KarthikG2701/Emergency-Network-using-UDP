from socket import *

serverName = '10.0.0.1' 
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)

# Timeout required to bypass initial SDN packet-in drop
clientSocket.settimeout(2.0)

# Prompt the user for a custom registration message
registration_message = input("Enter your custom registration message: ")
print(f"Attempting to register with server at {serverName}:{serverPort}...")

while True:
    try:
        clientSocket.sendto(registration_message.encode(), (serverName, serverPort))
        response, serverAddress = clientSocket.recvfrom(2048)
        print(f"Server Response: {response.decode()}")
        break 
    except timeout:
        print("Registration packet lost or delayed by SDN. Retrying...")

clientSocket.settimeout(None)
print("Registration successful. Listening for emergency alerts...")

while True:
    try:
        alert_data, serverAddress = clientSocket.recvfrom(2048)
        
        print("\n" + "="*50)
        print("!!! EMERGENCY ALERT RECEIVED !!!")
        print(f"Message: {alert_data.decode()}")
        print("="*50 + "\n")
        
    except KeyboardInterrupt:
        print("\nClient shutting down.")
        break
    except Exception as e:
        print(f"An error occurred: {e}")
        break

clientSocket.close()
