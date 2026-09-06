import json
import uuid
from datetime import datetime
from pathlib import Path

class SessionManager:
    
    def __init__(self):
        self.sessions_dir = Path(__file__).parent.parent / 'data' / 'sessions'
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.active_sessions = {}
        self.load_sessions()
    
    def load_sessions(self):
        for session_file in self.sessions_dir.glob('*.json'):
            try:
                with open(session_file, 'r') as f:
                    session = json.load(f)
                    self.active_sessions[session['id']] = session
            except:
                pass
    
    def create_session(self, target_info):
        session_id = str(uuid.uuid4())[:8]
        session = {
            'id': session_id,
            'target': target_info,
            'connected': True,
            'created': datetime.now().isoformat(),
            'commands': []
        }
        self.active_sessions[session_id] = session
        self._save_session(session_id)
        return session_id
    
    def get_session(self, session_id):
        return self.active_sessions.get(session_id)
    
    def list_sessions(self):
        return list(self.active_sessions.values())
    
    def close_session(self, session_id):
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['connected'] = False
            self._save_session(session_id)
            return True
        return False
    
    def add_command(self, session_id, command, output):
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['commands'].append({
                'command': command,
                'output': output,
                'timestamp': datetime.now().isoformat()
            })
            self._save_session(session_id)
    
    def _save_session(self, session_id):
        session_file = self.sessions_dir / f"{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(self.active_sessions[session_id], f, indent=2)
