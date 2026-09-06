import json
import os
from datetime import datetime

class TargetManager:
    
    def __init__(self, data_file='targets/targets.json'):
        self.data_file = data_file
        self.targets = []
        self.load_targets()
    
    def load_targets(self):
        if os.path.exists(self.data_file):
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
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.targets, f, indent=2)
            print(f"[+] Saved {len(self.targets)} targets")
            return True
        except Exception as e:
            print(f"[-] Error saving targets: {e}")
            return False
    
    def add_target(self, ip, os_type, name=None, port=None):
        for t in self.targets:
            if t['ip'] == ip:
                print(f"[-] Target {ip} already exists")
                return False
        
        target = {
            'id': len(self.targets) + 1,
            'name': name or f"Target-{ip}",
            'ip': ip,
            'os': os_type.lower(),
            'port': port or 4444,
            'status': 'pending',
            'added': datetime.now().isoformat(),
            'notes': ''
        }
        
        self.targets.append(target)
        self.save_targets()
        print(f"[+] Target added: {target['name']} ({ip})")
        return True
    
    def list_targets(self):
        if not self.targets:
            print("[-] No targets found")
            return
        
        print("\n📋 TARGETS:")
        print("=" * 70)
        print(f"{'ID':<4} {'Name':<20} {'IP':<16} {'OS':<10} {'Status':<12}")
        print("-" * 70)
        
        for t in self.targets:
            print(f"{t['id']:<4} {t['name'][:19]:<20} {t['ip']:<16} {t['os']:<10} {t['status']:<12}")
        print("=" * 70)
    
    def get_target(self, target_id):
        for t in self.targets:
            if t['id'] == target_id:
                return t
        return None
    
    def update_status(self, target_id, new_status):
        target = self.get_target(target_id)
        if not target:
            print(f"[-] Target {target_id} not found")
            return False
        
        target['status'] = new_status
        self.save_targets()
        print(f"[+] Updated target {target['name']} status to: {new_status}")
        return True
    
    def delete_target(self, target_id):
        target = self.get_target(target_id)
        if not target:
            print(f"[-] Target {target_id} not found")
            return False
        
        self.targets.remove(target)
        self.save_targets()
        print(f"[-] Deleted target: {target['name']} ({target['ip']})")
        return True
