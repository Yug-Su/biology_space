"""
Test different Groq models to find which ones are available
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

GROQ_API_KEY = settings.GROQ_API_KEY
GROQ_BASE_URL = settings.GROQ_BASE_URL


async def test_groq_model(model_name):
    """Test a specific Groq model"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GROQ_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": "Say 'test ok'"}],
                    "max_tokens": 10
                },
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                message = data['choices'][0]['message']['content']
                return True, f"✅ {model_name}: {message}"
            else:
                error_data = response.json() if response.status_code == 400 else {}
                error_msg = error_data.get('error', {}).get('message', response.text)
                return False, f"❌ {model_name}: {error_msg[:100]}"

    except Exception as e:
        return False, f"❌ {model_name}: {str(e)[:100]}"


async def main():
    print("=" * 70)
    print("Testing Groq Models")
    print("=" * 70)

    # List of models to test based on Groq documentation
    models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "llama3-70b-8192",
        "llama3-8b-8192",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
        "gemma-7b-it"
    ]

    working_models = []

    for model in models:
        success, message = await test_groq_model(model)
        print(message)
        if success:
            working_models.append(model)

    print("\n" + "=" * 70)
    print("SUMMARY:")
    print("=" * 70)

    if working_models:
        print(f"\n✅ Working models ({len(working_models)}):")
        for model in working_models:
            print(f"   - {model}")

        print(f"\n💡 Recommendation: Update your .env file:")
        print(f"   FALLBACK_AI_MODEL={working_models[0]}")
    else:
        print("\n❌ No working models found!")
        print("   Check your Groq API key at: https://console.groq.com/keys")

    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
