#!/usr/bin/env python3
"""
Basic usage example for Surf AI Agent.

This demonstrates how to use the Surf agent with different LLM providers
by configuring the base URL and API key.
"""

import os
from surf import SurfAgent, SurfConfig

def example_openai():
    """Example using OpenAI API."""
    print("=== OpenAI Example ===")
    
    # Create configuration
    config = SurfConfig(
        base_url="https://api.openai.com/v1",
        api_key=os.environ.get("OPENAI_API_KEY"),
        model="gpt-4o-mini",
        verbose=True
    )
    
    # Create agent
    with SurfAgent(config) as agent:
        # Run with natural language instruction
        result = agent.run("Click at coordinates 100, 200 and then type 'Hello World'")
        
        print(f"Success: {result.success}")
        print(f"Message: {result.message}")
        print(f"Actions executed: {len(result.actions_executed)}")
        for i, action in enumerate(result.actions_executed):
            print(f"  {i+1}. {action}")


def example_local_llm():
    """Example using a local LLM (like Ollama, LM Studio, etc.)."""
    print("\n=== Local LLM Example ===")
    
    # Create configuration for local LLM
    # This assumes you have a local provider running on http://localhost:11434
    config = SurfConfig(
        base_url="http://localhost:11434/v1",
        api_key="not-needed",  # Some local providers don't need API keys
        model="llama3.2",
        verbose=True
    )
    
    # Create agent
    with SurfAgent(config) as agent:
        # Run with natural language instruction
        result = agent.run("Move the mouse to 500, 300 and double-click")
        
        print(f"Success: {result.success}")
        print(f"Message: {result.message}")
        for action in result.actions_executed:
            print(f"  - {action}")


def example_custom_provider():
    """Example using a custom LLM provider."""
    print("\n=== Custom Provider Example ===")
    
    # Create configuration for custom provider
    config = SurfConfig(
        base_url="https://your-custom-provider.com/api/v1",
        api_key=os.environ.get("CUSTOM_API_KEY"),
        model="custom-model",
        verbose=True,
        # Add custom headers if needed
        headers={
            "X-Custom-Header": "custom-value"
        }
    )
    
    # Create agent
    with SurfAgent(config) as agent:
        # Run with natural language instruction
        result = agent.run("Press Ctrl+S to save, then wait 2 seconds")
        
        print(f"Success: {result.success}")
        print(f"Message: {result.message}")


def example_programmatic_actions():
    """Example using pre-defined actions instead of LLM."""
    print("\n=== Programmatic Actions Example ===")
    
    from surf.actions import ClickAction, TypeAction, WaitAction
    
    # Create configuration (LLM not needed for this example)
    config = SurfConfig(
        base_url="https://api.openai.com/v1",
        api_key="dummy",  # Not used in this example
        verbose=True
    )
    
    # Create agent
    with SurfAgent(config) as agent:
        # Create actions programmatically
        actions = [
            ClickAction(x=100, y=200),
            TypeAction(text="Hello from programmatic actions!"),
            WaitAction(seconds=1.0),
            ClickAction(x=300, y=400, button="right")
        ]
        
        # Run the actions
        result = agent.run_actions(actions)
        
        print(f"Success: {result.success}")
        print(f"Message: {result.message}")


def example_from_env():
    """Example loading configuration from environment variables."""
    print("\n=== Environment Variables Example ===")
    
    # Set environment variables (in practice, set these before running)
    # os.environ["SURF_BASE_URL"] = "https://api.openai.com/v1"
    # os.environ["SURF_API_KEY"] = "your-api-key"
    # os.environ["SURF_MODEL"] = "gpt-4"
    # os.environ["SURF_VERBOSE"] = "1"
    
    # Create configuration from environment
    config = SurfConfig.from_env(
        model="gpt-4o-mini",  # Override model
        verbose=True
    )
    
    print(f"Loaded config: {config.to_dict()}")
    
    # Create agent
    with SurfAgent(config) as agent:
        result = agent.run("Scroll down by 100 pixels")
        print(f"Result: {result.message}")


if __name__ == "__main__":
    print("Surf AI Agent - Basic Usage Examples\n")
    
    # Note: These examples will only show simulated actions
    # In a real implementation, you would connect to a desktop environment
    # like E2B to actually execute the actions
    
    try:
        example_openai()
    except Exception as e:
        print(f"OpenAI example failed (expected if no API key): {e}")
    
    try:
        example_local_llm()
    except Exception as e:
        print(f"Local LLM example failed (expected if no local server): {e}")
    
    try:
        example_custom_provider()
    except Exception as e:
        print(f"Custom provider example failed (expected if no API): {e}")
    
    # These examples don't need API access
    example_programmatic_actions()
    example_from_env()
    
    print("\n=== All examples completed ===")
