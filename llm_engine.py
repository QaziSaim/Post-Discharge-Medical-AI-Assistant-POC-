import google.generativeai as genai
import os

# Configure API key
genai.configure(api_key="")

# Initialize Gemini 2.5 Flash model
model = genai.GenerativeModel("gemini-2.5-flash")

def generate_answer(context, question):
    prompt = f"""
You are a kind and helpful nephrology assistant.

Use the context below to answer the patient's question clearly.

Context:
{context}

Question:
{question}

Answer:
"""
    response = model.generate_content(prompt)
    return response.text.strip()
