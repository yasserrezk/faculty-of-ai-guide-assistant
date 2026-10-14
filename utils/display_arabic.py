import json
import arabic_reshaper
from bidi.algorithm import get_display

def show(text):
    return get_display(arabic_reshaper.reshape(text))

with open(r"faculty-of-ai-guide-assistant/utils/pages.json", encoding="utf-8") as f:
    data = json.load(f)

print(show(data[3]["text"]))