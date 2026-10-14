import json
import re
import unicodedata
import pymupdf

PDF_PATH = "/home/nitrox/Downloads/GUIDE.pdf"

def normalize_ar(text):
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[\u064B-\u0652\u0640]", "", text)   # tashkeel + tatweel
    text = re.sub(r"[ \t]+", " ", text)                  # collapse spaces/tabs
    text = re.sub(r"\n{2,}", "\n\n", text)               # normalize paragraph breaks
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)         # single newline -> space
    text = re.sub(r" {2,}", " ", text)
    return text.strip()

def extract_content(path, pages=None):
    with pymupdf.open(path) as doc:
        pages = pages or range(len(doc))
        result = []
        for i in pages:
            raw = doc[i].get_text(sort=True)
            result.append({"page": i + 1, "text": normalize_ar(raw)})
    return result

data = extract_content(PDF_PATH)
with open("pages.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)



