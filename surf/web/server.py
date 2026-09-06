"""
Flask Web Server for Surf AI Agent.

Provides a web interface and API for the Surf agent.
Designed for container deployment with minimal resource usage.
"""

import os
import json
from typing import Optional, Dict, Any, List
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import threading

# Import Surf components
from surf import SurfAgent, SurfConfig
from surf.actions import BaseAction, ClickAction, TypeAction, PressKeyAction, ScrollAction

app = Flask(__name__, static_folder='static', template_folder='templates')

# Global agent instance (will be initialized on first request)
_agent = None
_agent_lock = threading.Lock()

# Configuration storage (for web UI)
_config = None


def get_agent() -> SurfAgent:
    """Get or create the Surf agent instance."""
    global _agent, _config
    
    if _agent is None:
        with _agent_lock:
            if _agent is None:
                # Use default config or from environment
                config = SurfConfig.from_env()
                _config = config
                _agent = SurfAgent(config)
    
    return _agent


def update_agent_config(config: SurfConfig) -> None:
    """Update the agent configuration."""
    global _agent, _config
    
    with _agent_lock:
        _config = config
        if _agent is not None:
            _agent.close()
        _agent = SurfAgent(config)


@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files."""
    return send_from_directory('static', filename)


@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """Get or update configuration."""
    global _config
    
    if request.method == 'GET':
        # Return current config (mask API key)
        config_dict = _config.to_dict() if _config else {}
        config_dict['api_key'] = '***MASKED***' if config_dict.get('api_key') else None
        return jsonify({
            'config': config_dict,
            'has_config': _config is not None
        })
    
    elif request.method == 'POST':
        data = request.json
        
        # Create new config from request
        config_kwargs = {
            'base_url': data.get('base_url', 'https://api.openai.com/v1'),
            'model': data.get('model', 'gpt-4o-mini'),
            'temperature': data.get('temperature', 0.7),
            'max_tokens': data.get('max_tokens', 4096),
            'timeout': data.get('timeout', 30),
            'verbose': data.get('verbose', False),
        }
        
        # Only set API key if provided
        if data.get('api_key'):
            config_kwargs['api_key'] = data['api_key']
        
        # Handle custom headers
        if data.get('headers'):
            config_kwargs['headers'] = data['headers']
        
        try:
            config = SurfConfig(**config_kwargs)
            update_agent_config(config)
            return jsonify({'status': 'success', 'message': 'Configuration updated'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/actions', methods=['POST'])
def handle_actions():
    """Execute actions from natural language instruction."""
    data = request.json
    instruction = data.get('instruction', '')
    context = data.get('context', None)
    
    if not instruction:
        return jsonify({'status': 'error', 'message': 'No instruction provided'}), 400
    
    try:
        agent = get_agent()
        result = agent.run(instruction, context=context)
        
        # Serialize actions
        actions = []
        for action in result.actions_executed:
            actions.append({
                'type': action.action_type,
                'params': action.params
            })
        
        failed = []
        for action, error in result.actions_failed:
            failed.append({
                'type': action.action_type,
                'params': action.params,
                'error': error
            })
        
        return jsonify({
            'status': 'success' if result.success else 'partial',
            'message': result.message,
            'success': result.success,
            'actions_executed': actions,
            'actions_failed': failed,
            'error': result.error
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/actions/direct', methods=['POST'])
def handle_direct_actions():
    """Execute pre-defined actions directly."""
    data = request.json
    actions_data = data.get('actions', [])
    
    if not actions_data:
        return jsonify({'status': 'error', 'message': 'No actions provided'}), 400
    
    try:
        from surf.actions import parse_action
        
        # Parse actions
        actions = [parse_action(action) for action in actions_data]
        
        agent = get_agent()
        result = agent.run_actions(actions)
        
        # Serialize results
        executed = []
        for action in result.actions_executed:
            executed.append({
                'type': action.action_type,
                'params': action.params
            })
        
        failed = []
        for action, error in result.actions_failed:
            failed.append({
                'type': action.action_type,
                'params': action.params,
                'error': error
            })
        
        return jsonify({
            'status': 'success' if result.success else 'partial',
            'message': result.message,
            'success': result.success,
            'actions_executed': executed,
            'actions_failed': failed
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'version': '0.1.0'})


@app.route('/api/available_actions')
def get_available_actions():
    """Get list of available action types."""
    agent = get_agent()
    actions = agent.get_available_actions()
    return jsonify(actions)


# For local Python use (non-web)
def run_local(instruction: str, config: Optional[SurfConfig] = None) -> Dict[str, Any]:
    """
    Run Surf agent locally without web server.
    
    Args:
        instruction: Natural language instruction
        config: Optional SurfConfig
        
    Returns:
        Result dictionary
    """
    if config:
        agent = SurfAgent(config)
    else:
        config = SurfConfig.from_env()
        agent = SurfAgent(config)
    
    try:
        result = agent.run(instruction)
        
        actions = []
        for action in result.actions_executed:
            actions.append({
                'type': action.action_type,
                'params': action.params
            })
        
        failed = []
        for action, error in result.actions_failed:
            failed.append({
                'type': action.action_type,
                'params': action.params,
                'error': error
            })
        
        return {
            'status': 'success' if result.success else 'partial',
            'message': result.message,
            'success': result.success,
            'actions_executed': actions,
            'actions_failed': failed,
            'error': result.error
        }
    finally:
        agent.close()


if __name__ == '__main__':
    # Run the Flask server
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    print(f"Starting Surf Web Server on {host}:{port}")
    print(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug, threaded=True)
