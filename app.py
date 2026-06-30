import streamlit as st
import uuid
from dotenv import load_dotenv
import html as html_lib

load_dotenv()

st.set_page_config(
    page_title="ITSM AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body { margin: 0; padding: 0; }
* { box-sizing: border-box; }

[data-testid="stAppViewContainer"] { background: #070B18 !important; }
[data-testid="stMain"] { background: #070B18 !important; }
.block-container { max-width: 100% !important; padding: 24px 40px !important; width: 100% !important; }
[data-testid="stHeader"] { display: none !important; }
#MainMenu, footer { display: none !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0D1425 !important;
    border-right: 1px solid #1A2744 !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {
    font-family: 'Inter', sans-serif !important;
}

.sidebar-logo { font-size:26px; font-weight:700; color:#F1F5F9; letter-spacing:-0.5px; padding:8px 0 4px; }
.sidebar-sub { font-size:15px; color:#4A5568; margin-bottom:14px; }
.status-pill {
    display:inline-flex; align-items:center; gap:8px;
    background:#0A2318; border:1px solid #166534;
    color:#4ADE80; padding:7px 16px; border-radius:20px;
    font-size:15px; font-weight:500; margin-bottom:20px;
    font-family:'Inter',sans-serif;
}
.status-dot { width:8px; height:8px; border-radius:50%; background:#4ADE80; animation:blink 2s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
.section-label { font-size:13px; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#3B5070; margin:18px 0 10px; font-family:'Inter',sans-serif; }
.tool-block { background:#121D35; border:1px solid #1E2E50; border-radius:10px; padding:13px 15px; margin-bottom:9px; }
.tool-name { font-size:15px; font-weight:600; color:#60A5FA; font-family:'JetBrains Mono',monospace; margin-bottom:4px; }
.tool-desc { font-size:13px; color:#4A5568; font-family:'Inter',sans-serif; }
hr.divider { border:none; border-top:1px solid #1A2744; margin:16px 0; }

/* Page header */
.page-header {
    background:linear-gradient(135deg,#0D1425 0%,#111827 100%);
    border:1px solid #1A2744; border-radius:18px;
    padding:32px 40px; margin-bottom:28px;
    position:relative; overflow:hidden; width:100%;
}
.page-header::before {
    content:''; position:absolute; top:0; left:0; right:0; height:3px;
    background:linear-gradient(90deg,#3B82F6 0%,#8B5CF6 50%,#06B6D4 100%);
}
.header-title { font-size:38px; font-weight:700; color:#F8FAFC; letter-spacing:-1px; margin:0 0 8px; font-family:'Inter',sans-serif; }
.header-sub { font-size:17px; color:#4A5568; font-family:'Inter',sans-serif; }
.header-sub span { color:#3B82F6; font-weight:500; }

/* Stats */
.stats-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:28px; width:100%; }
.stat-box {
    background:#0D1425; border:1px solid #1A2744;
    border-radius:14px; padding:22px 24px; text-align:center;
    position:relative; overflow:hidden;
}
.stat-box::before {
    content:''; position:absolute; bottom:0; left:0; right:0; height:2px;
    background:linear-gradient(90deg,transparent,#3B82F6,transparent); opacity:0.5;
}
.stat-number { font-size:42px; font-weight:700; color:#3B82F6; font-family:'JetBrains Mono',monospace; line-height:1; margin-bottom:8px; }
.stat-text { font-size:13px; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#3B5070; font-family:'Inter',sans-serif; }

/* Chat window */
.chat-window {
    background:#0D1425; border:1px solid #1A2744;
    border-radius:18px; padding:24px 32px;
    min-height:400px; margin-bottom:20px; width:100%;
}

/* USER message — right aligned */
.msg-user-row {
    display:flex; justify-content:flex-end;
    margin:14px 0;
}
.msg-user-bubble {
    background:linear-gradient(135deg,#1D4ED8,#2563EB);
    color:#F8FAFC;
    padding:16px 22px;
    border-radius:22px 22px 5px 22px;
    max-width:65%;
    font-size:18px;
    line-height:1.7;
    font-family:'Inter',sans-serif;
    box-shadow:0 4px 20px rgba(59,130,246,0.25);
    word-wrap:break-word;
}

/* AGENT message — left aligned */
.msg-agent-row {
    display:flex; align-items:flex-start;
    gap:14px; margin:14px 0;
}
.msg-avatar {
    width:42px; height:42px; border-radius:12px;
    background:linear-gradient(135deg,#3B82F6,#8B5CF6);
    display:flex; align-items:center; justify-content:center;
    font-size:20px; flex-shrink:0; margin-top:2px;
    box-shadow:0 4px 12px rgba(59,130,246,0.3);
}
.msg-agent-bubble {
    background:#121D35; border:1px solid #1E2E50;
    color:#E2E8F0;
    padding:16px 22px;
    border-radius:5px 22px 22px 22px;
    max-width:70%;
    font-size:18px;
    line-height:1.75;
    font-family:'Inter',sans-serif;
    word-wrap:break-word;
}
.tool-tags { display:flex; flex-wrap:wrap; gap:7px; margin-bottom:10px; }
.tool-tag {
    display:inline-flex; align-items:center; gap:5px;
    background:#0A1628; border:1px solid #1A3A6A;
    color:#60A5FA; padding:5px 12px; border-radius:7px;
    font-size:13px; font-family:'JetBrains Mono',monospace; font-weight:500;
}

/* Empty state */
.empty-state { display:flex; flex-direction:column; align-items:center; justify-content:center; padding:60px 20px; }
.empty-icon { font-size:60px; margin-bottom:18px; }
.empty-title { font-size:24px; font-weight:600; color:#3B5070; margin-bottom:8px; font-family:'Inter',sans-serif; }
.empty-desc { font-size:16px; color:#2A3A55; margin-bottom:24px; font-family:'Inter',sans-serif; }
.chips-row { display:flex; flex-wrap:wrap; gap:10px; justify-content:center; }
.chip {
    background:#0D1425; border:1px solid #1A2F55; color:#60A5FA;
    padding:10px 20px; border-radius:24px; font-size:15px;
    font-weight:500; font-family:'Inter',sans-serif;
}

/* Chat input */
[data-testid="stChatInput"] > div {
    background:#0D1425 !important;
    border:1px solid #1A2744 !important;
    border-radius:16px !important;
}
[data-testid="stChatInput"] textarea {
    background:#0D1425 !important;
    color:#E2E8F0 !important;
    font-size:18px !important;
    font-family:'Inter',sans-serif !important;
    line-height:1.6 !important;
    border:none !important;
    outline:none !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color:#2A3A55 !important;
    font-size:18px !important;
    font-family:'Inter',sans-serif !important;
}

/* Button */
.stButton > button {
    background:#121D35 !important; color:#60A5FA !important;
    border:1px solid #1E2E50 !important; border-radius:10px !important;
    font-size:15px !important; font-weight:500 !important;
    padding:10px 16px !important; width:100% !important;
    font-family:'Inter',sans-serif !important;
}
.stButton > button:hover { background:#0A1628 !important; border-color:#3B82F6 !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">⚡ AI Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">ITSM Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="status-pill"><div class="status-dot"></div>Online</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Available Tools</div>', unsafe_allow_html=True)
    for icon, name, desc in [
        ("🔍", "search_knowledge_base", "IT policies & procedures"),
        ("🗄️", "query_incidents",        "Live incident database"),
        ("🌐", "web_search",             "Real-time web results"),
    ]:
        st.markdown(f'<div class="tool-block"><div class="tool-name">{icon} {name}</div><div class="tool-desc">{desc}</div></div>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Model</div>', unsafe_allow_html=True)
    st.markdown('<div class="tool-block"><div class="tool-name">🦙 Llama 4 Scout</div><div class="tool-desc">meta-llama/llama-4-scout-17b</div></div>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    if st.button("🗑️  Clear conversation"):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.tool_call_count = 0
        st.rerun()

# ── Session state ─────────────────────────────────────────────────────────────
if "messages"        not in st.session_state: st.session_state.messages = []
if "thread_id"       not in st.session_state: st.session_state.thread_id = str(uuid.uuid4())
if "tool_call_count" not in st.session_state: st.session_state.tool_call_count = 0

# ── Header ────────────────────────────────────────────────────────────────────
msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])

st.markdown("""
<div class="page-header">
    <div class="header-title">🤖 ITSM AI Agent</div>
    <div class="header-sub">Powered by <span>LangGraph</span> &nbsp;·&nbsp; <span>Groq</span> &nbsp;·&nbsp; <span>ChromaDB</span> &nbsp;·&nbsp; <span>Tavily</span></div>
</div>
""", unsafe_allow_html=True)

# ── Stats ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="stats-grid">
    <div class="stat-box"><div class="stat-number">{msg_count}</div><div class="stat-text">Messages</div></div>
    <div class="stat-box"><div class="stat-number">{st.session_state.tool_call_count}</div><div class="stat-text">Tool Calls</div></div>
    <div class="stat-box"><div class="stat-number">3</div><div class="stat-text">Tools Active</div></div>
    <div class="stat-box"><div class="stat-number" style="color:#4ADE80">10/10</div><div class="stat-text">Eval Score</div></div>
</div>
""", unsafe_allow_html=True)

# ── Chat window (pure HTML — full control over alignment and font) ─────────────
chat_html = '<div class="chat-window">'

if not st.session_state.messages:
    chat_html += """
    <div class="empty-state">
        <div class="empty-icon">🤖</div>
        <div class="empty-title">ITSM AI Agent ready</div>
        <div class="empty-desc">Ask about incidents, IT policies, or search the web</div>
        <div class="chips-row">
            <span class="chip">How do I reset my password?</span>
            <span class="chip">Show me all critical incidents</span>
            <span class="chip">How do I set up VPN?</span>
            <span class="chip">Latest ransomware threats?</span>
        </div>
    </div>"""
else:
    for msg in st.session_state.messages:
        # Escape content to prevent HTML injection
        content = html_lib.escape(msg["content"]).replace('\n', '<br>')
        if msg["role"] == "user":
            chat_html += f"""
            <div class="msg-user-row">
                <div class="msg-user-bubble">{content}</div>
            </div>"""
        else:
            tools_html = ""
            if msg.get("tools_used"):
                tags = "".join([f'<span class="tool-tag">⚡ {t}</span>' for t in msg["tools_used"]])
                tools_html = f'<div class="tool-tags">{tags}</div>'
            chat_html += f"""
            <div class="msg-agent-row">
                <div class="msg-avatar">🤖</div>
                <div class="msg-agent-bubble">{tools_html}{content}</div>
            </div>"""

chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask about incidents, IT policies, or anything else..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("🤖 Agent thinking..."):
        try:
            from agent import build_agent

            @st.cache_resource
            def get_agent():
                return build_agent()

            agent     = get_agent()
            config    = {"configurable": {"thread_id": st.session_state.thread_id}}

            from langchain_core.messages import AIMessage, ToolMessage as LCToolMessage
            result    = agent.invoke({"messages": [("user", prompt)]}, config=config)

            answer    = ""
            tools_used = []
            for m in result["messages"]:
                if isinstance(m, LCToolMessage):
                    tools_used.append(m.name)
                    st.session_state.tool_call_count += 1
                if isinstance(m, AIMessage) and m.content:
                    answer = m.content

            st.session_state.messages.append({
                "role":       "assistant",
                "content":    answer,
                "tools_used": list(dict.fromkeys(tools_used))
            })
        except Exception as e:
            st.session_state.messages.append({
                "role":       "assistant",
                "content":    f"⚠️ Error: {str(e)}",
                "tools_used": []
            })

    st.rerun()