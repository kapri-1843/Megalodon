import json
import requests
import re
from pathlib import Path

def scan(username=None):
    if not username:
        return {'success': False, 'error': 'No username provided'}
    
    results = {
        'success': True,
        'username': username,
        'platforms': [],
        'found_count': 0
    }
    
    # 35+ Platforms to check
    platforms = {
        'github': f'https://github.com/{username}',
        'twitter': f'https://twitter.com/{username}',
        'instagram': f'https://instagram.com/{username}',
        'reddit': f'https://reddit.com/user/{username}',
        'youtube': f'https://youtube.com/@{username}',
        'tiktok': f'https://tiktok.com/@{username}',
        'linkedin': f'https://linkedin.com/in/{username}',
        'facebook': f'https://facebook.com/{username}',
        'pinterest': f'https://pinterest.com/{username}',
        'tumblr': f'https://tumblr.com/blog/{username}',
        'snapchat': f'https://snapchat.com/add/{username}',
        'telegram': f'https://t.me/{username}',
        'discord': f'https://discord.com/users/{username}',
        'spotify': f'https://open.spotify.com/user/{username}',
        'soundcloud': f'https://soundcloud.com/{username}',
        'flickr': f'https://flickr.com/people/{username}',
        'deviantart': f'https://deviantart.com/{username}',
        'vimeo': f'https://vimeo.com/{username}',
        'twitch': f'https://twitch.tv/{username}',
        'patreon': f'https://patreon.com/{username}',
        'medium': f'https://medium.com/@{username}',
        'quora': f'https://quora.com/profile/{username}',
        'steam': f'https://steamcommunity.com/id/{username}',
        'roblox': f'https://roblox.com/user.aspx?username={username}',
        'imgur': f'https://imgur.com/user/{username}',
        'pastebin': f'https://pastebin.com/u/{username}',
        'slack': f'https://slack.com/community/{username}',
        'zoom': f'https://zoom.us/user/{username}',
        'skype': f'https://skype.com/account/username/{username}',
        'whatsapp': f'https://wa.me/+{username}',
        'viber': f'https://viber.com/{username}',
        'line': f'https://line.me/R/ti/p/@{username}',
        'wechat': f'https://wechat.com/{username}',
        'kik': f'https://kik.me/{username}',
        'tinder': f'https://tinder.com/profile/{username}',
        'bumble': f'https://bumble.com/{username}',
        'hinge': f'https://hinge.co/{username}'
    }
    
    found = []
    
    for platform, url in platforms.items():
        try:
            response = requests.get(url, timeout=5, allow_redirects=True)
            
            # Check if page exists (status 200)
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for "not found" indicators
                not_found_indicators = [
                    'page not found',
                    'sorry, this page is not available',
                    'not found',
                    'doesn\'t exist',
                    'user not found',
                    'profile not found',
                    'account not found',
                    'this user has no profile'
                ]
                
                # Also check for redirect patterns
                is_not_found = any(indicator in content for indicator in not_found_indicators)
                
                if not is_not_found:
                    found.append({
                        'platform': platform,
                        'url': url,
                        'exists': True,
                        'status_code': response.status_code
                    })
        except:
            continue
    
    results['platforms'] = found
    results['found_count'] = len(found)
    
    return results
