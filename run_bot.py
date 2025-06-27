#!/usr/bin/env python3
"""
Simple script to run Agent Honk Discord bot
"""

import sys
import os
import asyncio

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent_honk.bot import main

if __name__ == "__main__":
    print("🦆 Starting Agent Honk...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🦆 Agent Honk is flying away... Goodbye!")
    except Exception as e:
        print(f"🦆 Error: {e}")
        sys.exit(1)
