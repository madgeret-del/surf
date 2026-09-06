# Surf - Computer Use AI Agent

Surf is a flexible, open-source AI agent that enables computer use through natural language instructions. It can interact with GUI environments by generating and executing actions like click, double-click, scroll, type, press keys, and more.

## Features

- **Multi-Provider Support**: Works with any LLM provider (OpenAI, local LLMs, custom providers)
- **Configurable**: Set your base URL and API key for any compatible API
- **Extensible Actions**: Support for mouse clicks, keyboard input, scrolling, and more
- **Natural Language Interface**: Describe what you want to do in plain English
- **Programmatic Control**: Execute pre-defined actions or let the LLM generate them
- **Web Interface**: HTML frontend for container deployment
- **Docker Ready**: Optimized for free container services (2-8GB RAM)

## Installation

### Python Library

```bash
pip install surf-ai-agent
```

Or from source:

```bash
git clone https://github.com/madgeret-del/surf.git
cd surf
pip install -r requirements.txt
```

### Docker Container

For free container services (RunPod, Railway, Render, Fly.io, etc.):

```bash
# Build and run
docker build -t surf-ai-agent .
docker run -p 8080:8080 -e SURF_API_KEY=your-key surf-ai-agent

# Or with docker-compose
docker-compose up -d
```

### Using Pre-built Image

```bash
docker pull ghcr.io/madgeret-del/surf:latest
docker run -p 8080:8080 -e SURF_API_KEY=your-key ghcr.io/madgeret-del/surf:latest
```

## Quick Start

### For Free Container Services

Surf is optimized for deployment on free container platforms with Xeon CPUs and 2-8GB RAM:

- **RunPod** - Free GPU/CPU containers
- **Railway** - Free tier with 2GB RAM
- **Render** - Free web services
- **Fly.io** - Free small containers
- **Replit** - Free containers
- **Hugging Face Spaces** - Free hosting

#### One-Click Deploy (RunPod)

1. Create a new container on RunPod
2. Use this Dockerfile or pull from `ghcr.io/madgeret-del/surf:latest`
3. Set environment variables:
   - `SURF_API_KEY` = Your LLM API key
   - `SURF_BASE_URL` = Your LLM base URL (default: OpenAI)
   - `SURF_MODEL` = Model to use (default: gpt-4o-mini)
4. Expose port 8080
5. Access the web UI at `http://your-container-url:8080`

#### One-Click Deploy (Railway)

1. Create new Railway project
2. Connect GitHub repo
3. Set environment variables
4. Deploy!

### Using OpenAI

```python
from surf import SurfAgent, SurfConfig

config = SurfConfig(
    base_url="https://api.openai.com/v1",
    api_key="your-api-key",
    model="gpt-4o-mini",
    verbose=True
)

with SurfAgent(config) as agent:
    result = agent.run("Click at coordinates 100, 200 and type 'Hello World'")
    print(f"Executed {len(result.actions_executed)} actions")
```

### Using a Local LLM (Ollama, LM Studio, etc.)

```python
from surf import SurfAgent, SurfConfig

config = SurfConfig(
    base_url="http://localhost:11434/v1",
    api_key="not-needed",
    model="llama3.2",
    verbose=True
)

with SurfAgent(config) as agent:
    result = agent.run("Move the mouse to 500, 300 and double-click")
```

### Using Environment Variables

```bash
export SURF_BASE_URL="https://api.openai.com/v1"
export SURF_API_KEY="your-api-key"
export SURF_MODEL="gpt-4"
export SURF_VERBOSE="1"
```

```python
from surf import SurfAgent, SurfConfig

config = SurfConfig.from_env()

with SurfAgent(config) as agent:
    result = agent.run("Scroll down by 100 pixels")
```

### Programmatic Actions

