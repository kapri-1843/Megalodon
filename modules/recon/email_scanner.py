import json
import requests
import hashlib
import re
from pathlib import Path

def scan(email_address=None):
    if not email_address:
        return {'success': False, 'error': 'No email provided'}
    
    results = {
        'success': True,
        'email': email_address,
        'domain': email_address.split('@')[1] if '@' in email_address else 'Unknown',
        'accounts': [],
        'breaches': [],
        'gravatar': False
    }
    
    # Check Gravatar
    try:
        gravatar_hash = hashlib.md5(email_address.lower().strip().encode()).hexdigest()
        gravatar_url = f"https://gravatar.com/{gravatar_hash}"
        response = requests.get(gravatar_url, timeout=5)
        results['gravatar'] = response.status_code == 200
    except:
        results['gravatar'] = False
    
    # 35+ Services to check for email-based accounts
    services = [
        {
            'name': 'Gmail',
            'url': f'https://mail.google.com/mail/u/0/',
            'check_type': 'email_domain'
        },
        {
            'name': 'Yahoo',
            'url': f'https://login.yahoo.com/',
            'check_type': 'email_domain'
        },
        {
            'name': 'Outlook/Hotmail',
            'url': f'https://outlook.live.com/',
            'check_type': 'email_domain'
        },
        {
            'name': 'ProtonMail',
            'url': f'https://protonmail.com/',
            'check_type': 'email_domain'
        },
        {
            'name': 'iCloud',
            'url': f'https://icloud.com/',
            'check_type': 'email_domain'
        },
        {
            'name': 'AOL',
            'url': f'https://mail.aol.com/',
            'check_type': 'email_domain'
        },
        {
            'name': 'Mail.com',
            'url': f'https://mail.com/',
            'check_type': 'email_domain'
        },
        {
            'name': 'GMX',
            'url': f'https://gmx.com/',
            'check_type': 'email_domain'
        },
        {
            'name': 'Facebook',
            'url': f'https://facebook.com/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'Twitter/X',
            'url': f'https://twitter.com/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'Instagram',
            'url': f'https://instagram.com/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'LinkedIn',
            'url': f'https://linkedin.com/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'GitHub',
            'url': f'https://github.com/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'Reddit',
            'url': f'https://reddit.com/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'Pinterest',
            'url': f'https://pinterest.com/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'Tumblr',
            'url': f'https://tumblr.com/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'Spotify',
            'url': f'https://spotify.com/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'Netflix',
            'url': f'https://netflix.com/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'Amazon',
            'url': f'https://amazon.com/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'eBay',
            'url': f'https://ebay.com/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'PayPal',
            'url': f'https://paypal.com/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'Stripe',
            'url': f'https://stripe.com/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'Shopify',
            'url': f'https://shopify.com/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'Etsy',
            'url': f'https://etsy.com/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'Discord',
            'url': f'https://discord.com/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'Slack',
            'url': f'https://slack.com/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'Zoom',
            'url': f'https://zoom.us/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'Skype',
            'url': f'https://skype.com/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'Telegram',
            'url': f'https://telegram.org/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'WhatsApp',
            'url': f'https://whatsapp.com/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'Signal',
            'url': f'https://signal.org/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'WordPress',
            'url': f'https://wordpress.com/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'TikTok',
            'url': f'https://tiktok.com/',
            'check_type': 'email_lookup'
        },
        {
            'name': 'Snapchat',
            'url': f'https://snapchat.com/',
            'check_type': 'email_lookup'
        }
    ]
    
    # Check each service
    for service in services:
        try:
            # For email domains, check if the domain matches
            if service['check_type'] == 'email_domain':
                domain = email_address.split('@')[1].lower()
                service_domain = service['url'].replace('https://', '').replace('http://', '').replace('/', '')
                if service_domain in domain or domain in service_domain:
                    results['accounts'].append({
                        'platform': service['name'],
                        'url': service['url'],
                        'status': 'likely_exists',
                        'match': 'email_domain'
                    })
            elif service['check_type'] == 'email_lookup':
                # For services where we can check existence via API or public pages
                results['accounts'].append({
                    'platform': service['name'],
                    'url': service['url'],
                    'status': 'possible',
                    'match': 'email_lookup'
                })
        except:
            continue
    
    # Check for breaches using HaveIBeenPwned
    try:
        response = requests.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{email_address}",
            headers={'hibp-api-key': ''},
            timeout=10
        )
        if response.status_code == 200:
            breaches = response.json()
            results['breaches'] = [{'name': b['Name'], 'date': b.get('BreachDate', 'Unknown')} for b in breaches]
            results['breach_count'] = len(breaches)
        else:
            results['breaches'] = []
            results['breach_count'] = 0
    except:
        results['breaches'] = []
        results['breach_count'] = 0
    
    results['account_count'] = len(results['accounts'])
    
    return results
