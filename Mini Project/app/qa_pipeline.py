import requests
import json
import os
import streamlit as st # Import streamlit to access st.secrets
from .wikipedia_fetcher import get_context_from_wikipedia
from .translate import translate_text

# API key for Gemini. IMPORTANT: This is now read from Streamlit Secrets.
# Ensure you set this secret in your Streamlit Community Cloud dashboard.
# In local development, you can use a .streamlit/secrets.toml file.
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    raise ValueError("GOOGLE_API_KEY not found in Streamlit secrets. Please set it securely.")

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def answer_question(question, src_lang):
    """
    Answers a question by:
    1. Optionally fetching context from Wikipedia.
    2. Using a Google LLM (Gemini API) to answer the question, potentially
       augmented with Wikipedia context.
    3. Returns the answer in the original question's language (LLM is multilingual).
    """
    try:
        # Fetch context from Wikipedia based on an English version of the question
        question_for_wiki_search = question
        if src_lang != "en":
            question_for_wiki_search = translate_text(question, src_lang, "en")

        context = get_context_from_wikipedia(question_for_wiki_search)

        # Construct the prompt for the LLM
        prompt = (
            f"Provide a very concise and accurate answer to the following question, ideally in 1-2 sentences. "
            f"**Always give a direct, factual answer.** "
            f"Use the provided context to add relevant details or when your general knowledge is insufficient. "
            f"Do not state that you lack current information, internet access, or that the answer is not in the context. "
            f"Answer in the original language of the question ('{question}') if possible, otherwise in English.\n\n"
            f"Question: '{question}'\n\n"
        )

        if context and context.strip() != "Sorry, no relevant context could be retrieved from Wikipedia." and len(context.strip()) >= 50:
            prompt += f"Context: '{context}'"
        
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}]
        }
        headers = {'Content-Type': 'application/json'}
        params = {'key': API_KEY}

        response = requests.post(API_URL, headers=headers, params=params, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()

        if result.get("candidates") and result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts"):
            answer = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            return answer
        
        return "Sorry, I could not generate an answer."

    except requests.exceptions.RequestException as e:
        return f"An API error occurred while answering the question: {e}"
    except Exception as e:
        return f"An error occurred while answering the question: {e}"

