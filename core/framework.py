import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.logger import logger
from core.session_manager import SessionManager
from core.module_loader import ModuleLoader
from config import Config

class Megalodon:
    
    def __init__(self):
        self.config = Config()
        self.session = SessionManager()
        self.module_loader = ModuleLoader()
        self.target = None
        self.compromised = False
        self.last_result = None
    
    def set_target(self, target_info):
        self.target = target_info
        logger.success(f"Target set: {target_info.get('value', 'Unknown')}")
        
    def run_recon(self):
        logger.info("Running reconnaissance...")
        module = self.module_loader.load('recon', 'phone_scanner')
        if module:
            result = module.run(self.target)
            self.last_result = result
            return result
        return {'success': False, 'error': 'Recon module not found'}
    
    def generate_payload(self, os_type):
        logger.info(f"Generating payload for {os_type}...")
        module = self.module_loader.load('payloads', 'reverse_shell')
        if module:
            result = module.generate(os_type)
            self.last_result = result
            return result
        return {'success': False, 'error': 'Payload module not found'}
    
    def run_exploit(self, method):
        logger.info(f"Running exploit: {method}...")
        module = self.module_loader.load('exploits', method)
        if module:
            result = module.run(self.target)
            self.last_result = result
            if result.get('success'):
                self.compromised = True
                session_id = self.session.create_session(self.target)
                logger.success(f"Target compromised! Session: {session_id}")
            return result
        return {'success': False, 'error': f'Exploit {method} not found'}
    
    def run_post_exploit(self, action):
        if not self.compromised:
            logger.error("Target not compromised yet")
            return {'success': False, 'error': 'Not compromised'}
        
        logger.info(f"Running post-exploitation: {action}...")
        module = self.module_loader.load('post_exploit', action)
        if module:
            result = module.run(self.target)
            self.last_result = result
            return result
        return {'success': False, 'error': f'Post-exploit {action} not found'}
    
    def get_status(self):
        return {
            'target': self.target,
            'compromised': self.compromised,
            'last_result': self.last_result,
            'sessions': self.session.list_sessions()
        }
