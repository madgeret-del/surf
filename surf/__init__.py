"""
Surf - Computer Use AI Agent

A flexible AI agent that can interact with GUI environments through natural language.
Supports any LLM provider via configurable base URL and API key.
"""

from .llm_client import LLMClient
from .actions import (
    ClickAction,
    DoubleClickAction,
    ScrollAction,
    TypeAction,
    PressKeyAction,
    WaitAction,
    MoveMouseAction,
)
from .agent import SurfAgent
from .config import SurfConfig

__version__ = "0.1.0"
__all__ = [
    "LLMClient",
    "SurfAgent",
    "SurfConfig",
    "ClickAction",
    "DoubleClickAction",
    "ScrollAction",
    "TypeAction",
    "PressKeyAction",
    "WaitAction",
    "MoveMouseAction",
]
