import requests
import json

# API key for Gemini. In a real deployment, manage securely.
# For Canvas, leave empty and it will be provided at runtime.
API_KEY = "AIzaSyC2-DdvrC9ugyaZCzF66Ox0CikNimFj8UE"
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def translate_text(text, src_lang, dest_lang):
    """
    Translates text from source language to destination language using a Google LLM (Gemini API).
    """
    if src_lang == dest_lang:
        return text

    prompt = f"Translate the following text from {src_lang} to {dest_lang}: '{text}'"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}]
    }
    headers = {'Content-Type': 'application/json'}
    params = {'key': API_KEY}

    try:
        response = requests.post(API_URL, headers=headers, params=params, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()

        if result.get("candidates") and result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts"):
            return result["candidates"][0]["content"]["parts"][0]["text"].strip()
        print(f"Translation failed for text: '{text}' from {src_lang} to {dest_lang}. API response: {result}")
        return text # Fallback: return original if translation fails or is empty
    except requests.exceptions.RequestException as e:
        print(f"API request error during translation: {e}. Falling back to original text.")
        return text
    except Exception as e:
        print(f"An unexpected error occurred during translation: {e}. Falling back to original text.")
        return text