# Surf - Computer Use AI Agent

Surf is a flexible, open-source AI agent that enables computer use through natural language instructions. It can interact with GUI environments by generating and executing actions like click, double-click, scroll, type, press keys, and more.

## Features

- **Multi-Provider Support**: Works with any LLM provider (OpenAI, local LLMs, custom providers)
- **Configurable**: Set your base URL and API key for any compatible API
- **Extensible Actions**: Support for mouse clicks, keyboard input, scrolling, and more
- **Natural Language Interface**: Describe what you want to do in plain English
- **Programmatic Control**: Execute pre-defined actions or let the LLM generate them

## Installation

```bash
pip install surf-ai-agent
```

Or from source:

```bash
git clone https://github.com/madgeret-del/surf.git
cd surf
pip install -r requirements.txt
```

## Quick Start

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

## Examples

See the `examples/` directory for more usage examples:

- `basic_usage.py` - Basic usage with different providers
- More examples coming soon!

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.