```python
from surf import SurfAgent, SurfConfig
from surf.actions import ClickAction, TypeAction, WaitAction

config = SurfConfig()

with SurfAgent(config) as agent:
    actions = [
        ClickAction(x=100, y=200),
        TypeAction(text="Hello!"),
        WaitAction(seconds=1.0)
    ]
    result = agent.run_actions(actions)
```

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_url` | str | `"https://api.openai.com/v1"` | Base URL for the LLM API |
| `api_key` | str | None | API key for authentication |
| `model` | str | `"gpt-4"` | Model name to use |
| `temperature` | float | 0.7 | Sampling temperature (0.0-2.0) |
| `max_tokens` | int | 4096 | Maximum tokens in response |
| `timeout` | int | 30 | Request timeout in seconds |
| `verbose` | bool | False | Enable verbose logging |
| `action_timeout` | int | 10 | Timeout for individual actions |
| `max_actions` | int | 20 | Maximum actions per instruction |
| `headers` | dict | {} | Additional HTTP headers |
| `extra_params` | dict | {} | Additional request parameters |

## Available Actions

| Action | Description | Parameters |
|--------|-------------|------------|
| `click` | Click mouse | `x`, `y`, `button` |
| `double_click` | Double-click mouse | `x`, `y`, `button` |
| `scroll` | Scroll mouse wheel | `x`, `y`, `delta_x`, `delta_y` |
| `type` | Type text | `text`, `x`, `y`, `delay` |
| `press_key` | Press keyboard key | `key`, `modifier` |
| `move_mouse` | Move mouse cursor | `x`, `y`, `relative` |
| `wait` | Wait | `seconds` |
| `focus` | Focus window/element | `target` |
| `screenshot` | Take screenshot | `x`, `y`, `width`, `height`, `fullscreen` |

## Integration with Desktop Environments

To connect to a real desktop environment like E2B, set a custom action executor:

```python
from surf import SurfAgent, SurfConfig, ActionResult
from surf.actions import BaseAction

def e2b_executor(action: BaseAction) -> ActionResult:
    # Convert action to E2B format and send to desktop
    if action.action_type == "click":
        # Send click to E2B
        e2b.click(x=action.params["x"], y=action.params["y"])
        return ActionResult(success=True, message="Click executed")
    # ... handle other action types
    return ActionResult(success=False, message="Action not supported")

config = SurfConfig(...)
with SurfAgent(config) as agent:
    agent.set_action_executor(e2b_executor)
    result = agent.run("Click on the start menu")
```

## Web Interface

The HTML web interface allows you to:

- Configure your LLM provider (base URL, API key, model)
- Enter natural language instructions
- See generated actions in real-time
- View execution results

### Screenshot

The web UI features a modern dark theme with:
- Configuration panel with presets for popular providers
- Command input with example buttons
- Real-time action execution display
- Status bar with API health and stats

## Examples

See the `examples/` directory for more usage examples:

- `basic_usage.py` - Basic usage with different providers
- More examples coming soon!

## Container Deployment Guide

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SURF_API_KEY` | Yes | - | Your LLM API key |
| `SURF_BASE_URL` | No | `https://api.openai.com/v1` | LLM API base URL |
| `SURF_MODEL` | No | `gpt-4o-mini` | Model to use |
| `SURF_VERBOSE` | No | `false` | Enable verbose logging |
| `PORT` | No | `8080` | Web server port |
| `HOST` | No | `0.0.0.0` | Web server host |

### Docker Build & Run

```bash
# Build the image
docker build -t surf-ai-agent .

# Run with environment variables
docker run -p 8080:8080 \
  -e SURF_API_KEY=your-api-key \
  -e SURF_BASE_URL=https://api.openai.com/v1 \
  -e SURF_MODEL=gpt-4o-mini \
  surf-ai-agent

# Run with docker-compose
docker-compose up -d
```

### Resource Requirements

- **Memory**: 512MB minimum, 2GB recommended
- **CPU**: 1 vCPU minimum, 2+ vCPU for better performance
- **Storage**: < 500MB
- **Port**: 8080 (configurable via `PORT` env var)

### Free Container Platforms

#### RunPod (Recommended)
- Free tier: 1 vCPU, 4GB RAM
- GPU options available
- Perfect for Surf

#### Railway
- Free tier: 1 vCPU, 2GB RAM
- Easy deployment
- Automatic HTTPS

#### Render
- Free tier: 1 vCPU, 1GB RAM
- Web service deployment
- Automatic scaling

#### Fly.io
- Free tier: 2 vCPU, 3GB RAM
- Global edge network
- Great for low-latency

#### Replit
- Free containers
- Easy to set up
- Built-in editor

#### Hugging Face Spaces
- Free hosting for ML apps
- GPU support
- Great for demos

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.
