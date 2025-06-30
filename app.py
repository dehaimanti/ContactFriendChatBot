import streamlit as st
from pdf_utils import download_pdf_text
from rag_utils import chunk_text, find_best_chunks
from prompt import build_prompt
from llm import call_llm

st.set_page_config(page_title="📄 Multi-PDF ChatBot", layout="centered")

st.sidebar.title("🔐 API & PDF Settings")
api_key = st.sidebar.text_input("Enter GROQ API Key", type="password")
model = st.sidebar.selectbox("Choose Model", ["llama3-70b-8192", "mixtral-8x7b-32768"])

st.sidebar.markdown("### 🔗 Paste up to 5 PDF HTTPS URLs")
default_urls = [
    "https://coopervision.com/sites/coopervision.com/files/pi01000_rev_c_avaira_vitality_pi_final.pdf",
    "https://coopervision.com/sites/coopervision.com/files/pi01099_rev_d_biofinity_family_pi_0.pdf",
    "https://coopervision.com/sites/coopervision.com/files/pi01018_rev_c_biomedics_55_asphere_final.pdf",
    "https://coopervision.com/sites/coopervision.com/files/pi01093_rev_b_biomedics_toric.pdf",
    "https://coopervision.com/sites/coopervision.com/files/pi01017_package_insert_omafilcon_a_60_xc_aspheric_biomedics_xc_rev_a_0.pdf"
]

pdf_urls = [
    st.sidebar.text_input(f"PDF Link {i+1}", value=default_urls[i])
    for i in range(5)
]

st.title("📚 Contact Friend ChatBot")
st.markdown("Ask questions based on any of the 5 PDFs provided.")

valid_urls = [url for url in pdf_urls if url.lower().endswith(".pdf") and url.startswith("https://")]

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


        question = st.chat_input("💬 Ask a question based on the PDFs:")
        if question:
            with st.spinner("🤖 Thinking..."):
                context, sources = find_best_chunks(question, all_chunks)
                prompt = build_prompt(question, context)
                answer = call_llm(prompt, api_key, model)

                st.session_state.history.append({
                    "question": question,
                    "answer": answer,
                    "sources": sources
                })

        for chat in st.session_state.history:
            with st.chat_message("user"):
                st.write(chat["question"])
            with st.chat_message("assistant"):
                st.write(chat["answer"])
                st.markdown(f"<div style='font-size: 0.85em; color: gray'>📄 Sources: {', '.join(chat['sources'])}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.info("Please enter your API key and at least one valid PDF URL.")