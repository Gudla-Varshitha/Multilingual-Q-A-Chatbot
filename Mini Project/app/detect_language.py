import requests
import json

# API key for Gemini. REPLACE "YOUR_ACTUAL_API_KEY_HERE" with your Google Cloud API Key.
API_KEY = "AIzaSyC2-DdvrC9ugyaZCzF66Ox0CikNimFj8UE"
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def detect_language(text):
    """
    Detects the language of the given text using a Google LLM (Gemini API).
    Returns 'en' as a fallback if detection fails.
    """
    if not text or not text.strip():
        return "en" # Default to English for empty input

    prompt = f"Detect the ISO 639-1 language code of the following text: '{text}'. Respond with only the language code (e.g., 'en', 'es', 'fr', 'te', 'hi')."
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}]
    }
    headers = {'Content-Type': 'application/json'}
    params = {'key': API_KEY}

    try:
        response = requests.post(API_URL, headers=headers, params=params, data=json.dumps(payload))
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        result = response.json()

        if result.get("candidates") and result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts"):
            lang_code = result["candidates"][0]["content"]["parts"][0]["text"].strip().lower()
            # Basic validation for common language codes (e.g., "en", "es", "fr")
            if len(lang_code) >= 2 and len(lang_code) <= 3: # ISO 639-1 or 639-2
                return lang_code
        print(f"Language detection failed for text: '{text}'. Falling back to 'en'. API response: {result}")
        return "en"
    except requests.exceptions.RequestException as e:
        print(f"API request error during language detection: {e}. Falling back to 'en'.")
        return "en"
    except Exception as e:
        print(f"An unexpected error occurred during language detection: {e}. Falling back to 'en'.")
        return "en"