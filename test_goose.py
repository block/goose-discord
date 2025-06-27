#!/usr/bin/env python3
"""
Test script to verify Goose CLI integration works correctly
"""

import asyncio
import tempfile
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent_honk.goose_client import GooseClient

async def test_goose_client():
    print("🦆 Testing Goose CLI integration...")
    
    client = GooseClient()
    
    # Test 1: Simple prompt
    print("\n📝 Test 1: Simple prompt")
    result = await client.run_initial("test_thread_123", "Hello! Tell me a fun fact about ducks.")
    
    if result:
        print(f"✅ Success! Response: {result[:100]}...")
    else:
        print("❌ Failed to get response")
        return False
    
    # Test 2: Follow-up message
    print("\n📝 Test 2: Follow-up message")
    history = [
        {"role": "user", "content": "Hello! Tell me a fun fact about ducks."},
        {"role": "assistant", "content": result},
        {"role": "user", "content": "Tell me another one!"}
    ]
    
    result2 = await client.run_with_history("test_thread_123", history)
    
    if result2:
        print(f"✅ Success! Follow-up response: {result2[:100]}...")
    else:
        print("❌ Failed to get follow-up response")
        return False
    
    # Cleanup
    client.cleanup_session("test_thread_123")
    print("\n🧹 Cleaned up test session")
    
    return True

async def test_goose_command():
    """Test raw goose command to make sure it works"""
    print("\n🔧 Testing raw goose command...")
    
    try:
        # Test the basic command structure
        process = await asyncio.create_subprocess_exec(
            'goose', 'run', '--text', 'Say hello',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=tempfile.mkdtemp()
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
        
        if process.returncode == 0:
            print("✅ Raw goose command works!")
            print(f"Response: {stdout.decode('utf-8')[:100]}...")
            return True
        else:
            print(f"❌ Goose command failed: {stderr.decode('utf-8')}")
            return False
            
    except FileNotFoundError:
        print("❌ Goose command not found! Make sure Goose is installed.")
        return False
    except Exception as e:
        print(f"❌ Error testing goose command: {e}")
        return False

if __name__ == "__main__":
    async def main():
        print("🦆 Agent Honk - Goose Integration Test")
        print("=" * 40)
        
        # Test raw command first
        if not await test_goose_command():
            print("\n❌ Basic goose command test failed. Please check your Goose installation.")
            return
        
        # Test our client
        if await test_goose_client():
            print("\n🎉 All tests passed! Agent Honk should work correctly now.")
        else:
            print("\n❌ Client tests failed. Check the logs above.")
    
    asyncio.run(main())
