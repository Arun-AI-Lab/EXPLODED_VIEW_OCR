import os

def save_uploaded_file(uploaded_file, save_dir="sample_diagrams"):
    """Save uploaded file and return path."""
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def parse_page_range(input_str: str, total_pages: int) -> list[int]:
    """
    Parse a string like "1,2,5-7" into a list of page indices (0-based).
    """
    pages = set()
    parts = input_str.split(",")
    for p in parts:
        p = p.strip()
        if "-" in p:
            start, end = p.split("-")
            for i in range(int(start), int(end) + 1):
                if 1 <= i <= total_pages:
                    pages.add(i - 1)  # zero-based
        elif p.isdigit():
            i = int(p)
            if 1 <= i <= total_pages:
                pages.add(i - 1)
    return sorted(list(pages))
