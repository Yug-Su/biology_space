"""
Test script to verify API keys for OpenRouter and Groq
"""

import httpx
import os
import sys
import asyncio
import django

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spacebio.settings')
django.setup()

from django.conf import settings

OPENROUTER_API_KEY = settings.OPENROUTER_API_KEY
OPENROUTER_BASE_URL = settings.OPENROUTER_BASE_URL
GROQ_API_KEY = settings.GROQ_API_KEY
GROQ_BASE_URL = settings.GROQ_BASE_URL


async def test_openrouter():
    """Test OpenRouter API key"""
    print("\n🔍 Testing OpenRouter API...")
    print(f"   API Key: {OPENROUTER_API_KEY[:20]}..." if OPENROUTER_API_KEY else "   ❌ No API key found")

    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == 'your-openrouter-api-key':
        print("   ❌ Invalid or missing API key")
        return False

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "SpaceBio Test"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "Say 'test successful' in French"}],
                    "max_tokens": 20
                },
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                message = data['choices'][0]['message']['content']
                print(f"   ✅ OpenRouter API is working!")
                print(f"   Response: {message}")
                return True
            elif response.status_code == 402:
                print(f"   ❌ Payment Required (402) - No credits available")
                print(f"   Add credits at: https://openrouter.ai/credits")
                return False
            elif response.status_code == 401:
                print(f"   ❌ Unauthorized (401) - Invalid API key")
                return False
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
                return False

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False


async def test_groq():
    """Test Groq API key"""
    print("\n🔍 Testing Groq API...")
    print(f"   API Key: {GROQ_API_KEY[:20]}..." if GROQ_API_KEY else "   ❌ No API key found")

    if not GROQ_API_KEY or GROQ_API_KEY == 'your-groq-api-key':
        print("   ❌ Invalid or missing API key")
        return False

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GROQ_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-70b-versatile",
                    "messages": [{"role": "user", "content": "Say 'test successful' in French"}],
                    "max_tokens": 20
                },
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                message = data['choices'][0]['message']['content']
                print(f"   ✅ Groq API is working!")
                print(f"   Response: {message}")
                return True
            elif response.status_code == 401:
                print(f"   ❌ Unauthorized (401) - Invalid API key")
                return False
            elif response.status_code == 400:
                print(f"   ❌ Bad Request (400)")
                print(f"   Response: {response.text}")
                # Try with different model
                print("\n   Trying with mixtral-8x7b-32768...")
                response2 = await client.post(
                    f"{GROQ_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "mixtral-8x7b-32768",
                        "messages": [{"role": "user", "content": "Say 'test successful' in French"}],
                        "max_tokens": 20
                    },
                    timeout=30.0
                )
                if response2.status_code == 200:
                    data = response2.json()
                    message = data['choices'][0]['message']['content']
                    print(f"   ✅ Groq API works with mixtral-8x7b-32768!")
                    print(f"   Response: {message}")
                    print(f"   💡 Consider changing FALLBACK_AI_MODEL to 'mixtral-8x7b-32768'")
                    return True
                else:
                    print(f"   ❌ Also failed with mixtral: {response2.status_code}")
                    return False
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
                return False

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False


async def main():
    print("=" * 60)
    print("🔑 API Keys Test - SpaceBio Platform")
    print("=" * 60)

    openrouter_ok = await test_openrouter()
    groq_ok = await test_groq()

    print("\n" + "=" * 60)
    print("📊 RESULTS:")
    print("=" * 60)
    print(f"OpenRouter: {'✅ Working' if openrouter_ok else '❌ Failed'}")
    print(f"Groq:       {'✅ Working' if groq_ok else '❌ Failed'}")

    if openrouter_ok or groq_ok:
        print("\n✅ At least one API provider is working!")
        if not openrouter_ok:
            print("💡 Suggestion: Use Groq as PRIMARY_AI_MODEL in .env")
    else:
        print("\n❌ No working API providers found!")
        print("\n📝 Next steps:")
        print("   1. Get new API keys:")
        print("      - OpenRouter: https://openrouter.ai/keys")
        print("      - Groq: https://console.groq.com/keys")
        print("   2. Update your .env file with the new keys")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
