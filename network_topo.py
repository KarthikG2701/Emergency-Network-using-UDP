from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import time
import os

def run_emergency_network():
    net = Mininet(controller=RemoteController, switch=OVSSwitch)

    info('*** Adding Ryu Remote Controller (Port 6653)\n')
    net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)

    info('*** Adding OpenFlow 1.3 Switch and Hosts\n')
    s1 = net.addSwitch('s1', protocols='OpenFlow13')
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')

    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)

    info('*** Starting Network\n')
    net.start()
    time.sleep(2)

    info('*** Connecting Host OS directly to Mininet via s1 (No socat needed)\n')
    os.system('ip addr add 10.0.0.254/24 dev s1 2>/dev/null')
    os.system('ip link set s1 up')

    info('*** Pre-populating ARP & Flow tables via pingAll\n')
    net.pingAll()

    info('*** Starting Server, Clients, and Web UI in Background\n')
    h1.cmd('python3 -u server.py > server.log 2>&1 &')
    time.sleep(1)

    h2.cmd('echo "REGISTER_H2" | python3 -u client.py > h2_client.log 2>&1 &')
    h3.cmd('echo "REGISTER_H3" | python3 -u client.py > h3_client.log 2>&1 &')
    time.sleep(1)

    python_bin = './venv/bin/python3' if os.path.exists('./venv/bin/python3') else 'python3'
    h1.cmd(f'{python_bin} -u app.py > ui.log 2>&1 &')
    time.sleep(1)

    info('\n' + '=' * 60 + '\n')
    info('  DASHBOARD LIVE AT: http://10.0.0.1:8080\n')
    info('  (Open http://10.0.0.1:8080 in your normal desktop browser)\n')
    info('=' * 60 + '\n\n')

    CLI(net)

    info('*** Stopping background services...\n')
    h1.cmd('pkill -f server.py')
    h1.cmd('pkill -f app.py')
    h2.cmd('pkill -f client.py')
    h3.cmd('pkill -f client.py')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run_emergency_network()
