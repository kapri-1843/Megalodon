import logging
from pathlib import Path
from datetime import datetime

class Logger:
    
    def __init__(self, name='Megalodon'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        if not self.logger.handlers:
            log_dir = Path(__file__).parent.parent / 'data' / 'logs'
            log_dir.mkdir(parents=True, exist_ok=True)
            
            log_file = log_dir / f"megalodon_{datetime.now().strftime('%Y%m%d')}.log"
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def info(self, message):
        self.logger.info(message)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def success(self, message):
        self.logger.info(f"✅ {message}")
    
    def fail(self, message):
        self.logger.error(f"❌ {message}")

logger = Logger()
