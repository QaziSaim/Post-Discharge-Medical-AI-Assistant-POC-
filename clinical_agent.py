import faiss
import pickle
import numpy as np
import logging
import requests
from sentence_transformers import SentenceTransformer
from llm_engine import generate_answer  # This calls Mistral locally via llama-cpp

# Setup logging
logging.basicConfig(filename="clinical_agent.log", level=logging.INFO)

# Load FAISS index and stored chunks
def load_faiss_data():
    index = faiss.read_index("embeddings/faiss_index/faiss.index")
    with open("embeddings/faiss_index/chunks.pkl", "rb") as f:
        chunks = pickle.load(f)
    return index, chunks

# Embed the question using MiniLM (same as used in chunking)
def embed_question(question, model):
    return model.encode([question])[0]

# Filter chunks by FAISS similarity threshold
def search_chunks(question_embedding, index, chunks, top_k=5, threshold=0.8):
    D, I = index.search(np.array([question_embedding]), top_k)
    print("🔍 FAISS distances:", D[0])  # For debugging

    relevant_chunks = []
    for distance, idx in zip(D[0], I[0]):
        if distance < threshold:
            relevant_chunks.append(chunks[idx])

    return relevant_chunks

# Tavily web search fallback
def fallback_web_search(query):
    API_KEY = "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"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    json = {"query": query, "search_depth": "basic"}
    response = requests.post("https://api.tavily.com/search", headers=headers, json=json)

    if response.status_code == 200:
        return response.json()["results"][0]["content"]
    return "No relevant information found on the web."

def run_clinical_agent(question):
    if question.strip().lower() in ["bye", "exit", "thank you", "thanks"]:
        return ("I'm glad I could help! Take care and follow up with your doctor. 👋", "Session Ended")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    index, chunks = load_faiss_data()

    q_embedding = embed_question(question, model)
    top_chunks = search_chunks(q_embedding, index, chunks, top_k=5, threshold=0.8)

    if not top_chunks:
        logging.warning(f"No relevant chunks found for: {question}")
        answer = fallback_web_search(question)
        source = "🌐 Source: Web (Tavily)"
    else:
        context = "\n\n".join(top_chunks)
        answer = generate_answer(context, question)
        answer = answer.replace("```", "")  # prevent accidental code blocks
        answer = answer.replace("    ", "")  # remove excessive indentation
        source = "📘 Source: Nephrology PDF"

    logging.info(f"Question: {question}")
    logging.info(f"Answer: {answer}")
    logging.info(f"Source: {source}")

    followup_prompt = "\n\nHow else can I assist you today?"
    return answer + followup_prompt, source

if __name__ == "__main__":
    print("💬 Clinical Agent Activated!")
    while True:
        user_question = input("👤 Ask your medical question: ")
        answer, src = run_clinical_agent(user_question)
        print("\n🤖 Clinical Agent:", answer)
        print(src)
        if src == "Session Ended":
            break
