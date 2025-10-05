"""
Test script to check AI provider connection
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spacebio.settings')
django.setup()

import asyncio
from core.services.ai_providers import ai_provider

async def test_chat():
    """Test chat functionality"""
    try:
        print("Testing AI Chat Provider...\n")

        # Test message
        messages = [
            {"role": "user", "content": "Hello, can you hear me?"}
        ]

        print("Sending test message...")
        response = await ai_provider.chat(messages, max_tokens=100)

        print("SUCCESS!")
        print(f"Response: {response}\n")
        return True

    except Exception as e:
        print(f"ERROR: {e}\n")
        print(f"Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_chat())
    sys.exit(0 if result else 1)
