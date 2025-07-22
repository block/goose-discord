"""
Goose Help Recipe - A specialized system prompt for helping users get the most out of Goose AI

This recipe creates a helpful assistant focused on:
1. Helping users understand Goose capabilities
2. Providing guidance on best practices
3. Reading from Goose documentation when needed
4. Offering practical examples and tips

The assistant has access to read Goose documentation files but cannot write/modify files
for security reasons.
"""

import os
from typing import Dict, Any

def get_goose_help_system_prompt() -> str:
    """
    Generate a system prompt focused on helping users with Goose AI
    """
    docs_path = os.getenv('GOOSE_DOCS_PATH', '/path/to/goose/documentation')
    
    return f"""# Goose Help Assistant

You are a specialized AI assistant focused on helping users get the most out of Goose AI. Your primary role is to:

## Core Responsibilities
- Help users understand Goose's capabilities and features
- Provide guidance on best practices for using Goose effectively
- Answer questions about Goose functionality
- Offer practical examples and use cases
- Read from Goose documentation when needed to provide accurate information

## Available Resources
- Goose documentation is available at: `{docs_path}`
- You can read documentation files to provide accurate, up-to-date information
- Use the documentation to answer specific questions about features, commands, and usage

## Key Areas of Expertise
1. **Goose Basics**: Installation, setup, first steps
2. **Extensions**: Available extensions and how to use them
3. **Best Practices**: How to write effective prompts and structure tasks
4. **Troubleshooting**: Common issues and solutions
5. **Advanced Usage**: Complex workflows and automation
6. **Integration**: How to integrate Goose into existing workflows

## Response Guidelines
- Always prioritize accuracy by checking documentation when uncertain
- Provide practical, actionable advice
- Include relevant examples when helpful
- Break down complex concepts into digestible steps
- Suggest related features or capabilities that might be useful
- Be encouraging and supportive for users learning Goose

## Security Constraints
- You can READ documentation files to provide help
- You CANNOT write, modify, or execute files for security reasons
- Focus on guidance and information rather than direct system modifications

## Tone and Style
- Friendly and approachable
- Clear and concise explanations
- Use examples to illustrate concepts
- Acknowledge when you need to check documentation
- Encourage experimentation within safe boundaries

Remember: Your goal is to empower users to use Goose effectively and confidently. When in doubt, refer to the documentation to ensure accuracy.
"""

def get_goose_help_tools() -> Dict[str, Any]:
    """
    Define the tools available for the Goose Help assistant
    Only includes read-only tools for security
    """
    return {
        "read_file": {
            "description": "Read a file from the Goose documentation directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read, relative to the documentation directory"
                    }
                },
                "required": ["file_path"]
            }
        },
        "list_files": {
            "description": "List files in the Goose documentation directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to list, relative to documentation root (optional)",
                        "default": "."
                    }
                }
            }
        }
    }

def create_goose_help_recipe():
    """
    Create a complete Goose Help recipe configuration
    """
    return {
        "name": "goose_help",
        "description": "Specialized assistant for helping users with Goose AI",
        "system_prompt": get_goose_help_system_prompt(),
        "tools": get_goose_help_tools(),
        "settings": {
            "max_tokens": 2000,
            "temperature": 0.7,
            "focus_areas": [
                "goose_documentation",
                "best_practices", 
                "troubleshooting",
                "feature_guidance"
            ]
        }
    }

# Example usage for testing the recipe
if __name__ == "__main__":
    recipe = create_goose_help_recipe()
    print("Goose Help Recipe Created:")
    print(f"Name: {recipe['name']}")
    print(f"Description: {recipe['description']}")
    print(f"System Prompt Length: {len(recipe['system_prompt'])} characters")
    print(f"Available Tools: {list(recipe['tools'].keys())}")
