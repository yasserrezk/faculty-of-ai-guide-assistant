import requests
from utils import weaviate_retriever as wr


def prompt_augementation(message, rag_query):
    SYSTEM_ROLE = """
    أنت مساعد ذكي متخصص في دليل كلية الذكاء الاصطناعي. مهمتك الإجابة عن أسئلة الطلاب بدقة اعتمادًا على نصوص الدليل فقط.
    """

    SYSTEM_PROMPT = """
التعليمات:
1. أجب فقط من السياق المقدّم، ولا تستخدم معلومات من خارجه.
2. إذا لم تجد الإجابة في السياق، قل: "لم أجد هذه المعلومة في دليل الكلية."
3. أجب باللغة العربية الفصحى المبسّطة، وبإيجاز ووضوح.
4. اذكر رقم الصفحة المصدر في نهاية الإجابة، مثال: (المصدر: صفحة 12).
5. لا تخمّن ولا تختلق أرقامًا أو شروطًا أو تواريخ.
6. إذا تعارضت المصادر، اذكر ذلك صراحةً.
"""

    PROMPT = f"""
السوال:
{message}
البيانات المقدمة:
{rag_query}
"""

    return [
        {
            "role": "system",
            "content": SYSTEM_ROLE.strip() + "\n" + SYSTEM_PROMPT.strip(),
        },
        {"role": "user", "content": PROMPT.strip()},
    ]


def chat_query(message, temperature=0.1, num_ctx=4096):

    chunks = wr.query(message, limit=3)
    context = "\n\n".join(c for c in chunks)
    resp = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "qwen2.5:1.5b",
            "messages": prompt_augementation(message, context),
            "stream": False,
            "think": False,
            "options": {
                "temperature": temperature,
                "num_ctx": num_ctx,
            },
        },
        timeout=120,
    )

    if resp.ok:
        return resp.json()["message"]["content"]
    else:
        print(resp.status_code, resp.text)
