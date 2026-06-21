from groq import Groq
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Get API key
api_key = os.getenv("GROQ_API_KEY")

print("API Key Loaded:", api_key[:10], "...")  # debug

client = Groq(api_key=api_key)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": "Say hello"}
    ]
)

print(response.choices[0].message.content)