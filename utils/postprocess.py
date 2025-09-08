import re
from typing import List
from wordfreq import zipf_frequency

# Regex for alphanumeric part refs
PART_RE = re.compile(r"\b[A-Z0-9]{2,15}\b", re.IGNORECASE)

# Your domain-specific stopwords (kept as is)
STOPWORDS = {
    "LG", "ELECTRONICS", "INC", "COPYRIGHT", "ALL", "RIGHTS", "RESERVED", "LGE",
    "TRAINING", "SERVICE", "PURPOSES", "ONLY", "INTERNAL", "USE", "2020", "AND",
    "2016", "2018", "2015", "2019", "2021", "2017", "2022", "LAN", "GENDER",
    "WHITE", "BLACK", "EAD63769504", "EAD64185903", "EAD63769505", "EAD64185904",
    "EXPLODED", "VIEW", "IMPORTANT", "SAFETY", "NOTICE", "MANY", "ELECTRICAL",
    "MECHANICAL", "PARTS", "IN", "THIS", "CHASSIS", "HAVE", "RELATED",
    "CHARACTERISTICS", "THESE", "ARE", "IDENTIFIED", "BY", "IT", "IS", "ESSENTIAL",
    "SPECIAL", "SHOULD", "BE", "REPLACED", "WITH", "SAME", "COMPONENTS", "AS",
    "RECOMMENDED", "MANUAL", "PREVENT", "FIRE", "OR", "OTHER", "HAZARDS", "DO",
    "NOT", "MODIFY", "THE", "ORIGINAL", "DESIGN", "WITHOUT", "PERMISSION", "OF",
    "MANUFACTURER", "SHOCK", "THAT", "TO", "MRC", "MODULE", "REPAIR", "CENTER",
    "OPTICAL", "SHEET", "ITEM", "INCH", "LOCATION", "LOCATION#", "STATUS", "UNDER",
    "59INCH", "PANEL", "ASS'Y", "POL", "REAR", "FRONT", "COF", "SOURCE", "PCB",
    "LEFT", "RIGHT", "ASS", "FOR", "SIDE", "STAND", "SCREW", "BOARD"
}

def normalize_token(token: str) -> str:
    """
    Apply special normalization rules:
    - If token starts with 'N' and second last char is 'O', replace with '0'
    """
    t = token.upper()

    if t.startswith("N") and len(t) >= 3:
        if t[-2] == "O":
            t = t[:-2] + "0" + t[-1]

    return t


def is_common_english_word(token: str) -> bool:
    """
    Check if a token is a common English word using wordfreq.
    """
    # If it contains digits, it's not a normal English word
    if any(ch.isdigit() for ch in token):
        return False

    # Measure frequency on a Zipf scale: 0 (rare) to 7 (very common)
    freq = zipf_frequency(token.lower(), "en")
    return freq >= 4.0  # threshold: common English word (e.g. THE, AND, FROM)


def extract_parts(full_text: str) -> List[str]:
    """
    Extract part references, ignoring stopwords and common English words.
    Applies normalization to fix OCR errors.
    """
    parts = set()
    for m in PART_RE.finditer(full_text):
        token = m.group(0).upper()

        # Skip if in stopwords
        if token in STOPWORDS:
            continue

        # Skip common English words
        if is_common_english_word(token):
            continue

        # Normalize OCR quirks
        token = normalize_token(token)

        parts.add(token)

    return sorted(parts)
