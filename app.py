import json
import uuid
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from utils import chatbot

LOGO = Path("assets/logo.png")
AVATAR = str(LOGO) if LOGO.exists() else "🎓"

HISTORY_FILE = Path("data/chats.json")
PERSIST = True  # False = الهيستوري يتمسح مع ريفريش الصفحة

SUGGESTIONS = [
    "ما شروط التخرج؟",
    "اعضاء هيئة التدريس",
    "إيه مواد سنة ثالثة ترم الاول قسم ذكاء الالة؟",
]

st.set_page_config(
    page_title="AI College Assistant",
    page_icon=str(LOGO) if LOGO.exists() else "🎓",
    layout="wide",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&display=swap');

:root {
    --bg: #0a0a0b;
    --sidebar: #0f0f11;
    --panel: #151517;
    --panel-hover: #1c1c1f;
    --border: rgba(255, 255, 255, .09);
    --border-hover: rgba(255, 255, 255, .24);
    --text: #ECECEC;
    --muted: #9A9AA0;
    --accent: #38BDF8;
}

html, body, .stApp,
[data-testid="stMarkdownContainer"],
[data-testid="stSidebar"],
.stButton button,
[data-testid="stChatInput"] textarea {
    font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif;
}

html, body, .stApp {
    background: var(--bg) !important;
    color: var(--text);
}

[data-testid="stMain"],
[data-testid="stHeader"],
[data-testid="stBottom"],
[data-testid="stBottom"] > div {
    background: transparent !important;
}

#MainMenu, footer { visibility: hidden; }
a { color: var(--accent) !important; }

[data-testid="stMainBlockContainer"] {
    max-width: 1000px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
    background: var(--sidebar) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] > div { background: transparent !important; }
[data-testid="stSidebar"] * { color: var(--text); }

[data-testid="stSidebar"] .stButton > button {
    min-height: 42px;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 10px;
    justify-content: flex-start;
    transition: background .15s ease, border-color .15s ease;
}
[data-testid="stSidebar"] .stButton > button p {
    unicode-bidi: plaintext;
    text-align: start;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--panel-hover);
    border-color: var(--border);
}
/* الشات النشط */
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
    background: var(--panel-hover);
    border-color: var(--border-hover);
}
[data-testid="stSidebar"] [data-testid="stImage"] img { border-radius: 14px; }

.side-label {
    margin: 1.2rem 0 .4rem;
    font-size: .8rem;
    color: var(--muted);
    letter-spacing: .04em;
}

