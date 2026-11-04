from flask import Flask, render_template_string, request, jsonify
import socket
import random
import threading
import time

app = Flask(__name__)

SERVER_IP = '10.0.0.1'
SERVER_PORT = 5000

traffic_logs = []
generator_active = False
emergency_state = {"active": False, "last_message": "None", "timestamp": ""}
packet_counter = 0
counter_lock = threading.Lock()

UI_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SDN Emergency Network & Priority Telemetry</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-dark: #0f172a;
            --card-bg: #1e293b;
            --border-col: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --high-red: #ef4444;
            --mod-yellow: #facc15;
            --low-green: #22c55e;
            --accent-blue: #3b82f6;
            --accent-purple: #8b5cf6;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-main);
            padding: 24px;
        }
        .dashboard { max-width: 1280px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; }
        
        /* Top Header & Emergency Banner */
        .header-bar {
            display: flex; justify-content: space-between; align-items: center;
            background: var(--card-bg); padding: 18px 24px; border-radius: 12px;
            border: 1px solid var(--border-col);
        }
        .header-title h1 { font-size: 1.4rem; font-weight: 700; display: flex; align-items: center; gap: 10px; }
        .header-title p { color: var(--text-muted); font-size: 0.85rem; margin-top: 4px; }
        
        .emergency-banner {
            padding: 10px 18px; border-radius: 8px; font-weight: 600; font-size: 0.9rem;
            background: rgba(34, 197, 94, 0.15); color: var(--low-green); border: 1px solid rgba(34, 197, 94, 0.3);
            transition: all 0.3s ease;
        }
        .emergency-banner.active {
            background: rgba(239, 68, 68, 0.2); color: #fca5a5; border: 1px solid var(--high-red);
            box-shadow: 0 0 15px rgba(239, 68, 68, 0.4);
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.65; } 100% { opacity: 1; } }

        /* KPI Metrics Row */
        .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
        .kpi-card {
            background: var(--card-bg); padding: 16px 20px; border-radius: 12px;
            border: 1px solid var(--border-col); display: flex; flex-direction: column; gap: 6px;
        }
        .kpi-label { font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
        .kpi-val { font-size: 1.65rem; font-weight: 700; }
        .val-high { color: var(--high-red); }
        .val-mod { color: var(--mod-yellow); }
        .val-low { color: var(--low-green); }

        /* Controls & Visualisation Grid */
        .main-grid { display: grid; grid-template-columns: 1fr 1.6fr; gap: 20px; }
        .card {
            background: var(--card-bg); padding: 20px; border-radius: 12px;
            border: 1px solid var(--border-col); display: flex; flex-direction: column; gap: 16px;
        }
        .card h2 { font-size: 1.05rem; font-weight: 600; color: #e2e8f0; border-bottom: 1px solid var(--border-col); padding-bottom: 10px; }

        /* Form Inputs & Buttons */
        .form-group { display: flex; flex-direction: column; gap: 8px; }
        .form-group label { font-size: 0.85rem; color: var(--text-muted); }
        input, select {
            background: #0f172a; border: 1px solid var(--border-col); color: white;
            padding: 10px 12px; border-radius: 8px; font-size: 0.95rem; outline: none;
        }
        input:focus, select:focus { border-color: var(--accent-blue); }
        
        .btn-group { display: flex; flex-direction: column; gap: 10px; margin-top: 6px; }
        button {
            padding: 11px 16px; border: none; border-radius: 8px; font-weight: 600;
            font-size: 0.9rem; cursor: pointer; transition: all 0.2s; color: white;
        }
        .btn-primary { background: var(--accent-blue); }
        .btn-primary:hover { background: #2563eb; }
        .btn-burst { background: var(--accent-purple); }
        .btn-burst:hover { background: #7c3aed; }
        .btn-gen-start { background: #10b981; }
        .btn-gen-stop { background: var(--high-red); }

        /* Latency Bar & Logs Table */
        .log-container {
            background: #0b1120; border: 1px solid var(--border-col); border-radius: 8px;
            height: 310px; overflow-y: auto; padding: 12px; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;
        }
        .log-item {
            display: grid; grid-template-columns: 95px 120px 130px 1fr; align-items: center;
            padding: 8px 10px; border-bottom: 1px solid #1e293b; border-radius: 6px; margin-bottom: 4px;
        }
        .badge {
            padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;
            display: inline-block; text-align: center; width: 95px;
        }
        .badge-high { background: rgba(239, 68, 68, 0.2); color: var(--high-red); border: 1px solid var(--high-red); }
        .badge-moderate { background: rgba(250, 204, 21, 0.15); color: var(--mod-yellow); border: 1px solid var(--mod-yellow); }
        .badge-low { background: rgba(34, 197, 94, 0.15); color: var(--low-green); border: 1px solid var(--low-green); }
        
        .row-high { border-left: 4px solid var(--high-red); background: rgba(239, 68, 68, 0.05); }
        .row-moderate { border-left: 4px solid var(--mod-yellow); background: rgba(250, 204, 21, 0.04); }
        .row-low { border-left: 4px solid var(--low-green); background: rgba(34, 197, 94, 0.04); }
        
        .chart-wrapper { position: relative; height: 260px; width: 100%; }
    </style>
</head>
<body>
<div class="dashboard">
    <div class="header-bar">
        <div class="header-title">
            <h1>📡 SDN Priority Queuing & Emergency Telemetry</h1>
            <p>Strict Priority Scheduler (High &gt; Moderate &gt; Low) | Only High Priority Triggers Emergency</p>
        </div>
        <div id="emergencyBanner" class="emergency-banner">
            🟢 SYSTEM NORMAL — NO ACTIVE EMERGENCY
        </div>
    </div>

    <div class="kpi-grid">
        <div class="kpi-card">
            <span class="kpi-label">Avg High Priority RTT (Red)</span>
            <span class="kpi-val val-high" id="avgHigh">-- ms</span>
        </div>
        <div class="kpi-card">
            <span class="kpi-label">Avg Moderate RTT (Yellow)</span>
            <span class="kpi-val val-mod" id="avgMod">-- ms</span>
        </div>
        <div class="kpi-card">
            <span class="kpi-label">Avg Low Priority RTT (Green)</span>
            <span class="kpi-val val-low" id="avgLow">-- ms</span>
        </div>
        <div class="kpi-card">
            <span class="kpi-label">Total Packets Serviced</span>
            <span class="kpi-val" id="totalPkts">0</span>
        </div>
    </div>

    <div class="main-grid">
        <div class="card">
            <h2>⚡ Dispatch & Traffic Control</h2>
            <form id="sendForm" class="form-group">
                <label>Message Payload</label>
                <input type="text" id="message" placeholder="e.g., Sector 4 sensor reading..." required>
                
                <label style="margin-top: 8px;">Traffic Priority Class</label>
                <select id="priority">
                    <option value="high">🔴 High Priority (Triggers Emergency)</option>
                    <option value="moderate" selected>🟡 Moderate Priority (Standard Warning)</option>
                    <option value="low">🟢 Low Priority (Routine Telemetry)</option>
                </select>

                <div class="btn-group">
                    <button type="submit" class="btn-primary">Send Single Packet</button>
                    <button type="button" class="btn-burst" onclick="sendBurst()">🚀 Send All 3 Priorities Simultaneously (Queue Test)</button>
                </div>
            </form>

            <h2 style="margin-top: 10px;">🎲 Random Network Traffic Mode</h2>
            <p style="font-size: 0.82rem; color: var(--text-muted);">
                Continuously generates randomized multi-priority bursts to visualize queuing delay separation in real time.
            </p>
            <button id="toggleGen" class="btn-gen-start" onclick="toggleGenerator()">▶ Start Random Traffic Mode</button>
        </div>

        <div class="card">
            <h2>📈 Real-Time Latency Visualization (ms)</h2>
            <div class="chart-wrapper">
                <canvas id="latencyChart"></canvas>
            </div>
        </div>
    </div>

    <div class="card">
        <h2>📋 Live Priority Service Log (Ordered by Server Completion)</h2>
        <div class="log-container" id="logBox"></div>
    </div>
</div>

<script>
    const ctx = document.getElementById('latencyChart').getContext('2d');
    const latencyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Round-Trip Latency (ms)',
                data: [],
                backgroundColor: [],
                borderColor: [],
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            scales: {
                y: { beginAtZero: true, grid: { color: '#334155' }, ticks: { color: '#94a3b8' }, title: { display: true, text: 'Latency (ms)', color: '#94a3b8' } },
                x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
            },
            plugins: { legend: { display: false } }
        }
    });

    document.getElementById('sendForm').onsubmit = async (e) => {
        e.preventDefault();
        const msg = document.getElementById('message').value;
        const pri = document.getElementById('priority').value;
        await fetch('/send', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: msg, priority: pri})
        });
        document.getElementById('message').value = '';
        refreshData();
    };

    async function sendBurst() {
        const msg = document.getElementById('message').value || "Simultaneous Queue Test";
        await fetch('/send_burst', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: msg})
        });
        refreshData();
    }

    async function toggleGenerator() {
        const res = await fetch('/toggle_generator', {method: 'POST'});
        const data = await res.json();
        const btn = document.getElementById('toggleGen');
        if (data.active) {
            btn.innerText = "⏹ Stop Random Traffic Mode";
            btn.className = "btn-gen-stop";
        } else {
            btn.innerText = "▶ Start Random Traffic Mode";
            btn.className = "btn-gen-start";
        }
    }

    async function refreshData() {
        const res = await fetch('/logs');
        const data = await res.json();
        const logs = data.logs;
        
        // Update Emergency Banner
        const banner = document.getElementById('emergencyBanner');
        if (data.emergency.active) {
            banner.className = "emergency-banner active";
            banner.innerText = `🚨 EMERGENCY ACTIVE: "${data.emergency.last_message}" (${data.emergency.timestamp})`;
        }

        // Update Logs
        const box = document.getElementById('logBox');
        box.innerHTML = logs.slice().reverse().map(l => `
            <div class="log-item row-${l.priority}">
                <span style="color:#94a3b8;">${l.timestamp}</span>
                <span class="badge badge-${l.priority}">${l.priority.toUpperCase()}</span>
                <span style="font-weight:700; color:#f8fafc;">${l.latency} ms</span>
                <span>${l.msg} ${l.emergency ? '🚨 <b>[BROADCASTED TO NODES]</b>' : ''}</span>
            </div>
        `).join('');

        // Calculate KPI Averages
        const calcAvg = (p) => {
            const nums = logs.filter(x => x.priority === p && typeof x.latency === 'number').map(x => x.latency);
            return nums.length ? (nums.reduce((a,b)=>a+b, 0) / nums.length).toFixed(1) + ' ms' : '-- ms';
        };
        document.getElementById('avgHigh').innerText = calcAvg('high');
        document.getElementById('avgMod').innerText = calcAvg('moderate');
        document.getElementById('avgLow').innerText = calcAvg('low');
        document.getElementById('totalPkts').innerText = logs.length;

        // Update Chart (last 20 packets)
        const recent = logs.slice(-20);
        latencyChart.data.labels = recent.map(l => `#${l.id} (${l.priority[0].toUpperCase()})`);
        latencyChart.data.datasets[0].data = recent.map(l => typeof l.latency === 'number' ? l.latency : 0);
        latencyChart.data.datasets[0].backgroundColor = recent.map(l => 
            l.priority === 'high' ? '#ef4444' : (l.priority === 'moderate' ? '#facc15' : '#22c55e')
        );
        latencyChart.update();
    }

    setInterval(refreshData, 600);
