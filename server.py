import socket
import threading
import queue
import time

SERVER_IP = '10.0.0.1'
SERVER_PORT = 5000

# Separate FIFO queues for each priority class
high_q = queue.Queue()
mod_q = queue.Queue()
low_q = queue.Queue()

subscribers = set()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
print(f"[*] Strict Priority UDP Server listening on {SERVER_IP}:{SERVER_PORT}")

def priority_scheduler():
    """Services High -> Moderate -> Low in strict priority order."""
    while True:
        item = None
        priority_level = None

        # Always check High priority first, then Moderate, then Low
        if not high_q.empty():
            item = high_q.get()
            priority_level = "HIGH"
        elif not mod_q.empty():
            item = mod_q.get()
            priority_level = "MODERATE"
        elif not low_q.empty():
            item = low_q.get()
            priority_level = "LOW"
        else:
            time.sleep(0.005)
            continue

        addr, msg, arrival_time = item

        # Simulated transmission/service time (60ms) so queuing delay is clearly measurable
        time.sleep(0.06)

        # ONLY High Priority triggers an emergency broadcast to subscribers (h2, h3)
        if priority_level == "HIGH":
            alert_banner = f"🚨 [EMERGENCY DECLARED]: {msg}"
            print(f"\n[!!!] HIGH PRIORITY EMERGENCY TRIGGERED BY {addr}: {msg}")
            for sub in list(subscribers):
                try:
                    server_socket.sendto(alert_banner.encode(), sub)
                except Exception as e:
                    print(f"Failed to alert subscriber {sub}: {e}")
            ack_reply = f"EMERGENCY_BROADCAST_SENT|{priority_level}|{msg}"
        else:
            print(f"[*] Serviced [{priority_level}] request from {addr}: {msg}")
            ack_reply = f"NORMAL_ACK|{priority_level}|{msg}"

        # Send reply back to sender so it can calculate total RTT latency
        server_socket.sendto(ack_reply.encode(), addr)

# Start background scheduler thread
threading.Thread(target=priority_scheduler, daemon=True).start()

while True:
    try:
        data, addr = server_socket.recvfrom(2048)
        text = data.decode().strip()

        # Handle subscriber registrations from h2 and h3 client.py scripts
        if text.startswith("REGISTER") or ":" not in text:
            subscribers.add(addr)
            print(f"[+] Registered Subscriber Node: {addr} (Total: {len(subscribers)})")
            server_socket.sendto(b"Registered successfully with Emergency Server.", addr)
            continue

        # Parse PRIORITY:MESSAGE from UI traffic
        pri, msg = text.split(":", 1)
        pri = pri.strip().upper()

        # Small batching window (15ms) so simultaneous burst packets enter queues before scheduler pulls
        if pri == "HIGH":
            high_q.put((addr, msg, time.time()))
        elif pri == "MODERATE":
            mod_q.put((addr, msg, time.time()))
        else:
            low_q.put((addr, msg, time.time()))

    except Exception as e:
        print(f"Server error: {e}")
