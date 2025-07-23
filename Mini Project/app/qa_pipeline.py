import requests
import json
import os # Import os for environment variables
from .wikipedia_fetcher import get_context_from_wikipedia # Keep for RAG
from .translate import translate_text # Import translate_text for internal use

# API key for Gemini. IMPORTANT: REPLACE "YOUR_ACTUAL_API_KEY_HERE" with your Google Cloud API Key.
# Hardcoding API keys is generally not recommended for production environments for security reasons.
API_KEY = "AIzaSyC2-DdvrC9ugyaZCzF66Ox0CikNimFj8UE"
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def answer_question(question, src_lang):
    """
    Answers a question by:
    1. Translating the question to English (if needed) for Wikipedia search.
    2. Fetching context from Wikipedia based on the English question.
    3. Using a Google LLM (Gemini API) to answer the question, potentially
       augmented with Wikipedia context, prioritizing current knowledge for
       "current" queries.
    4. Returns the answer.
    """
    try:
        if not API_KEY or API_KEY == "YOUR_ACTUAL_API_KEY_HERE":
            raise ValueError("API_KEY is not set or is still a placeholder. Please replace 'YOUR_ACTUAL_API_KEY_HERE' in app/qa_pipeline.py with your actual Google Cloud API key.")

        # Translate the incoming question to English for Wikipedia search
        # Wikipedia search often works best with English queries.
        question_en = translate_text(question, src_lang, "en")
        print(f"Translated question to English for Wikipedia search: {question_en}") # Debugging

        # Get context from Wikipedia using the English question
        context = get_context_from_wikipedia(question_en)

        # --- DEBUGGING PRINTS (CRUCIAL FOR DIAGNOSIS) ---
        print(f"\n--- DEBUG: Context for LLM (from Wikipedia) ---\n")
        print(context)
        print(f"\n--- DEBUG END ---\n")
        # -------------------------------------------------

        # Determine if the question is asking for current information
        current_keywords = ["current", "latest", "who is", "what is the current"]
        is_current_query = any(keyword in question.lower() for keyword in current_keywords)

        # Construct the prompt for the LLM
        prompt = ""
        if context and context.strip() != "Sorry, no relevant context could be retrieved from Wikipedia." and len(context.strip()) >= 50:
            # For both current and general queries with context:
            # Instruct the LLM to use context if relevant, otherwise fall back to general knowledge.
            print("Context available. Instructing LLM to use context if relevant, else general knowledge.")
            prompt = (
                f"Answer the following question concisely and accurately. "
                f"Use the provided context if relevant, otherwise answer based on your general knowledge. "
                f"Answer in the original language of the question ('{question}') if possible, otherwise in English.\n\n"
                f"Question: '{question}'\n\n"
                f"Context: '{context}'"
            )
        else:
            # If no good context from Wikipedia, tell the LLM to use general knowledge.
            print("No sufficient context found from Wikipedia or context too short. Answering based on general knowledge.")
            prompt = (
                f"Answer the following question concisely and accurately based on your general knowledge. "
                f"Answer in the original language of the question ('{question}') if possible, otherwise in English:\n\n"
                f"Question: '{question}'"
            )

        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}]
        }
        headers = {'Content-Type': 'application/json'}
        params = {'key': API_KEY}

        # --- DEBUGGING PRINTS (CRUCIAL FOR DIAGNOSIS) ---
        print(f"\n--- DEBUG: Prompt sent to LLM ---\n")
        print(prompt)
        print(f"\n--- DEBUG END ---\n")

        response = requests.post(API_URL, headers=headers, params=params, data=json.dumps(payload))
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        result = response.json()

        if result.get("candidates") and result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts"):
            answer = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            print(f"LLM Answer: '{answer}'")
            return answer
        
        print(f"LLM did not return a valid answer. API response: {result}")
        return "Sorry, I could not generate an answer."

    except requests.exceptions.RequestException as e:
        print(f"API request error during question answering: {e}")
        return f"An API error occurred while answering the question: {e}"
    except Exception as e:
        print(f"An unexpected error occurred in answer_question: {e}")
        return f"An error occurred while answering the question: {e}"