</script>
</body>
</html>
"""

def dispatch_udp(priority, msg):
    global packet_counter
    start_time = time.time()
    is_emergency = False

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3.0)
        payload = f"{priority.upper()}:{msg}"
        sock.sendto(payload.encode(), (SERVER_IP, SERVER_PORT))

        reply, _ = sock.recvfrom(2048)
        latency = round((time.time() - start_time) * 1000, 2)
        sock.close()

        decoded_reply = reply.decode()
        if decoded_reply.startswith("EMERGENCY_BROADCAST_SENT"):
            is_emergency = True
            emergency_state["active"] = True
            emergency_state["last_message"] = msg
            emergency_state["timestamp"] = time.strftime("%H:%M:%S")
    except Exception:
        latency = "Timeout"

    with counter_lock:
        packet_counter += 1
        pkt_id = packet_counter
        traffic_logs.append({
            "id": pkt_id,
            "timestamp": time.strftime("%H:%M:%S"),
            "priority": priority,
            "latency": latency,
            "msg": msg,
            "emergency": is_emergency
        })

@app.route('/')
def index():
    return render_template_string(UI_TEMPLATE)

@app.route('/send', methods=['POST'])
def send_single():
    data = request.json
    dispatch_udp(data.get('priority', 'moderate'), data.get('message', 'Test'))
    return jsonify({"status": "ok"})

@app.route('/send_burst', methods=['POST'])
def send_burst():
    base_msg = request.json.get('message', 'Burst Test')
    # Send Low first, Moderate second, High third within milliseconds so all 3 queue up together
    threads = [
        threading.Thread(target=dispatch_udp, args=('low', f"{base_msg} [Low]")),
        threading.Thread(target=dispatch_udp, args=('moderate', f"{base_msg} [Moderate]")),
        threading.Thread(target=dispatch_udp, args=('high', f"{base_msg} [High]"))
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return jsonify({"status": "ok"})

def random_traffic_loop():
    global generator_active
    samples = {
        'high': ["Fire alarm in Server Room", "Containment breach detected", "Power grid failure"],
        'moderate': ["High CPU load warning", "Link utilization at 80%", "Backup power engaged"],
        'low': ["Routine ping check", "Temperature sensor 22C", "Daily log sync"]
    }
    while generator_active:
        # Dispatch small random multi-priority bursts so queuing priority is visible
        burst_size = random.choice([2, 3])
        threads = []
        for _ in range(burst_size):
            pri = random.choices(['high', 'moderate', 'low'], weights=[0.2, 0.4, 0.4])[0]
            msg = f"[Random] {random.choice(samples[pri])}"
            threads.append(threading.Thread(target=dispatch_udp, args=(pri, msg)))
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        time.sleep(random.uniform(0.8, 1.5))

@app.route('/toggle_generator', methods=['POST'])
def toggle_generator():
    global generator_active
    generator_active = not generator_active
    if generator_active:
        threading.Thread(target=random_traffic_loop, daemon=True).start()
    return jsonify({"active": generator_active})

@app.route('/logs')
def get_logs():
    return jsonify({
        "logs": traffic_logs[-60:],
        "emergency": emergency_state
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
