"""
Surf AI Agent - Main agent class for computer use AI.

The agent uses an LLM to understand natural language instructions
and generates/executes GUI actions to interact with a desktop environment.
"""

import json
import re
from typing import Optional, Dict, Any, List, Tuple, Callable
from dataclasses import dataclass, field
import time

from .config import SurfConfig
from .llm_client import LLMClient, Message
from .actions import (
    BaseAction,
    ClickAction,
    DoubleClickAction,
    ScrollAction,
    TypeAction,
    PressKeyAction,
    MoveMouseAction,
    WaitAction,
    FocusAction,
    ScreenshotAction,
    ActionResult,
    ACTION_CLASSES,
    parse_action,
    parse_actions_json,
    actions_to_json,
)


@dataclass
class AgentResult:
    """Result of an agent execution."""
    success: bool
    message: str
    actions_executed: List[BaseAction] = field(default_factory=list)
    actions_failed: List[Tuple[BaseAction, str]] = field(default_factory=list)
    llm_response: Optional[str] = None
    error: Optional[str] = None


class SurfAgent:
    """
    AI Agent for computer use via natural language.
    
    This agent:
    1. Takes natural language instructions
    2. Uses an LLM to generate appropriate GUI actions
    3. Executes those actions (or would in a connected environment)
    
    Example:
        agent = SurfAgent(config)
        result = agent.run("Open the calculator and click on the '5' button")
    """
    
    # Available action types for the LLM to use
    ACTION_TYPES = {
        "click": {
            "description": "Click the mouse at specific coordinates",
            "params": {
                "x": "X coordinate (integer)",
                "y": "Y coordinate (integer)",
                "button": "Mouse button: 'left', 'right', or 'middle' (default: 'left')"
            },
            "required": ["x", "y"]
        },
        "double_click": {
            "description": "Double-click the mouse",
            "params": {
                "x": "X coordinate",
                "y": "Y coordinate",
                "button": "Mouse button (default: 'left')"
            },
            "required": ["x", "y"]
        },
        "scroll": {
            "description": "Scroll the mouse wheel",
            "params": {
                "x": "X coordinate (optional)",
                "y": "Y coordinate (optional)",
                "delta_x": "Horizontal scroll amount",
                "delta_y": "Vertical scroll amount"
            },
            "required": []
        },
        "type": {
            "description": "Type text at current position or specific coordinates",
            "params": {
                "text": "Text to type",
                "x": "X coordinate (optional)",
                "y": "Y coordinate (optional)",
                "delay": "Delay between keystrokes in seconds (default: 0.05)"
            },
            "required": ["text"]
        },
        "press_key": {
            "description": "Press a keyboard key",
            "params": {
                "key": "Key to press (e.g., 'Enter', 'Tab', 'a')",
                "modifier": "Modifier key: 'ctrl', 'shift', 'alt', 'meta' (optional)"
            },
            "required": ["key"]
        },
        "move_mouse": {
            "description": "Move the mouse cursor",
            "params": {
                "x": "X coordinate",
                "y": "Y coordinate",
                "relative": "If True, coordinates are relative to current position (default: False)"
            },
            "required": ["x", "y"]
        },
        "wait": {
            "description": "Wait for a specified time",
            "params": {
                "seconds": "Time to wait in seconds (default: 1.0)"
            },
            "required": []
        },
        "focus": {
            "description": "Focus on a window or element",
            "params": {
                "target": "Window title or element identifier"
            },
            "required": ["target"]
        },
        "screenshot": {
            "description": "Take a screenshot",
            "params": {
                "x": "X coordinate for screenshot region (optional)",
                "y": "Y coordinate for screenshot region (optional)",
                "width": "Width of screenshot region (optional)",
                "height": "Height of screenshot region (optional)",
                "fullscreen": "Take fullscreen screenshot (default: True)"
            },
            "required": []
        }
    }
    
    def __init__(self, config: SurfConfig):
        """
        Initialize the Surf AI Agent.
        
        Args:
            config: SurfConfig with LLM and agent settings
        """
        self.config = config
        self.llm = LLMClient(config)
        self.action_executor: Optional[Callable[[BaseAction], ActionResult]] = None
        
        # Build the system prompt
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the LLM."""
        action_descriptions = []
        for action_name, action_info in self.ACTION_TYPES.items():
            desc = action_info["description"]
            params = ", ".join([f"{k}: {v}" for k, v in action_info["params"].items()])
            required = action_info.get("required", [])
            req_str = f" (Required: {', '.join(required)})" if required else ""
            action_descriptions.append(f"- {action_name}: {desc}. Parameters: {params}{req_str}")
        
        actions_str = "\n".join(action_descriptions)
        
        return f"""You are a Computer Use AI Agent. Your task is to help users interact with a desktop GUI environment by generating appropriate actions based on their natural language instructions.

