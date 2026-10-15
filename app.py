import json

import requests
import streamlit as st

from utils import weaviate_retriever as wr
from utils.chatbot import prompt_augementation


# Same settings as utils/chatbot.py (chat_query)
OLLAMA_URL = "http://localhost:11434"
MODEL = ""
TEMPERATURE = 0.1
NUM_CTX = 4096

EXAMPLES = [
    "ما هي شروط القبول في الكلية؟",
    "كيف يتم حساب المعدل التراكمي؟",
    "ما هي الأقسام العلمية بالكلية؟",
]

st.set_page_config(page_title="مساعد دليل كلية الذكاء الاصطناعي", page_icon="🎓")

st.markdown(
    """
    <style>
    [data-testid="stChatMessageContent"],
    [data-testid="stChatInput"] textarea,
    h1, .stCaption, [data-testid="stExpander"] { direction: rtl; text-align: right; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎓 مساعد دليل كلية الذكاء الاصطناعي")
st.caption("اسأل عن أي شيء في دليل الطالب، والإجابة تكون من الدليل فقط.")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("الإعدادات")
    top_k = st.slider("عدد المقاطع المسترجعة", 1, 8, 3)
    if st.button("مسح المحادثة"):
        st.session_state.messages = []
        st.rerun()


def show_sources(sources):
    with st.expander("المصادر"):
        for s in sources:
            st.markdown(s)
            st.divider()


def stream_answer(question, chunks):
    context = "\n\n".join(chunks)
    with requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": MODEL,
            "messages": prompt_augementation(question, context),
            "stream": True,
            "think": False,
            "options": {"temperature": TEMPERATURE, "num_ctx": NUM_CTX},
        },
        stream=True,
        timeout=120,
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line:
                continue
            data = json.loads(line)
            token = data.get("message", {}).get("content", "")
            if token:
                yield token
            if data.get("done"):
                break


for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("sources"):
            show_sources(m["sources"])

question = st.chat_input("اكتب سؤالك هنا...")

if not st.session_state.messages and not question:
    st.markdown("**أمثلة على الأسئلة:**")
    for i, ex in enumerate(EXAMPLES):
        if st.button(ex, key=f"ex{i}"):
            question = ex

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        chunks = []
        try:
            with st.spinner("جارٍ البحث في الدليل..."):
                chunks = wr.query(question, limit=top_k)
            if not chunks:
                answer = "لم أجد هذه المعلومة في دليل الكلية."
                st.markdown(answer)
            else:
                answer = st.write_stream(stream_answer(question, chunks))
                show_sources(chunks)
        except Exception as e:
            answer = f"حدث خطأ: {e}"
            chunks = []
            st.error(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": chunks}
    )
