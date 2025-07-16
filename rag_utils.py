from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def chunk_text(text, chunk_size=500, source=""):
    words = text.split()
    return [{"text": " ".join(words[i:i+chunk_size]), "source": source}
            for i in range(0, len(words), chunk_size)]

def find_best_chunks(question, all_chunks, top_k=3):
    texts = [chunk["text"] for chunk in all_chunks]
    sources = [chunk["source"] for chunk in all_chunks]
    
    vectorizer = TfidfVectorizer().fit(texts + [question])
    chunk_vecs = vectorizer.transform(texts)
    question_vec = vectorizer.transform([question])
    
    scores = cosine_similarity(question_vec, chunk_vecs).flatten()
    best_indices = np.argsort(scores)[-top_k:]

    best_chunks = [all_chunks[i] for i in reversed(best_indices)]
    combined_text = "\n\n".join([chunk["text"] for chunk in best_chunks])
    pdf_sources = list(set([chunk["source"] for chunk in best_chunks]))
    
    return combined_text, pdf_sources

from llm import call_llm

def is_relevant_question(question, api_key, model):
    relevance_prompt = f"""
You are an intelligent filter. Determine if the following question is related to **contact lenses** or their usage, side effects, care, or products.

If it is related, respond with "yes".  
If it is not related, respond with "no".

Question: "{question}"
Answer:
"""
    answer = call_llm(relevance_prompt.strip(), api_key, model).strip().lower()
    return "yes" in answer

