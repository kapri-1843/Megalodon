import json
import os
from pathlib import Path
from datetime import datetime

class TargetManager:
    
    def __init__(self, data_file='data/targets.json'):
        self.data_file = Path(data_file)
        self.targets = []
        self.load_targets()
    
    def load_targets(self):
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    self.targets = json.load(f)
                print(f"[+] Loaded {len(self.targets)} targets")
            except Exception as e:
                print(f"[-] Error loading targets: {e}")
                self.targets = []
        else:
            print("[+] No target file found, starting fresh")
            self.targets = []
    
    def save_targets(self):
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.targets, f, indent=2)
            return True
        except Exception as e:
            print(f"[-] Error saving targets: {e}")
            return False
    
    def add_target(self, ip, os_type, name=None, port=None):
        for t in self.targets:
            if t.get('ip') == ip:
                print(f"[-] Target {ip} already exists")
                return False
        
        target = {
            'id': len(self.targets) + 1,
            'name': name or f"Target-{ip}",
            'ip': ip,
            'os': os_type.lower(),
            'port': port or 4444,
            'status': 'pending',
            'added': datetime.now().isoformat()
        }
        
        self.targets.append(target)
        self.save_targets()
        print(f"[+] Target added: {target['name']} ({ip})")
        return True
    
    def list_targets(self):
        if not self.targets:
            print("[-] No targets found")
            return []
        
        print("\n📋 TARGETS:")
        print("=" * 70)
        print(f"{'ID':<4} {'Name':<20} {'IP':<16} {'OS':<10} {'Status':<12}")
        print("-" * 70)
        
        for t in self.targets:
            print(f"{t.get('id', '?'):<4} {t.get('name', 'Unknown')[:19]:<20} {t.get('ip', 'N/A'):<16} {t.get('os', 'unknown'):<10} {t.get('status', 'pending'):<12}")
        print("=" * 70)
        
        return self.targets
    
    def get_target(self, name_or_id):
        for t in self.targets:
            if t.get('name') == name_or_id or str(t.get('id')) == str(name_or_id):
                return t
        return None
    
    def get_target_by_ip(self, ip):
        for t in self.targets:
            if t.get('ip') == ip:
                return t
        return None
    
    def update_status(self, name_or_id, new_status):
        target = self.get_target(name_or_id)
        if not target:
            print(f"[-] Target {name_or_id} not found")
            return False
        
        target['status'] = new_status
        self.save_targets()
        print(f"[+] Updated target {target['name']} status to: {new_status}")
        return True
    
    def delete_target(self, name_or_id):
        target = self.get_target(name_or_id)
        if not target:
            print(f"[-] Target {name_or_id} not found")
            return False
        
        self.targets.remove(target)
        self.save_targets()
        print(f"[-] Deleted target: {target['name']} ({target['ip']})")
        return True
