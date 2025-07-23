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
    """Answer a question using RAG with ChromaDB, with clarification and conversation continuity"""
    history = st.session_state.get("history", [])
    previous_question = history[-1]["question"] if history else ""
    previous_answer = history[-1]["answer"] if history else ""

    # Rebuild the current question if it's a follow-up
    context_prompt = f"""
You are a helpful assistant for answering questions related to contact lenses.

The previous user question was:
"{previous_question}"
And your previous answer was:
"{previous_answer}"

Now the user is asking:
"{question}"

If the new question is a follow-up, clarify and combine it into a complete new question using the previous context. If it's standalone, return it as-is.

Only output the full updated question.
"""
    full_question = call_llm(context_prompt.strip(), api_key, model).strip()

    if len(full_question.strip().split()) < 5 and "lens" not in full_question.lower():
        return ("😅 That’s a bit too vague! Did you mean a good solution for contact lenses, eye care, or something else?", [])

    if not is_relevant_question(full_question, api_key, model):
        return ("🤷‍♀️ That doesn’t sound like a contact lens question. Can you rephrase or be more specific?", [])

    context, sources = find_best_chunks(full_question)
    prompt = build_prompt(full_question, context)
    answer = call_llm(prompt, api_key, model)
    return answer, sources
