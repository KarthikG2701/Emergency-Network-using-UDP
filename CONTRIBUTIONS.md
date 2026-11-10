CONTRIBUTIONS:

🔹 Deliverable 1: Core SDN & Socket Foundation
Akshata — UDP Socket Programming & Baseline Latency

Designed and implemented the core connectionless UDP client-server communication architecture (server.py and client.py).   


Built the subscriber registration mechanism allowing virtual hosts (h2, h3) to register with the central emergency server on h1 (10.0.0.1:5000).

Implemented initial packet timestamping and baseline end-to-end latency measurement.

B Raghavendra — Mininet Data Plane & Ryu SDN Control Plane

Designed the custom Software-Defined Networking (SDN) topology (network_topo.py) using Mininet and Open vSwitch (s1).

Implemented the Ryu SDN controller (emergency_controller.py) to manage control-plane flow tables and Layer-2/Layer-3 packet forwarding.

Configured virtual host IP addressing (10.0.0.1/24 – 10.0.0.3/24), link provisioning, and switch-to-controller handshakes over TCP port 6653.

Karthik Ganesh — System Integration, Architecture & Flow Design

Integrated the UDP socket application layer with the underlying Mininet SDN data plane and Ryu controller so end-to-end traffic flowed seamlessly across virtual hosts.

Resolved cross-layer reachability and ARP/flow-table initialization between hosts.

Authored the system architecture diagrams, packet flow sequences, and technical documentation for Deliverable 1.

🚀 Deliverable 2: Priority Telemetry, Web UI & Network Automation
To build upon the Deliverable 1 foundation, the new enhancements were split into three equal engineering tracks aligned with each member's Deliverable 1 domain:

Akshata — Strict Priority Queuing Engine & Nodal Delay Instrumentation (server.py)

Upgraded the UDP server to a multi-threaded Strict Priority Scheduler with isolated FIFO queues (high_q, mod_q, low_q), ensuring arriving requests are always serviced in strict High > Moderate > Low order.

Implemented Selective Emergency Triggering, restricting emergency broadcast fan-out (h2, h3) exclusively to HIGH priority packets while returning standard acknowledgements for MODERATE and LOW traffic.

Instrumented server-side nodal delay tracking to measure exact Queuing Delay (
d 
queue
​
 ) and Service/Transmission Delay (
d 
trans
​
 +d 
proc
​
 ) per packet for downstream telemetry.   


B Raghavendra — OpenFlow 1.3 Enforcement, Namespace Bridging & Process Automation (network_topo.py, start.sh)

Resolved SDN control-plane handshake drops by enforcing OpenFlow 1.3 protocol compatibility on Open vSwitch (s1) and pre-populating ARP/flow tables.

Engineered automated background process orchestration inside network_topo.py to launch the UDP server, subscriber clients, and web server across isolated Mininet host namespaces without manual xterm intervention.

Configured virtual switch bridge routing (10.0.0.254/24 on s1) to expose the Mininet network directly to the host OS browser, and created the unified start.sh one-command startup and teardown pipeline.

Karthik Ganesh — Interactive Telemetry Web UI, Random Traffic Generator & RTT Measurement (app.py)

Designed and built the modern Flask Web Dashboard (app.py) featuring colour-coded priority telemetry (Red for High, Yellow for Moderate, Green for Low), live KPI cards, a pulsing emergency alert banner, and an interactive Nodal Delay Packet Inspector.

Developed the Random Traffic Generator Mode and Simultaneous Multi-Priority Burst / Congestion Wave stress-testing engines to simulate network load and bufferbloat in real time.

Implemented client-side Round-Trip Time (RTT) Measurement and TCP-style Exponential Weighted Moving Average (EWMA) calculations (
EstimatedRTT, 
DevRTT jitter, and 
TimeoutInterval), paired with live dual Chart.js visualizations (Stacked Nodal Delay Breakdown and Time-Series RTT convergence).