/* ---------- Hero ---------- */
.hero { padding: 8vh 0 2.5rem; text-align: center; animation: fadeUp .5s ease both; }
.hero .hi {
    font-size: clamp(2rem, 4vw, 3.2rem);
    font-weight: 700;
    line-height: 1.5;
    background: linear-gradient(100deg, #FFFFFF 20%, #A1A1AA 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero .sub {
    margin-top: .5rem;
    font-size: 1.2rem;
    font-weight: 500;
    color: var(--muted);
    line-height: 1.9;
}

/* ---------- Suggestion cards ---------- */
[data-testid="stMain"] .stButton > button {
    min-height: 78px;
    padding: .9rem 1rem;
    border-radius: 14px;
    border: 1px solid var(--border);
    background: var(--panel);
    color: var(--text);
    font-weight: 500;
    transition: border-color .18s ease, background .18s ease, transform .18s ease;
}
[data-testid="stMain"] .stButton > button p {
    unicode-bidi: plaintext;
    text-align: start;
    line-height: 1.8;
}
[data-testid="stMain"] .stButton > button:hover {
    background: var(--panel-hover);
    border-color: var(--border-hover);
    transform: translateY(-2px);
}

/* ---------- Messages ---------- */
[data-testid="stChatMessage"] {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 16px;
    padding: .8rem .65rem;
    animation: fadeUp .35s ease both;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li {
    color: var(--text);
    line-height: 1.95;
    text-align: start;
    unicode-bidi: plaintext;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: var(--panel);
    border-color: var(--border);
    padding: .8rem 1rem;
    scroll-margin-top: 1rem;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: none; }
}

/* ---------- Thinking ---------- */
.thinking {
    display: flex;
    align-items: center;
    gap: .6rem;
    padding: .5rem 0;
    color: var(--muted);
    font-weight: 500;
}
.thinking .dots span {
    display: inline-block;
    width: 6px;
    height: 6px;
    margin: 0 2px;
    border-radius: 50%;
    background: var(--accent);
    animation: bounce 1.2s infinite ease-in-out both;
}
.thinking .dots span:nth-child(2) { animation-delay: .15s; }
.thinking .dots span:nth-child(3) { animation-delay: .30s; }
@keyframes bounce {
    0%, 80%, 100% { opacity: .3; transform: translateY(0); }
    40%           { opacity: 1;  transform: translateY(-5px); }
}

/* ---------- Chat input ---------- */
[data-testid="stChatInput"] {
    border-radius: 16px;
    border: 1px solid var(--border);
    background: var(--panel);
    transition: border-color .18s ease;
}
[data-testid="stChatInput"]:focus-within { border-color: var(--accent); }
[data-testid="stChatInput"] textarea {
    color: var(--text);
    background: transparent;
    unicode-bidi: plaintext;
}
[data-testid="stChatInput"] textarea::placeholder { color: #6B6B72; }
[data-testid="stChatInput"] button {
    border-radius: 10px;
    transition: opacity .15s ease;
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox [data-baseweb="select"] > div {
    background-color: var(--panel);
    color: var(--text);
    border-color: var(--border);
    border-radius: 10px;
}

::-webkit-scrollbar { width: 7px; height: 7px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: #2A2A2E; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #3A3A40; }

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation: none !important; transition: none !important; }
}
</style>
""",
    unsafe_allow_html=True,
)


# ---------- History storage ----------
def load_chats() -> dict:
    if PERSIST and HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_chats() -> None:
    if not PERSIST:
        return
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(
        json.dumps(st.session_state.chats, ensure_ascii=False),
        encoding="utf-8",
    )


# ---------- State ----------
if "chats" not in st.session_state:
    st.session_state.chats = load_chats()
    st.session_state.active = None
    st.session_state.pending = None


def new_chat():
    st.session_state.active = None


def open_chat(cid):
    st.session_state.active = cid


def delete_chat(cid):
    st.session_state.chats.pop(cid, None)
    if st.session_state.active == cid:
        st.session_state.active = None
    save_chats()


def pick_suggestion(text):
    st.session_state.pending = text


# ---------- Input ----------
prompt = st.chat_input("اسأل عن دليل الكلية...")
if st.session_state.pending:
    prompt = st.session_state.pending
    st.session_state.pending = None

if prompt:
    if st.session_state.active not in st.session_state.chats:
        cid = uuid.uuid4().hex
        st.session_state.chats[cid] = {"title": prompt[:40], "messages": []}
        st.session_state.active = cid
    st.session_state.chats[st.session_state.active]["messages"].append(
        {"role": "user", "content": prompt}
    )
    save_chats()

active = st.session_state.active
messages = (
    st.session_state.chats[active]["messages"]
    if active in st.session_state.chats
    else []
)

# ---------- Sidebar ----------
with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), width=200)

    st.markdown("### مساعد كلية الذكاء الاصطناعي")
    st.button("＋  New chat", width="stretch", on_click=new_chat)

    if st.session_state.chats:
        st.markdown('<div class="side-label">المحادثات</div>', unsafe_allow_html=True)

    for cid in reversed(list(st.session_state.chats)):
        col_open, col_del = st.columns([5, 1])
        col_open.button(
            st.session_state.chats[cid]["title"],
            key=f"open_{cid}",
            width="stretch",
            type="primary" if cid == active else "secondary",
            on_click=open_chat,
            args=(cid,),
        )
        col_del.button("✕", key=f"del_{cid}", on_click=delete_chat, args=(cid,))

# ---------- Welcome ----------
if not messages:
    st.markdown(
        """
        <div class="hero">
            <div class="hi">أهلاً وسهلاً يا عزيزي الطالب</div>
            <div class="sub">إزاي أقدر أساعدك؟</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    columns = st.columns(len(SUGGESTIONS))
    for column, suggestion in zip(columns, SUGGESTIONS):
        column.button(
            suggestion,
            width="stretch",
            key=f"suggestion_{suggestion}",
            on_click=pick_suggestion,
            args=(suggestion,),
        )
else:
    # مساحة تحت عشان البرومبت الجديد يقدر يطلع لأول الصفحة
    st.markdown(
        "<style>[data-testid='stMainBlockContainer']{padding-bottom:60vh}</style>",
        unsafe_allow_html=True,
    )

# ---------- History ----------
for message in messages:
    avatar = AVATAR if message["role"] == "assistant" else "🎓"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ---------- Response ----------
if prompt:
    # اسكرول البرومبت الجديد لأول الصفحة
    components.html(
        """
        <script>
        const go = () => {
            const doc = window.parent.document;
            const users = doc.querySelectorAll(
                '[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])'
            );
            if (users.length) {
                users[users.length - 1].scrollIntoView({behavior: "smooth", block: "start"});
            }
        };
        [50, 250, 600].forEach(t => setTimeout(go, t));
        </script>
        """,
        height=0,
    )

    with st.chat_message("assistant", avatar=AVATAR):
        thinking = st.empty()
        thinking.markdown(
            '<div class="thinking"><span>جاري التفكير</span>'
            '<span class="dots"><span></span><span></span><span></span></span></div>',
            unsafe_allow_html=True,
        )

        def stream():
            first = True
            for chunk in chatbot.chat_stream(prompt, temperature=0.5, limit=5):
                if first:
                    thinking.empty()
                    first = False
                yield chunk
            if first:
                thinking.empty()

        try:
            reply = st.write_stream(stream())
        except Exception as e:
            thinking.empty()
            reply = "حصل خطأ أثناء توليد الرد، جرّب تاني."
            st.error(f"{reply}\n\n`{e}`")

    messages.append({"role": "assistant", "content": reply})
    save_chats()
