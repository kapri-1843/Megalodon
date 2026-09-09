import json
import requests
import phonenumbers
from phonenumbers import carrier, geocoder, timezone

def scan(phone_number=None):
    if not phone_number:
        return {'success': False, 'error': 'No phone number provided'}
    
    try:
        # Parse phone number
        parsed = phonenumbers.parse(phone_number, None)
        
        if not phonenumbers.is_valid_number(parsed):
            return {'success': False, 'error': 'Invalid phone number'}
        
        # Get carrier and location
        country = geocoder.country_name_for_number(parsed, "en")
        location = geocoder.description_for_number(parsed, "en")
        carrier_name = carrier.name_for_number(parsed, "en")
        timezones = timezone.time_zones_for_number(parsed)
        
        # Format number
        e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        national = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
        
        results = {
            'success': True,
            'phone': phone_number,
            'country': country,
            'location': location,
            'carrier': carrier_name,
            'timezones': list(timezones) if timezones else [],
            'valid': True,
            'e164': e164,
            'national': national
        }
        
        # ========== NEW: Registration Details ==========
        print("\n📱 PHONE RECON RESULTS")
        print("=" * 50)
        print(f"Number: {phone_number}")
        print(f"Country: {country}")
        print(f"Location: {location}")
        print(f"Carrier: {carrier_name}")
        print("=" * 50)
        
        # Try to get registration/owner info
        results['registration'] = get_phone_registration(phone_number, country)
        
        print("\n📋 REGISTRATION DETAILS:")
        print("-" * 40)
        if results['registration']['success']:
            for key, value in results['registration'].items():
                if key != 'success' and value:
                    print(f"{key.capitalize()}: {value}")
        else:
            print("  Not available (free tier limited)")
        print("-" * 40)
        
        return results
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_phone_registration(phone_number, country):
    """Try to get registration details using free APIs"""
    
    registration = {
        'success': False,
        'owner': None,
        'company': None,
        'type': None,
        'status': None
    }
    
    # Method 1: Use numverify (free tier)
    try:
        # Free API key (public demo key for testing)
        api_key = 'demo'  # Replace with your free numverify key
        response = requests.get(
            f'http://apilayer.net/api/validate?number={phone_number}&access_key={api_key}',
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('valid'):
                registration['success'] = True
                registration['owner'] = data.get('owner', 'Unknown')
                registration['company'] = data.get('carrier', 'Unknown')
                registration['type'] = data.get('line_type', 'Unknown')  # mobile, landline, voip
                registration['status'] = 'Active'
                print(f"[+] Registration info found via numverify")
                return registration
    except:
        pass
    
    # Method 2: Use abstractapi (free tier)
    try:
        api_key = 'demo'  # Replace with your free abstractapi key
        response = requests.get(
            f'https://phonevalidation.abstractapi.com/v1/?api_key={api_key}&phone={phone_number}',
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('valid'):
                registration['success'] = True
                registration['owner'] = 'Not available'
                registration['company'] = data.get('carrier', 'Unknown')
                registration['type'] = data.get('line_type', 'Unknown')
                registration['status'] = data.get('location', 'Unknown')
                print("[+] Registration info found via abstractapi")
                return registration
    except:
        pass
    
    # Method 3: Local carrier lookup (if no API available)
    if country:
        # Common carrier prefixes (if not detected by API)
        prefixes = {
            'Kenya': {
                'Safaricom': ['0722', '0723', '0724', '0725', '0726', '0727', '0728', '0729'],
                'Airtel': ['0733', '0734', '0735', '0736', '0737', '0738'],
                'Telkom': ['0777', '0778', '0779']
            },
            'Nigeria': {
                'MTN': ['0803', '0806', '0803', '0903', '0906'],
                'Glo': ['0805', '0807', '0811', '0815', '0905'],
                'Airtel': ['0802', '0808', '0812', '0902', '0907'],
                '9mobile': ['0809', '0817', '0818', '0909']
            },
            'South Africa': {
                'Vodacom': ['082', '072', '071'],
                'MTN': ['083', '073', '063'],
                'Cell C': ['084', '074', '064']
            }
        }
        
        # Clean number for prefix matching
        clean_number = phone_number.replace('+', '').replace(' ', '').replace('-', '')
        if len(clean_number) > 4:
            prefix = clean_number[-9:-4] if len(clean_number) >= 9 else clean_number[:4]
            
            if country in prefixes:
                for company, prefs in prefixes[country].items():
                    if any(prefix.startswith(p) for p in prefs):
                        registration['success'] = True
                        registration['company'] = company
                        registration['type'] = 'Mobile'
                        registration['status'] = 'Registered'
                        registration['owner'] = 'Not available'
                        print(f"[+] Carrier detected via prefix: {company}")
                        return registration
    
    # If all fails
    registration['message'] = 'Registration info not available (free tier limited)'
    return registration
