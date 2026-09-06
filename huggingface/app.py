"""
Hugging Face Spaces App for Surf AI Agent.

This is a minimal Flask app required by Hugging Face Spaces.
The actual functionality is in the static HTML/JS files.
"""

from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder='static')

# Serve the static HTML file
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# Serve static files
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 7860)))
