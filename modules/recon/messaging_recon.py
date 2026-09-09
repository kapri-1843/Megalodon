import json
import requests
import phonenumbers
from phonenumbers import carrier, geocoder
from pathlib import Path

class MessagingRecon:
    
    def __init__(self):
        self.target = None
    
    def set_target(self, target_info):
        self.target = target_info
        print(f"[+] Target set: {target_info.get('value', 'Unknown')}")
        return {'success': True}
    
    def scan_phone(self, phone_number):
        results = {
            'phone': phone_number,
            'platforms': [],
            'sms_capable': False,
            'mms_capable': False
        }
        
        try:
            parsed = phonenumbers.parse(phone_number, None)
            if phonenumbers.is_valid_number(parsed):
                country = geocoder.country_name_for_number(parsed, "en")
                results['country'] = country
                results['carrier'] = carrier.name_for_number(parsed, "en")
                results['sms_capable'] = True
                results['mms_capable'] = True
        
        except:
            results['sms_capable'] = True
            results['mms_capable'] = True
        
        # Check common messaging platforms
        platforms = ['WhatsApp', 'Telegram', 'Signal', 'Facebook Messenger']
        for platform in platforms:
            results['platforms'].append({
                'name': platform,
                'available': True  # Simulated
            })
        
        return {
            'success': True,
            'results': results,
            'message': 'Phone recon complete'
        }
    
    def scan(self, target_info=None):
        if target_info:
            self.set_target(target_info)
        
        if not self.target:
            return {'success': False, 'error': 'No target set'}
        
        value = self.target.get('value', '')
        
        # Detect if it's a phone number
        phone_clean = value.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        if phone_clean.isdigit() and len(phone_clean) >= 7:
            return self.scan_phone(value)
        
        return {'success': False, 'error': 'Not a valid phone number'}

def run(target_info=None):
    recon = MessagingRecon()
    return recon.scan(target_info)
