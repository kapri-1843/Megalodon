import json
import socket
import subprocess
from pathlib import Path

class AppScanner:
    
    def __init__(self):
        self.target = None
        self.vulnerable_ports = {
            5222: 'WhatsApp',
            5228: 'WhatsApp',
            8080: 'HTTP',
            8443: 'HTTPS',
            5555: 'ADB (Android)',
            22: 'SSH',
            3389: 'RDP'
        }
    
    def set_target(self, target_info):
        self.target = target_info
        print(f"[+] Target set: {target_info.get('value', 'Unknown')}")
        return {'success': True}
    
    def scan_ports(self, ip, ports=None):
        if ports is None:
            ports = list(self.vulnerable_ports.keys())
        
        print(f"[*] Scanning {ip} for vulnerable services...")
        open_ports = []
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    service = self.vulnerable_ports.get(port, 'Unknown')
                    open_ports.append({
                        'port': port,
                        'service': service,
                        'vulnerable': service in ['ADB (Android)', 'SSH', 'RDP']
                    })
                    print(f"[+] Port {port} open ({service})")
            except:
                pass
        
        return open_ports
    
    def scan(self, target_info=None):
        if target_info:
            self.set_target(target_info)
        
        if not self.target:
            return {'success': False, 'error': 'No target set'}
        
        ip = self.target.get('value')
        results = {
            'target': ip,
            'open_ports': self.scan_ports(ip),
            'vulnerable_services': []
        }
        
        for port in results['open_ports']:
            if port['vulnerable']:
                results['vulnerable_services'].append(port)
        
        return {
            'success': True,
            'results': results,
            'message': f"Found {len(results['open_ports'])} open ports"
        }

def run(target_info=None):
    scanner = AppScanner()
    return scanner.scan(target_info)
