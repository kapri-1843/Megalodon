import subprocess
import re
import socket

class NetworkScanner:
    
    def __init__(self):
        self.network_range = self.auto_detect_network()
        self.interfaces = self.get_interfaces()
    
    def auto_detect_network(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 1))
            ip = s.getsockname()[0]
            s.close()
            if not ip.startswith('127.'):
                parts = ip.split('.')
                return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
        except:
            pass
        return "192.168.1.0/24"
    
    def get_interfaces(self):
        interfaces = []
        try:
            result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'inet ' in line:
                    match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+)', line)
                    if match:
                        ip = match.group(1)
                        if not ip.startswith('127.'):
                            interfaces.append(ip)
        except:
            pass
        return interfaces
    
    def get_hostname(self, ip):
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return 'Unknown'
    
    def scan(self):
        print(f"\n[+] Network: {self.network_range}")
        print(f"[+] Interfaces: {', '.join(self.interfaces) if self.interfaces else 'Unknown'}")
        print("\n[*] Scanning with nmap...")
        print("=" * 50)
        
        devices = []
        
        try:
            # Use TCP connect scan with unprivileged flag
            cmd = ['nmap', '-sT', '--unprivileged', self.network_range]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                output = result.stdout
                
                # Find all IPs with hostnames
                current_ip = None
                current_hostname = 'Unknown'
                
                for line in output.split('\n'):
                    if 'Nmap scan report for' in line:
                        # Extract IP
                        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                        if ip_match:
                            current_ip = ip_match.group(1)
                            current_hostname = 'Unknown'
                            
                            # Extract hostname if present
                            if '(' in line and ')' in line:
                                parts = line.split('(')
                                if len(parts) > 1:
                                    hostname = parts[0].replace('Nmap scan report for', '').strip()
                                    if hostname and hostname != current_ip:
                                        current_hostname = hostname
                    
                    elif 'Host is up' in line and current_ip:
                        # Device is online
                        pass
                    
                    elif '/tcp' in line and current_ip and 'open' in line:
                        # Port is open - extract port and service
                        port_match = re.search(r'(\d+)/tcp\s+open\s+(\S+)', line)
                        if port_match:
                            port = port_match.group(1)
                            service = port_match.group(2)
                            
                            # Find or create device entry
                            device = next((d for d in devices if d['ip'] == current_ip), None)
                            if not device:
                                devices.append({
                                    'ip': current_ip,
                                    'hostname': current_hostname,
                                    'ports': [{'port': port, 'service': service}]
                                })
                            else:
                                device['ports'].append({'port': port, 'service': service})
                
                # Also find devices without open ports
                report_ips = re.findall(r'Nmap scan report for (\d+\.\d+\.\d+\.\d+)', output)
                for ip in report_ips:
                    if not any(d['ip'] == ip for d in devices):
                        devices.append({
                            'ip': ip,
                            'hostname': self.get_hostname(ip),
                            'ports': []
                        })
                
                print(f"[+] nmap scan complete: {len(devices)} devices found")
                
                # Parse detailed OS info if available
                for device in devices:
                    ip = device['ip']
                    try:
                        os_cmd = ['nmap', '-O', '--osscan-guess', ip]
                        os_result = subprocess.run(os_cmd, capture_output=True, text=True, timeout=60)
                        if os_result.returncode == 0:
                            os_match = re.search(r'OS details:\s+(.+?)(?:\n|$)', os_result.stdout)
                            if os_match:
                                device['os'] = os_match.group(1).strip()
                    except:
                        pass
                
            else:
                print(f"[-] nmap error: {result.stderr}")
                
        except Exception as e:
            print(f"[-] Scan failed: {e}")
            return {'success': False, 'error': str(e)}
        
        # Display results
        print("\n" + "=" * 50)
        print(f"[+] TOTAL DEVICES FOUND: {len(devices)}")
        print("=" * 50)
        
        if devices:
            print("\n📋 DETAILED DEVICE INFO:")
            print("-" * 80)
            for d in devices:
                print(f"\n  📍 {d['ip']} ({d.get('hostname', 'Unknown')})")
                if d.get('os'):
                    print(f"     OS: {d['os']}")
                if d.get('ports'):
                    print(f"     Open Ports:")
                    for port in d['ports']:
                        print(f"       - {port['port']}/tcp ({port['service']})")
                else:
                    print("     No open ports detected")
            print("-" * 80)
        else:
            print("[!] No devices found")
        
        return {
            'success': True,
            'devices': devices,
            'count': len(devices),
            'network': self.network_range
        }

def scan():
    scanner = NetworkScanner()
    return scanner.scan()
