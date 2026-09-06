import json
import requests
from pathlib import Path

def run(target_info=None):
    if not target_info:
        return {'success': False, 'error': 'No target info provided'}
    
    value = target_info.get('value', '')
    
    if not value:
        return {'success': False, 'error': 'No value to scan'}
    
    result = {
        'success': True,
        'value': value,
        'type': target_info.get('type', 'unknown'),
        'email_findings': {},
        'phone_findings': {},
        'username_findings': {}
    }
    
    # Check if it's an email
    if '@' in value and '.' in value:
        from modules.recon.email_scanner import scan
        email_result = scan(value)
        result['email_findings'] = email_result
    
    # Check if it's a phone number
    phone_clean = value.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
    if phone_clean.isdigit() and len(phone_clean) >= 7:
        from modules.recon.phone_scanner import scan
        phone_result = scan(value)
        result['phone_findings'] = phone_result
    
    # Check if it's a username (not email or phone)
    is_email = '@' in value and '.' in value
    is_phone = phone_clean.isdigit() and len(phone_clean) >= 7
    
    if not is_email and not is_phone:
        from modules.recon.username_scanner import scan
        username_result = scan(value)
        result['username_findings'] = username_result
    
    # Also try as username for emails (extract username part)
    if is_email:
        username_part = value.split('@')[0]
        from modules.recon.username_scanner import scan
        username_result = scan(username_part)
        result['username_findings'] = username_result
    
    return result
