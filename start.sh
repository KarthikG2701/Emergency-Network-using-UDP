#!/bin/bash
echo "[1/4] Cleaning up previous Mininet & Python processes..."
sudo mn -c > /dev/null 2>&1
sudo pkill -f ryu-manager
sudo pkill -f server.py
sudo pkill -f client.py
sudo pkill -f app.py

echo "[2/4] Ensuring Flask virtual environment is ready..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    ./venv/bin/pip install Flask > /dev/null 2>&1
fi

echo "[3/4] Starting Ryu SDN Controller in the background..."
source ~/Downloads/ryu_env/bin/activate
nohup ryu-manager emergency_controller.py > ryu.log 2>&1 &
deactivate
sleep 2

echo "[4/4] Launching Mininet Topology & Web UI..."
sudo python3 network_topo.py
