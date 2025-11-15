# Network Sentinel

**Real-time School Network Monitoring Dashboard**

---

## Overview
Network Sentinel is a Python and Flask-based application designed to monitor devices on a local network in real time. It provides latency information, online/offline status, and host details, updating automatically every few seconds.

---

## Features
- Discover devices on the local network automatically
- Ping-based latency measurement
- Online/offline status for each device
- Device hostname detection
- Web dashboard with live charts and tables
- Filters to show or hide offline devices
- Automatic updates every 5 seconds

---

## Technologies Used
- Python 3.11+
- Flask (web framework)
- Pythonping (latency monitoring)
- Scapy (optional, for advanced ARP scanning)
- JavaScript & Chart.js (frontend charts)
- HTML & CSS (dashboard UI)

---

## Installation & Usage
1. Clone the repository:
```bash
git clone https://github.com/Lz-acc/Sentinel_de_rede.git
Navigate to the project folder:

bash
Copiar código
cd Sentinel_de_cripto
Install dependencies:

bash
Copiar código
pip install -r requirements.txt
Run the Flask app:

bash
Copiar código
python app.py
Open your browser and go to http://127.0.0.1:5000 to access the dashboard.

Contributing
Contributions are welcome! Feel free to submit issues or pull requests.

License
This project is licensed under the MIT License.
