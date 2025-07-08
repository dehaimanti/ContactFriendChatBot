from pdf_utils import download_pdf_text
from rag_utils import chunk_text, find_best_chunks, is_relevant_question
from prompt import build_prompt
from llm import call_llm

def run_chat(pdf_url):
    print("🔗 Downloading PDF and extracting text...")
    text = download_pdf_text(pdf_url)
    chunks = chunk_text(text)

    print("🤖 ChatBot ready! Type your question or 'exit' to quit.")
    while True:
        q = input("You: ")
        if q.lower() == "exit":
            break
        if not is_relevant_question(q):
            print("Bot: This is not a relevant question related to Contact Lenses provided in the input pdf documents. Hence not providing a response.")
            continue
        context, sources = find_best_chunks(q, chunks)
        prompt = build_prompt(q, context)
        answer = call_llm(prompt)
        print("Bot:", answer)

if __name__ == "__main__":
    url = input("Enter HTTPS PDF URL: ")
    run_chat(url)
