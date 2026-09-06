"""
Configuration management for Surf AI Agent.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import os


@dataclass
class SurfConfig:
    """
    Configuration for the Surf AI Agent.
    
    Attributes:
        base_url: Base URL for the LLM API (e.g., "https://api.openai.com/v1")
        api_key: API key for authentication
        model: Model name to use (e.g., "gpt-4", "llama-3-70b")
        temperature: Sampling temperature (0.0 to 2.0)
        max_tokens: Maximum tokens in response
        timeout: Request timeout in seconds
        verbose: Enable verbose logging
        action_timeout: Timeout for individual actions in seconds
        max_actions: Maximum number of actions per instruction
    """
    base_url: str = field(default="https://api.openai.com/v1")
    api_key: Optional[str] = field(default=None)
    model: str = field(default="gpt-4")
    temperature: float = field(default=0.7)
    max_tokens: int = field(default=4096)
    timeout: int = field(default=30)
    verbose: bool = field(default=False)
    action_timeout: int = field(default=10)
    max_actions: int = field(default=20)
    
    # Additional headers for custom providers
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Custom request parameters
    extra_params: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.temperature < 0 or self.temperature > 2:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.action_timeout <= 0:
            raise ValueError("action_timeout must be positive")
        if self.max_actions <= 0:
            raise ValueError("max_actions must be positive")
    
    @classmethod
    def from_env(cls, **overrides: Any) -> "SurfConfig":
        """
        Create configuration from environment variables with optional overrides.
        
        Environment variables:
            SURF_BASE_URL: Base URL for LLM API
            SURF_API_KEY: API key
            SURF_MODEL: Model name
            SURF_TEMPERATURE: Temperature
            SURF_MAX_TOKENS: Max tokens
            SURF_TIMEOUT: Timeout in seconds
            SURF_VERBOSE: Verbose logging (1 for True)
        """
        config = cls()
        
        env_mappings = {
            "SURF_BASE_URL": ("base_url", str),
            "SURF_API_KEY": ("api_key", str),
            "SURF_MODEL": ("model", str),
            "SURF_TEMPERATURE": ("temperature", float),
            "SURF_MAX_TOKENS": ("max_tokens", int),
            "SURF_TIMEOUT": ("timeout", int),
            "SURF_VERBOSE": ("verbose", lambda x: x.lower() in ("1", "true", "yes")),
            "SURF_ACTION_TIMEOUT": ("action_timeout", int),
            "SURF_MAX_ACTIONS": ("max_actions", int),
        }
        
        for env_var, (attr, converter) in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                try:
                    setattr(config, attr, converter(value))
                except (ValueError, TypeError):
                    pass
        
        # Apply overrides
        for key, value in overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "base_url": self.base_url,
            "api_key": self.api_key,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "verbose": self.verbose,
            "action_timeout": self.action_timeout,
            "max_actions": self.max_actions,
            "headers": self.headers,
            "extra_params": self.extra_params,
        }
