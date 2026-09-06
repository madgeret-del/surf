"""
GUI Action classes for Surf AI Agent.

Defines the available actions that can be performed on a GUI/desktop environment.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple, Union
import json
import time


@dataclass
class ActionResult:
    """Result of an action execution."""
    success: bool
    message: str
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class BaseAction:
    """Base class for all GUI actions."""
    
    action_type: str = "base"
    
    def __init__(self, **kwargs: Any):
        self.params = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize action to dictionary."""
        return {
            "type": self.action_type,
            "params": self.params
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseAction":
        """Deserialize action from dictionary."""
        return cls(**data.get("params", {}))
    
    def execute(self, **kwargs: Any) -> ActionResult:
        """
        Execute the action.
        
        This should be overridden by subclasses.
        In a real implementation, this would connect to a desktop environment
        like E2B and send the action.
        """
        raise NotImplementedError("Execute must be implemented by subclasses")
    
    def __str__(self) -> str:
        return f"{self.action_type}({json.dumps(self.params)})"


@dataclass
class ClickAction(BaseAction):
    """Mouse click action."""
    action_type: str = "click"
    x: int = 0
    y: int = 0
    button: str = "left"  # left, right, middle
    
    def __init__(self, x: int, y: int, button: str = "left", **kwargs: Any):
        super().__init__(x=x, y=y, button=button, **kwargs)
    
    def execute(self, verbose: bool = False, **kwargs: Any) -> ActionResult:
        """Execute the click action."""
        # In a real implementation, this would send the click to the desktop
        if verbose:
            print(f"[Surf Action] Click at ({self.x}, {self.y}) with {self.button} button")
        return ActionResult(
            success=True,
            message=f"Clicked at ({self.x}, {self.y}) with {self.button} button"
        )


@dataclass
class DoubleClickAction(BaseAction):
    """Mouse double-click action."""
    action_type: str = "double_click"
    x: int = 0
    y: int = 0
    button: str = "left"
    
    def __init__(self, x: int, y: int, button: str = "left", **kwargs: Any):
        super().__init__(x=x, y=y, button=button, **kwargs)
    
    def execute(self, verbose: bool = False, **kwargs: Any) -> ActionResult:
        """Execute the double-click action."""
        if verbose:
            print(f"[Surf Action] Double click at ({self.x}, {self.y}) with {self.button} button")
        return ActionResult(
            success=True,
            message=f"Double clicked at ({self.x}, {self.y}) with {self.button} button"
        )


@dataclass
class ScrollAction(BaseAction):
    """Mouse scroll action."""
    action_type: str = "scroll"
    x: int = 0
    y: int = 0
    delta_x: int = 0
    delta_y: int = 0
    
    def __init__(self, x: int = 0, y: int = 0, delta_x: int = 0, delta_y: int = 0, **kwargs: Any):
        super().__init__(x=x, y=y, delta_x=delta_x, delta_y=delta_y, **kwargs)
    
    def execute(self, verbose: bool = False, **kwargs: Any) -> ActionResult:
        """Execute the scroll action."""
        if verbose:
            print(f"[Surf Action] Scroll at ({self.x}, {self.y}) by ({self.delta_x}, {self.delta_y})")
        return ActionResult(
            success=True,
            message=f"Scrolled at ({self.x}, {self.y}) by ({self.delta_x}, {self.delta_y})"
        )


@dataclass
class TypeAction(BaseAction):
    """Type text action."""
    action_type: str = "type"
    text: str = ""
    x: Optional[int] = None
    y: Optional[int] = None
    delay: float = 0.05  # Delay between keystrokes in seconds
    
    def __init__(self, text: str, x: Optional[int] = None, y: Optional[int] = None, delay: float = 0.05, **kwargs: Any):
        super().__init__(text=text, x=x, y=y, delay=delay, **kwargs)
    
    def execute(self, verbose: bool = False, **kwargs: Any) -> ActionResult:
        """Execute the type action."""
        if verbose:
            print(f"[Surf Action] Type text: {self.text[:50]}...")
        return ActionResult(
            success=True,
            message=f"Typed text: {self.text[:50]}..." if len(self.text) > 50 else f"Typed text: {self.text}"
        )


@dataclass
class PressKeyAction(BaseAction):
    """Press a key action."""
    action_type: str = "press_key"
    key: str = ""
    modifier: Optional[str] = None  # ctrl, shift, alt, meta
    
    def __init__(self, key: str, modifier: Optional[str] = None, **kwargs: Any):
        super().__init__(key=key, modifier=modifier, **kwargs)
    
    def execute(self, verbose: bool = False, **kwargs: Any) -> ActionResult:
        """Execute the press key action."""
        mod = f"+{self.modifier}" if self.modifier else ""
        if verbose:
            print(f"[Surf Action] Press key: {mod}{self.key}")
        return ActionResult(
            success=True,
            message=f"Pressed key: {mod}{self.key}"
        )


@dataclass
class MoveMouseAction(BaseAction):
    """Move mouse action."""
    action_type: str = "move_mouse"
    x: int = 0
    y: int = 0
    relative: bool = False  # If True, coordinates are relative to current position
    
    def __init__(self, x: int, y: int, relative: bool = False, **kwargs: Any):
        super().__init__(x=x, y=y, relative=relative, **kwargs)
    
    def execute(self, verbose: bool = False, **kwargs: Any) -> ActionResult:
        """Execute the move mouse action."""
        rel = "relative " if self.relative else ""
        if verbose:
            print(f"[Surf Action] Move mouse {rel}to ({self.x}, {self.y})")
        return ActionResult(
            success=True,
            message=f"Moved mouse {rel}to ({self.x}, {self.y})"
        )


@dataclass
class WaitAction(BaseAction):
    """Wait action."""
    action_type: str = "wait"
    seconds: float = 1.0
    
    def __init__(self, seconds: float = 1.0, **kwargs: Any):
        super().__init__(seconds=seconds, **kwargs)
    
    def execute(self, verbose: bool = False, **kwargs: Any) -> ActionResult:
        """Execute the wait action."""
        time.sleep(self.seconds)
        if verbose:
            print(f"[Surf Action] Waited for {self.seconds} seconds")
        return ActionResult(
            success=True,
            message=f"Waited for {self.seconds} seconds"
        )


@dataclass
class FocusAction(BaseAction):
    """Focus on a window or element action."""
    action_type: str = "focus"
    target: str = ""  # Window title, element selector, etc.
    
    def __init__(self, target: str, **kwargs: Any):
        super().__init__(target=target, **kwargs)
    
    def execute(self, verbose: bool = False, **kwargs: Any) -> ActionResult:
        """Execute the focus action."""
        if verbose:
            print(f"[Surf Action] Focus on: {self.target}")
        return ActionResult(
            success=True,
            message=f"Focused on: {self.target}"
        )


@dataclass
class ScreenshotAction(BaseAction):
    """Take a screenshot action."""
    action_type: str = "screenshot"
    x: Optional[int] = None
    y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fullscreen: bool = True
    
    def __init__(self, x: Optional[int] = None, y: Optional[int] = None, 
                 width: Optional[int] = None, height: Optional[int] = None,
                 fullscreen: bool = True, **kwargs: Any):
        super().__init__(x=x, y=y, width=width, height=height, fullscreen=fullscreen, **kwargs)
    
    def execute(self, verbose: bool = False, **kwargs: Any) -> ActionResult:
        """Execute the screenshot action."""
        if verbose:
            print(f"[Surf Action] Take screenshot")
        return ActionResult(
            success=True,
            message="Screenshot taken"
        )


# Action registry
ACTION_CLASSES = {
    "click": ClickAction,
    "double_click": DoubleClickAction,
    "scroll": ScrollAction,
    "type": TypeAction,
    "press_key": PressKeyAction,
    "move_mouse": MoveMouseAction,
    "wait": WaitAction,
    "focus": FocusAction,
    "screenshot": ScreenshotAction,
}


def parse_action(data: Dict[str, Any]) -> BaseAction:
    """
    Parse action from dictionary.
    
    Args:
        data: Dictionary with 'type' and 'params' keys
        
    Returns:
        Action instance
        
    Raises:
        ValueError: If action type is unknown
    """
    action_type = data.get("type", "")
    if action_type not in ACTION_CLASSES:
        raise ValueError(f"Unknown action type: {action_type}")
    return ACTION_CLASSES[action_type].from_dict(data)


def parse_actions_json(json_str: str) -> List[BaseAction]:
    """
    Parse multiple actions from JSON string.
    
    Args:
        json_str: JSON string containing list of actions
        
    Returns:
        List of Action instances
    """
    try:
        actions_data = json.loads(json_str)
        if not isinstance(actions_data, list):
            actions_data = [actions_data]
        return [parse_action(action) for action in actions_data]
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
    except Exception as e:
        raise ValueError(f"Failed to parse actions: {e}")


def actions_to_json(actions: List[BaseAction]) -> str:
    """
    Serialize actions to JSON string.
    
    Args:
        actions: List of Action instances
        
    Returns:
        JSON string
    """
    return json.dumps([action.to_dict() for action in actions], indent=2)
