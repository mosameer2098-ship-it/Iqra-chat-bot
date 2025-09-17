import openai
from config import OPENAI_API_KEY
import logging

openai.api_key = OPENAI_API_KEY

logger = logging.getLogger(__name__)

def ask_ai(message: str, user_id: int = None) -> str:
    """
    Query OpenAI ChatCompletion (gpt-3.5-turbo). Returns the assistant reply text.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message}
            ],
            max_tokens=600,
            temperature=0.7,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.exception("OpenAI error")
        return "⚠️ API Error: Unable to get response from AI right now."
        
      
