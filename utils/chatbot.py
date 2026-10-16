import json

import requests
from utils import weaviate_retriever as wr

OLLAMA_URL = "http://localhost:15000"
MODEL = "gemma3:4b"

SYSTEM_PROMPT = """
أنت مساعد ذكي متخصص في دليل كلية الذكاء الاصطناعي. شغلك إنك تجاوب على أسئلة الطلبة بدقة، اعتمادًا على نصوص الدليل اللي قدامك بس.

التعليمات:
1. جاوب من السياق المقدَّم بس، ومتستخدمش أي معلومة من برّه الدليل.
2. لو مالقيتش الإجابة في السياق، قول بالنص: "ملقيتش المعلومة دي في دليل الكلية."
3. جاوب باللهجة المصرية البسيطة والواضحة، وكأنك بتشرح لزميلك.
4. اشرح بالتفصيل: اذكر الشروط والاستثناءات والأرقام والمواعيد والخطوات اللي في الدليل، ومتكتفيش بإجابة مختصرة. لو الموضوع فيه أكتر من حالة، اشرح كل حالة لوحدها.
5. رتّب الإجابة لو فيها نقاط كتير (خطوات أو شروط) عشان تبقى سهلة في القراءة.
6. متذكرش أرقام صفحات أو أي إشارة لمكان المعلومة في الدليل.
7. متخمّنش ومتألفش أرقام أو شروط أو تواريخ مش موجودة في السياق.
8. لو في تعارض بين النصوص في السياق، وضّح ده صراحةً واذكر الاختلاف.
""".strip()

def prompt_augementation(message, context):
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"السؤال:\n{message}\n\nالبيانات المقدمة:\n{context}"},
    ]


def chat_stream(message, temperature=0.1, limit=3):
    context = "\n\n".join(wr.query(message, limit=limit))
    with requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": MODEL,
            "messages": prompt_augementation(message, context),
            "stream": True,
            "options": {"temperature": temperature},
        },
        stream=True,
        timeout=120,
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                chunk = json.loads(line)
                yield chunk["message"]["content"]
                if chunk.get("done"):
                    break


def chat_query(message, **kwargs):
    return "".join(chat_stream(message, **kwargs))