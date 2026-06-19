import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def ask_llm(context, question):

    prompt = f"""
You are a PDF assistant.

Answer ONLY using the provided context.

If the answer is not available in the context,
reply exactly:

"Not found in document."

Context:
{context}

Question:
{question}
""" 

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content