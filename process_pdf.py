import fitz  # to extract text
from langchain.text_splitter import RecursiveCharacterTextSplitter   # to split into word chunks
from sentence_transformers import SentenceTransformer   # to embedd chunks(vector reprn)
import faiss    #vector database
import os
import pickle

def extract_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text


def split_text_into_chunks(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 50  #each chunk shares 50 char with prev one
    )
    return splitter.split_text(text)


def create_embeddings(chunks):
    model = SentenceTransformer("all-MiniLM-L6-v2")   # sentence transformer model with 6 transformer layers and gives embedding vector of 384 dimensions
    embeddings = model.encode(chunks)
    return embeddings


def save_to_faiss(embeddings, chunks, index_path="embeddings/faiss_index"):
    dimension = embeddings.shape[1]    #stores how many numbers in each vector
    index = faiss.IndexFlatL2(dimension)    #creates faiss index with L2(Euclidean distance)
    index.add(embeddings)
    os.makedirs(index_path, exist_ok=True)

    faiss.write_index(index, f"{index_path}/faiss.index")    #saves faiss indexto a file

    with open(f"{index_path}/chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)     #saves actual text chunks into .pkl file


if __name__ == "__main__":
    pdf_text = extract_pdf_text("nephrology.pdf")
    chunks = split_text_into_chunks(pdf_text)
    embeddings = create_embeddings(chunks)
    save_to_faiss(embeddings, chunks)