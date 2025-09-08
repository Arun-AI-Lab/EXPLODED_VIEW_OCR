import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("VISION_API_KEY")
ENDPOINT_URL = f"https://vision.googleapis.com/v1/images:annotate?key={API_KEY}"

def detect_text(image_path: str):
    """
    Returns (full_text, words)
    words = list of dicts: {'text': 'ABC123'}
    """
    with open(image_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    body = {
        "requests": [{
            "image": {"content": content},
            "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
        }]
    }

    resp = requests.post(ENDPOINT_URL, json=body)
    data = resp.json()

    try:
        r = data["responses"][0]
    except (KeyError, IndexError):
        return "NO TEXT FOUND", []

    full_text = r.get("fullTextAnnotation", {}).get("text", "") or "NO TEXT FOUND"

    words = []
    ann = r.get("textAnnotations", [])
    for item in ann[1:]:
        txt = item.get("description", "").strip()
        if txt:
            words.append({"text": txt})

    return full_text, words
