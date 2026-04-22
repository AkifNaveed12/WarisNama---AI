import os
from dotenv import load_dotenv
load_dotenv()

print("=" * 50)
print("GEMINI API TEST")
print("=" * 50)

# Check if API key exists
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print(f"✅ API Key found: {api_key[:15]}...")
    print(f"   Length: {len(api_key)} characters")
else:
    print("❌ API Key NOT found in .env file")
    exit()

# Test new package with CORRECT model name
print("\n--- Testing google.genai (new package) ---")
try:
    from google import genai
    client = genai.Client(api_key=api_key)
    
    # CORRECT MODEL NAME: gemini-1.5-flash (without -exp)
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents="Say 'Hello World'"
    )
    print(f"✅ SUCCESS! Response: {response.text}")
    print("   Gemini is working correctly!")
except ImportError:
    print("❌ google-genai not installed")
    print("   Run: pip install google-genai")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 50)