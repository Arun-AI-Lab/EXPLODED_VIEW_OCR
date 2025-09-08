import os
import io
from PIL import Image
import streamlit as st
import fitz  # PyMuPDF

from utils.ocr import detect_text
from utils.postprocess import extract_parts

# --- Streamlit Config ---
st.set_page_config(page_title="Exploded View OCR", layout="wide")
st.title("📄 Exploded View OCR (PDF → TIFF + OCR)")

os.makedirs("tmp", exist_ok=True)

# --- Initialize session state ---
if "results" not in st.session_state:
    st.session_state["results"] = []
if "last_pdf" not in st.session_state:
    st.session_state["last_pdf"] = None

# --- File Upload ---
uploaded_pdf = st.file_uploader("Upload a PDF file", type=["pdf"])
page_input = st.text_input("Enter page numbers (e.g. 1,2,5-7):")

# Run OCR only when button is clicked
if uploaded_pdf and page_input:
    if st.button("Run OCR", type="primary"):
        def parse_pages(s):
            pages = []
            for part in s.split(","):
                if "-" in part:
                    start, end = part.split("-")
                    pages.extend(range(int(start), int(end) + 1))
                else:
                    pages.append(int(part))
            return [p - 1 for p in pages]  # PyMuPDF is 0-based

        selected_pages = parse_pages(page_input)

        pdf_path = os.path.join("tmp", uploaded_pdf.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_pdf.read())

        doc = fitz.open(pdf_path)
        results = []

        for i in selected_pages:
            if i < 0 or i >= len(doc):
                continue

            # Convert PDF page → TIFF
            page = doc[i]
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_bytes))

            # Save TIFF
            tiff_name = f"{os.path.splitext(uploaded_pdf.name)[0]}_p{i+1}.tiff"
            tiff_path = os.path.join("tmp", tiff_name)
            img.save(tiff_path, format="TIFF")

            # OCR
            full_text, words = detect_text(tiff_path)
            parts = extract_parts(full_text)

            results.append((i + 1, parts, tiff_path, tiff_name))

        # ✅ Save results in session_state so they don’t disappear
        st.session_state["results"] = results
        st.session_state["last_pdf"] = uploaded_pdf.name

# --- Display saved results (persist until refresh/new upload) ---
if st.session_state["results"]:
    st.subheader(f"📑 OCR Results (from {st.session_state['last_pdf']})")

    for page_num, parts, tiff_path, tiff_name in st.session_state["results"]:
        with st.expander(f"📄 Page {page_num}", expanded=True):
            if parts:
                parts_text = "\n".join(parts)
                st.text_area("📋 Parts (copy into Excel)", parts_text, height=150)
            else:
                st.write("📋 Parts: ❌ None Found")

            with open(tiff_path, "rb") as f:
                st.download_button(
                    label=f"⬇️ Download TIFF (Page {page_num})",
                    data=f.read(),
                    file_name=tiff_name,
                    mime="image/tiff",
                    key=f"tiff-{page_num}-{tiff_name}"
                )
