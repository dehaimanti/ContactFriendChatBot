import requests
import fitz  # from PyMuPDF
from io import BytesIO

def download_pdf_text(url):
    if not url.lower().endswith(".pdf") or not url.lower().startswith("https://"):
        raise ValueError("URL must be a valid HTTPS PDF link.")
    
    response = requests.get(url)
    response.raise_for_status()

    with BytesIO(response.content) as pdf_stream:
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text