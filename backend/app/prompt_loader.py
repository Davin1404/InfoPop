import json
import os
from typing import Dict, Any

def load_prompt_config(prompt_name: str = "AI_Agent_Prompt") -> Dict[str, Any]:
    """
    Load prompt configuration from JSON file
    
    Args:
        prompt_name: Name of the prompt file (without .json extension)
        
    Returns:
        Dictionary containing prompt configuration
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompts_dir = os.path.join(os.path.dirname(current_dir), "prompts")
    prompt_file = os.path.join(prompts_dir, f"{prompt_name}.json")
    
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in prompt file: {e}")

def format_system_prompt(prompt_config: Dict[str, Any]) -> str:
    """
    Format the prompt configuration into a system prompt string
    
    Args:
        prompt_config: Dictionary containing prompt configuration
        
    Returns:
        Formatted system prompt string
    """
    config = prompt_config["system_prompt"]
    
    # Build the prompt string
    prompt_parts = []
    
    # Header
    prompt_parts.append(f"# Role: {config['role']}")
    prompt_parts.append("")
    
    # Profile section
    profile = config["profile"]
    prompt_parts.append("## Profile")
    prompt_parts.append(f"- Author: {profile['author']}")
    prompt_parts.append(f"- Version: {profile['version']}")
    prompt_parts.append(f"- Language: {profile['language']}")
    prompt_parts.append(f"- Description: {profile['description']}")
    prompt_parts.append(f"- 特点：{profile['features']}")
    prompt_parts.append("")
    
    # Main Skills section
    prompt_parts.append("## MainSkills")
    for i, skill in enumerate(config["main_skills"], 1):
        prompt_parts.append(f"{i}. **{skill['name']}**")
        for desc in skill["description"]:
            prompt_parts.append(f"   - {desc}")
        prompt_parts.append("")
    
    # Rules section
    prompt_parts.append("## Rules")
    for i, rule in enumerate(config["rules"], 1):
        prompt_parts.append(f"{i}. **{rule['name']}**：{rule['description']}")
        if isinstance(rule["description"], list):
            prompt_parts[-1] = f"{i}. **{rule['name']}**："
            for desc in rule["description"]:
                prompt_parts.append(f"   - {desc}")
    prompt_parts.append("")
    
    # Structured Output section
    prompt_parts.append("## Structured Output")
    for key, value in config["structured_output"].items():
        prompt_parts.append(f"- **{key}**：{value}")
    prompt_parts.append("")
    
    # Source Reference Handling section
    prompt_parts.append("## Source-Reference Handling")
    prompt_parts.append("- 输出时：")
    for key, value in config["source_reference_handling"].items():
        prompt_parts.append(f"  - 如果{key} → {value}")
    prompt_parts.append("")
    
    # Context instruction
    prompt_parts.append(config["context_instruction"])
    
    return "\n".join(prompt_parts)

def get_system_prompt(prompt_name: str = "AI_Agent_Prompt") -> str:
    """
    Get formatted system prompt for the specified prompt configuration
    
    Args:
        prompt_name: Name of the prompt file (without .json extension)
        
    Returns:
        Formatted system prompt string
    """
    prompt_config = load_prompt_config(prompt_name)
    return format_system_prompt(prompt_config)

# For backward compatibility and easy access
def get_default_system_prompt() -> str:
    """Get the default AI Agent system prompt"""
    return get_system_prompt("AI_Agent_Prompt")
