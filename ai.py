import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def ask_ai(message: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Error: {str(e)}"
      
