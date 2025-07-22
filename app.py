import streamlit as st
from pdf_utils import download_pdf_text
from rag_utils import chunk_text, find_best_chunks, is_relevant_question
from prompt import build_prompt
from llm import call_llm
import os
from dotenv import load_dotenv

load_dotenv()

# Streamlit Page Config
st.set_page_config(page_title="📄 Multi-PDF ChatBot", layout="centered")

st.sidebar.title("🔐 API & PDF Settings")

# API Key input
api_key = st.sidebar.text_input(
    "Enter GROQ API Key", 
    value=os.getenv("GROQ_API_KEY", ""), 
    type="password"
)

# Model selection
model = st.sidebar.selectbox("Choose Model", ["llama3-70b-8192", "mixtral-8x7b-32768"])

# Default PDF URLs
st.sidebar.markdown("### 🔗 Paste up to 2 PDF HTTPS URLs")
default_urls = [
    "https://coopervision.com/sites/coopervision.com/files/pi01000_rev_c_avaira_vitality_pi_final.pdf",
    "https://coopervision.com/sites/coopervision.com/files/pi01099_rev_d_biofinity_family_pi_0.pdf"
 ]

# Collect up to 2 PDF URLs
pdf_urls = [
    st.sidebar.text_input(f"PDF Link {i+1}", value=default_urls[i])
    for i in range(2)
]

# App Title
st.title("📚 Contact Friend ChatBot")
st.markdown("Ask questions based on any of the 2 PDFs provided.")

# Validate URLs
valid_urls = [url for url in pdf_urls if url.lower().endswith(".pdf") and url.startswith("https://")]

# Load and Chat Logic
if api_key and valid_urls:
    try:
        with st.spinner("⏳ Loading PDFs..."):
            all_chunks = []
            for url in valid_urls:
                text = download_pdf_text(url)
                all_chunks.extend(chunk_text(text, source=url))

        if "history" not in st.session_state:
            st.session_state.history = []
            st.chat_message("assistant").markdown("👋 Hello, I’m **Contact Friend**! How can I help you today?")

        # Chat Input
        question = st.chat_input("💬 Ask a question based on the PDFs:")
        if question:
            if not is_relevant_question(question, api_key, model):
                answer = "This is not a relevant question related to Contact Lenses. Hence not providing a response."
                sources = []
            else:
                with st.spinner("🤖 Thinking..."):
                    context, sources = find_best_chunks(question, all_chunks)
                    prompt = build_prompt(question, context)
                    answer = call_llm(prompt, api_key, model)

            st.session_state.history.append({
                "question": question,
                "answer": answer,
                "sources": sources
            })

        # Display Chat History with Feedback
        for i, chat in enumerate(st.session_state.history):
            with st.chat_message("user"):
                st.write(chat["question"])
            with st.chat_message("assistant"):
                st.write(chat["answer"])
                if chat["sources"]:
                    st.markdown(
                        f"<div style='font-size: 0.85em; color: gray'>📄 Sources: {', '.join(chat['sources'])}</div>",
                        unsafe_allow_html=True)

                # Feedback buttons 👍👎
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("👍 Thumbs Up", key=f"thumbs_up_{i}"):
                        st.success("Thanks for the 👍!")
                with col2:
                    if st.button("👎 Thumbs Down", key=f"thumbs_down_{i}"):
                        st.warning("Got it 👎! We'll try to do better.")

    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.info("Please enter your API key and at least one valid PDF URL.")
