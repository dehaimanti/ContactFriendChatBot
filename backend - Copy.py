# backend.py
import streamlit as st
from pdf_utils import download_pdf_text
from rag_utils import chunk_text, find_best_chunks, is_relevant_question, store_chunk_in_chroma
from prompt import build_prompt
from llm import call_llm

def load_and_store_chunks(pdf_urls):
    """Download PDFs, chunk, and store them in ChromaDB"""
    for url in pdf_urls:
        text = download_pdf_text(url)
        chunks = chunk_text(text, source=url)
        for chunk in chunks:
            store_chunk_in_chroma(chunk)

def process_question(question, api_key, model):
    """Answer a question using RAG with ChromaDB, with clarification for vague queries and contextual reconstruction"""
    # Get previous user input (if any)
    history = [msg["question"] for msg in st.session_state.get("history", [])]
    previous_question = history[-1] if history else ""

    # Use LLM to decide if clarification or rephrasing is needed
    clarification_prompt = f"""
You are a smart assistant helping a user with questions about contact lenses.
The user has just asked: "{question}"
Their previous message was: "{previous_question}"

If the current question is vague (e.g., "yes", "okay", "what solution is best"), and you can combine it with the previous message to form a clear query, rephrase it into a complete question about contact lenses.
Otherwise, just return the current question.

Output only the rephrased or original full question, nothing else.
""" 
    question = call_llm(clarification_prompt.strip(), api_key, model).strip()

    if len(question.strip().split()) < 5 and "lens" not in question.lower():
        return ("😅 That’s a bit too vague! Did you mean a good solution for contact lenses, eye care, or something else?", [])

    if not is_relevant_question(question, api_key, model):
        return ("🤷‍♀️ That doesn’t sound like a contact lens question. Can you rephrase or be more specific?", [])

    context, sources = find_best_chunks(question)
    prompt = build_prompt(question, context)
    answer = call_llm(prompt, api_key, model)
    return answer, sources