You have access to the following GUI actions:
{actions_str}

For each instruction, respond with a JSON array of actions to perform. Each action must have:
- "type": The action type (one of: {', '.join(list(self.ACTION_TYPES.keys()))})
- "params": An object with the required parameters for that action type

Example responses:
- Click at coordinates: [{{ "type": "click", "params": {{ "x": 100, "y": 200 }} }}]
- Type text: [{{ "type": "type", "params": {{ "text": "Hello World" }} }}]
- Multiple actions: [{{ "type": "move_mouse", "params": {{ "x": 100, "y": 200 }} }}, {{ "type": "click", "params": {{ "x": 100, "y": 200 }} }}]

IMPORTANT:
1. Only respond with valid JSON - no other text, explanations, or markdown
2. Always use a JSON array (even for single actions)
3. Make reasonable assumptions about coordinates and parameters
4. For missing required information, use reasonable defaults or ask the user
5. Break complex tasks into multiple simple actions

Respond ONLY with the JSON array of actions, nothing else."""
    
    def _parse_llm_response(self, response: str) -> List[BaseAction]:
        """
        Parse the LLM response to extract actions.
        
        Args:
            response: Raw text response from LLM
            
        Returns:
            List of BaseAction instances
            
        Raises:
            ValueError: If response cannot be parsed
        """
        # Try to extract JSON from the response
        # Sometimes LLMs wrap JSON in markdown code blocks
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            json_str = response.strip()
        
        # Try to parse as JSON
        try:
            parsed = json.loads(json_str)
            if isinstance(parsed, list):
                return [parse_action(action) for action in parsed]
            elif isinstance(parsed, dict):
                return [parse_action(parsed)]
            else:
                raise ValueError(f"Unexpected response format: {type(parsed)}")
        except json.JSONDecodeError:
            # Try to extract from markdown code blocks
            code_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response, re.DOTALL)
            if code_match:
                try:
                    parsed = json.loads(code_match.group(1))
                    if isinstance(parsed, list):
                        return [parse_action(action) for action in parsed]
                    elif isinstance(parsed, dict):
                        return [parse_action(parsed)]
                except json.JSONDecodeError:
                    pass
            
            raise ValueError(f"Could not parse LLM response as JSON: {response[:200]}")
    
    def _generate_actions(self, instruction: str, context: Optional[str] = None) -> List[BaseAction]:
        """
        Generate actions from a natural language instruction.
        
        Args:
            instruction: Natural language instruction
            context: Optional context about current state
            
        Returns:
            List of actions to execute
        """
        messages: List[Message] = []
        
        # Add system message
        messages.append(Message(role="system", content=self.system_prompt))
        
        # Add context if provided
        if context:
            messages.append(Message(role="system", content=f"Current context: {context}"))
        
        # Add user instruction
        messages.append(Message(role="user", content=instruction))
        
        # Get LLM response
        response = self.llm.chat(messages, temperature=self.config.temperature)
        
        if self.config.verbose:
            print(f"[Surf Agent] LLM Response: {response.content[:500]}")
        
        # Parse actions from response
        actions = self._parse_llm_response(response.content)
        
        return actions
    
    def _execute_action(self, action: BaseAction, **kwargs: Any) -> ActionResult:
        """
        Execute a single action.
        
        Args:
            action: Action to execute
            **kwargs: Additional parameters
            
        Returns:
            ActionResult with execution outcome
        """
        if self.action_executor:
            return self.action_executor(action, **kwargs)
        else:
            # Default execution (simulated)
            return action.execute(verbose=self.config.verbose, **kwargs)
    
    def run(self, instruction: str, context: Optional[str] = None, 
            max_actions: Optional[int] = None) -> AgentResult:
        """
        Run the agent with a natural language instruction.
        
        Args:
            instruction: Natural language instruction
            context: Optional context about current state
            max_actions: Override max actions limit (default: from config)
            
        Returns:
            AgentResult with execution outcome
        """
        if max_actions is None:
            max_actions = self.config.max_actions
        
        actions_executed: List[BaseAction] = []
        actions_failed: List[Tuple[BaseAction, str]] = []
        
        try:
            # Generate actions from instruction
            actions = self._generate_actions(instruction, context)
            
            if self.config.verbose:
                print(f"[Surf Agent] Generated {len(actions)} actions")
                for i, action in enumerate(actions):
                    print(f"  {i+1}. {action}")
            
            # Limit actions
            if len(actions) > max_actions:
                if self.config.verbose:
                    print(f"[Surf Agent] Truncating to {max_actions} actions")
                actions = actions[:max_actions]
            
            # Execute each action
            for action in actions:
                if self.config.verbose:
                    print(f"[Surf Agent] Executing: {action}")
                
                try:
                    result = self._execute_action(action)
                    
                    if result.success:
                        actions_executed.append(action)
                        if self.config.verbose:
                            print(f"[Surf Agent] Success: {result.message}")
                    else:
                        actions_failed.append((action, result.error or result.message))
                        if self.config.verbose:
                            print(f"[Surf Agent] Failed: {result.message}")
                        
                        # Stop on failure by default
                        break
                        
                except Exception as e:
                    actions_failed.append((action, str(e)))
                    if self.config.verbose:
                        print(f"[Surf Agent] Error: {e}")
                    break
            
            return AgentResult(
                success=len(actions_failed) == 0,
                message=f"Executed {len(actions_executed)} actions, {len(actions_failed)} failed",
                actions_executed=actions_executed,
                actions_failed=actions_failed,
                llm_response=None
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                message=str(e),
                error=str(e),
                actions_executed=actions_executed,
                actions_failed=actions_failed
            )
    
    def run_actions(self, actions: List[BaseAction]) -> AgentResult:
        """
        Run a pre-defined list of actions.
        
        Args:
            actions: List of BaseAction instances to execute
            
        Returns:
            AgentResult with execution outcome
        """
        actions_executed: List[BaseAction] = []
        actions_failed: List[Tuple[BaseAction, str]] = []
        
        for action in actions:
            if len(actions_executed) + len(actions_failed) >= self.config.max_actions:
                break
                
            try:
                result = self._execute_action(action)
                
                if result.success:
                    actions_executed.append(action)
                    if self.config.verbose:
                        print(f"[Surf Agent] Success: {result.message}")
                else:
                    actions_failed.append((action, result.error or result.message))
                    if self.config.verbose:
                        print(f"[Surf Agent] Failed: {result.message}")
                    break
                    
            except Exception as e:
                actions_failed.append((action, str(e)))
                if self.config.verbose:
                    print(f"[Surf Agent] Error: {e}")
                break
        
        return AgentResult(
            success=len(actions_failed) == 0,
            message=f"Executed {len(actions_executed)} actions, {len(actions_failed)} failed",
            actions_executed=actions_executed,
            actions_failed=actions_failed
        )
    
    def set_action_executor(self, executor: Callable[[BaseAction], ActionResult]) -> None:
        """
        Set a custom action executor.
        
        This allows integration with real desktop environments like E2B.
        
        Args:
            executor: Function that takes a BaseAction and returns ActionResult
        """
        self.action_executor = executor
    
    def get_available_actions(self) -> Dict[str, Dict[str, Any]]:
        """Get descriptions of all available action types."""
        return self.ACTION_TYPES.copy()
    
    def close(self) -> None:
        """Close the agent and cleanup resources."""
        self.llm.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
