import os
import fitz  # PyMuPDF
from PIL import Image

def convert_pdf_to_tiffs(pdf_path, page_indices, output_dir="output_tiffs", dpi=400):
    """
    Convert selected PDF pages to TIFFs using PyMuPDF (no poppler).
    """
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)

    output_files = []
    zoom = dpi / 72  # scale factor
    mat = fitz.Matrix(zoom, zoom)

    for page_index in page_indices:
        page = doc[page_index]
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        out_file = os.path.join(output_dir, f"page_{page_index+1}.tiff")
        img.save(out_file, "TIFF")
        output_files.append(out_file)

    doc.close()
    return output_files
