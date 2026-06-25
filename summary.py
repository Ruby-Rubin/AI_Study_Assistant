import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_summary(text):

    prompt = f"""
You are an expert study assistant.

Generate a structured summary of the following document.

Format:

# Main Topics

# Key Concepts

# Important Points

# Final Takeaways

Requirements:
- Use bullet points
- Remove repetition
- Keep important technical details
- Make it useful for exam preparation

Document:

{text}
"""

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=1500
    )

    return response.choices[0].message.content