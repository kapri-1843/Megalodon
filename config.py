import os
from pathlib import Path

class Config:
    
    def __init__(self):
        self.BASE_DIR = Path(__file__).parent
        self.DATA_DIR = self.BASE_DIR / 'data'
        self.MODULES_DIR = self.BASE_DIR / 'modules'
        
        self.DATA_DIR.mkdir(exist_ok=True)
        (self.DATA_DIR / 'targets').mkdir(exist_ok=True)
        (self.DATA_DIR / 'sessions').mkdir(exist_ok=True)
        (self.DATA_DIR / 'logs').mkdir(exist_ok=True)
        
        self.LISTENER_IP = os.getenv('LISTENER_IP', '0.0.0.0')
        self.LISTENER_PORT = int(os.getenv('LISTENER_PORT', 4444))
        self.TIMEOUT = 30
        self.MAX_RETRIES = 3
        
        self.API_KEYS = {
            'whatsapp': os.getenv('WHATSAPP_API_KEY', ''),
            'gmail': os.getenv('GMAIL_API_KEY', ''),
            'instagram': os.getenv('INSTAGRAM_API_KEY', ''),
            'tiktok': os.getenv('TIKTOK_API_KEY', '')
        }
