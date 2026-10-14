import pandas as pd
import pymupdf
import re
from typing import Dict,List,Any
import json
import unicodedata
from nltk.tokenize import WhitespaceTokenizer


PDF_PATH = "/home/nitrox/Downloads/GUIDE.pdf"



_junk = re.compile(r'[\u0640\u064B-\u065F\u0670\u200b-\u200f\ufeff]')
_tok = WhitespaceTokenizer()

def clean_text(text: str) -> str:
    text = _junk.sub("", unicodedata.normalize("NFKC", text))
    text = text.translate(str.maketrans("یکھ", "يكه"))   # Persian forms in your PDF
    toks = [t for t in _tok.tokenize(text) if not t.startswith(("http", "www"))]
    return " ".join(toks)

doc = pymupdf.open(PDF_PATH)
pdf_contents: List[Dict[str,Any]] = []

for page_number,page_content in enumerate(doc[3:]):
    
    pdf_content:Dict[str,Any] = {
        'page_num':page_number+2,
        'content':clean_text(page_content.get_text()),
    }

    pdf_contents.append(pdf_content)
    print('Extraction & cleaning stage done sucessfully.')

with open("faculty-of-ai-guide-assistant/data/cleaned_metadata.json", "w", encoding="utf-8") as f:
    json.dump(pdf_contents, f, ensure_ascii=False, indent=2)
    print('File saved sucessfully in /data/....')