# 🦈 MEGALODON - Advanced Exploit Framework

A modular, AI-driven exploitation framework built from scratch for security research and penetration testing.

---

## Features

- Modular Architecture - Plug-and-play modules
- Multi-Platform - Android, Windows, Linux, iOS
- Zero-Click Capabilities - Exploit without user interaction
- Social Engineering - Automated SMS, Email, social media recon
- Real-time Monitoring - Live session management
- Web Dashboard - Full web interface with screen mirroring

---

## Project Structure

Megalodon/
├── core/ # Core framework engine
│ ├── framework.py # Main Megalodon class
│ ├── logger.py # Logging system
│ ├── session_manager.py # Session tracking
│ ├── module_loader.py # Dynamic module loading
│ ├── listener.py # Connection listener
│ ├── target_manager.py # Target management
│ └── websocket_server.py # WebSocket server
│
├── modules/ # All exploit modules
│ ├── recon/ # Reconnaissance
│ │ ├── network_scanner.py
│ │ ├── phone_scanner.py
│ │ ├── email_scanner.py
│ │ ├── username_scanner.py
│ │ └── social_scanner.py
│ │
│ ├── payloads/ # Payload generators
│ │ ├── apk_generator.py
│ │ ├── image_payload.py
│ │ ├── video_payload.py
│ │ └── web_payload.py
│ │
│ ├── exploits/ # Exploit modules
│ │ ├── ip_exploit.py
│ │ ├── sms_exploit.py
│ │ ├── email_exploit.py
│ │ ├── wifi_exploit.py
│ │ └── bluetooth_exploit.py
│ │
│ └── post_exploit/ # Post-exploitation
│ ├── screenshot_capture.py
│ ├── keylogger.py
│ ├── webcam_capture.py
│ ├── file_manager.py
│ ├── persistence.py
│ ├── screen_mirror.py
│ └── remote_control.py
│
├── payloads/ # Generated payloads
├── data/ # Persistent data storage
├── config/ # Configuration files
├── logs/ # Log files
├── templates/ # Web dashboard templates
├── web_dashboard.py # Flask web interface
├── run.py # Main entry point
├── requirements.txt # Python dependencies
└── README.md # This file
text


---

## Installation

```bash
# Clone
git clone https://github.com/kapri-1843/Megalodon.git
cd Megalodon

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python3 run.py

Commands
Target Management
Command	Description
target add <ip> <os> [name]	Add a target
target list	List all targets
target show <name>	Show target details
target delete <name>	Delete a target
target set <ip|phone|email> [os]	Set current target
Reconnaissance
Command	Description
recon phone <number>	Scan phone number
recon email <address>	Scan email
recon username <name>	Search username
recon social	Auto-scan current target
scan	Scan network for devices
Payloads
Command	Description
payload apk	Generate Android APK
payload image	Generate image payload
payload video	Generate video payload
payload web	Generate web payload
Exploits
Command	Description
exploit ip	IP/Network port scan
exploit sms	Send SMS exploit
exploit email	Send email exploit
exploit wifi	WiFi network scan
exploit bluetooth	Bluetooth device scan
Post-Exploitation
Command	Description
screenshot	Take screenshot
webcam	Capture webcam
keylog start	Start keylogger
keylog stop	Stop keylogger
keylog logs	View keystrokes
System
Command	Description
listen start	Start listener
listen stop	Stop listener
listen status	Listener status
status	Show current status
session list	List active sessions
help	Show all commands
exit	Exit Megalodon
Example Workflow
bash

# 1. Scan network
> scan

# 2. Add target
> target add 192.168.1.100 android Phone1

# 3. Recon target
> recon phone +1234567890

# 4. Generate payload
> payload apk

# 5. Start listener
> listen start

# 6. Send exploit
> exploit email

# 7. Check status
> status

# 8. Post-exploit
> screenshot
> keylog start
> keylog logs

Web Dashboard
bash

python3 web_dashboard.py

Open browser: http://localhost:5000

Features:

    Real-time target monitoring

    Screen mirroring

    Webcam streaming

    Remote control

    Keylogger view

    File browser

Configuration

Edit config/megalodon.json:
json

{
  "listener": {
    "ip": "0.0.0.0",
    "port": 4444
  },
  "email": {
    "sender_email": "your-email@gmail.com",
    "sender_password": "your-app-password",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587
  }
}

Gmail App Password

    Enable 2FA on Google account

    Security → App Passwords

    Select "Mail" → Generate

    Copy 16-character password

Modules Summary
Category	Count	Status
Reconnaissance	5	✅ Complete
Payloads	4	✅ Complete
Exploits	5	✅ Complete
Post-Exploit	7	✅ Complete
Total	21	✅ Complete
Disclaimer

This tool is for educational and authorized security testing only.

    Only use on systems you own or have explicit permission

    Unauthorized use is illegal and unethical

    Developers assume no liability for misuse

License

MIT License
Contact

    GitHub: @kapri-1843

    Repository: https://github.com/kapri-1843/Megalodon
