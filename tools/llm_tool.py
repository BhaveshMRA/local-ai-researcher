import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "llama-3.1-8b-instant"
def get_api_key():
    try:
        import streamlit as st
        return st.secrets["GROQ_API_KEY"]
    except:
        return os.environ.get("GROQ_API_KEY")

client = Groq(api_key=get_api_key())

def call_llm(prompt: str, system: str = "") -> str:
    """Send a prompt to Groq and return the response."""
    try:
        messages = []
        
        if system:
            messages.append({"role": "system", "content": system})
        
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=1024,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"ERROR: {str(e)}"


def test_connection() -> bool:
    """Test if Groq API is working."""
    try:
        test = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=10
        )
        return True
    except:
        return False