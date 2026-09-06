import json
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
        
        # Get details
        country = geocoder.country_name_for_number(parsed, "en")
        location = geocoder.description_for_number(parsed, "en")
        carrier_name = carrier.name_for_number(parsed, "en")
        timezones = timezone.time_zones_for_number(parsed)
        
        return {
            'success': True,
            'phone': phone_number,
            'country': country,
            'location': location,
            'carrier': carrier_name,
            'timezones': list(timezones) if timezones else [],
            'valid': True,
            'e164': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
            'national': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}
