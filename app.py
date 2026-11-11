"""
Government Scheme Eligibility Navigator - Streamlit Application
Professional civic-tech portal for Indian citizen scheme discovery.
Multi-Agent RAG, Intent Routing, LCEL, and ChromaDB.
"""
import streamlit as st
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add current directory to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from config import get_api_keys, DATA_DIR, CHROMA_PERSIST_DIR
from memory import CitizenProfile
from orchestrator import SchemeNavigatorOrchestrator
from ingest import ingest_documents

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Scheme Navigator | India",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ---- Global resets ---- */
[data-testid="stAppViewContainer"] {background:#f1f5f9;}
[data-testid="stSidebar"] {background:#ffffff; border-right:1px solid #e5e7eb;}
[data-testid="stChatInput"] textarea {border-radius:12px!important;}

/* ---- Government header ---- */
.gov-header {
    display:flex;
    justify-content:space-between;
    align-items:center;
    background:#1a2f5e;
    color:#ffffff;
    padding:16px 24px;
    border-radius:0;
    margin-bottom:0;
}
.gov-header-title {
    font-size:1.4rem;
    font-weight:700;
    letter-spacing:-0.5px;
    color:#ffffff;
}
.gov-divider {
    height:3px;
    background:#f59e0b;
    margin:0;
    margin-bottom:1rem;
}

/* ---- Chat bubbles ---- */
.chat-bubble-user {
    background:#e8f0fe;
    border-radius:18px 18px 4px 18px;
    padding:12px 16px;
    margin-left:20%;
    margin-bottom:0.75rem;
    color:#1e3a5f;
    font-size:0.95rem;
    line-height:1.5;
}
.chat-bubble-bot {
    background:#ffffff;
    border:1px solid #e5e7eb;
    border-radius:18px 18px 18px 4px;
    padding:16px 20px;
    margin-right:10%;
    margin-bottom:0.5rem;
    box-shadow:0 1px 3px rgba(0,0,0,0.08);
    font-size:0.95rem;
    line-height:1.6;
}

/* ---- Source pills ---- */
.source-pill {
    display:inline-block;
    background:#f0f9ff;
    border:1px solid #bae6fd;
    border-radius:20px;
    padding:2px 10px;
    font-size:0.75rem;
    color:#0369a1;
    margin:2px;
}

/* ---- Intent label ---- */
.intent-label {
    display:inline-block;
    background:#f8fafc;
    border:1px solid #e2e8f0;
    border-radius:4px;
    padding:2px 8px;
    font-size:0.7rem;
    color:#64748b;
    margin-top:8px;
}

/* ---- Scheme card ---- */
.scheme-card {
    background:#ffffff;
    border:1px solid #e5e7eb;
    border-radius:8px;
    padding:10px 14px;
    margin:4px 0;
    transition:border-color 0.15s;
}
.scheme-card:hover {border-color:#f59e0b;}

/* ---- Profile rows ---- */
.profile-row {
    display:flex;
    justify-content:space-between;
    padding:4px 0;
    border-bottom:1px solid #f1f5f9;
    font-size:0.875rem;
}
.profile-value  {color:#1a2f5e; font-weight:500;}
.profile-missing{color:#9ca3af; font-style:italic;}

/* ---- Sidebar sections ---- */
.sidebar-section {
    border-left:3px solid #f59e0b;
    padding-left:12px;
    margin-bottom:16px;
}
.sidebar-section h4 {
    font-size:0.8rem;
    font-weight:700;
    color:#374151;
    text-transform:uppercase;
    letter-spacing:0.5px;
    margin:0 0 6px 0;
}

/* ---- Footer ---- */
.footer-bar {
    background:#f8fafc;
    border-top:1px solid #e5e7eb;
    padding:12px 24px;
    font-size:0.75rem;
    color:#9ca3af;
    text-align:center;
    margin-top:2rem;
}

/* ---- Disclaimer / follow-up box ---- */
.disclaimer {
    background:#fffbeb;
    border:1px solid #fde68a;
    border-radius:6px;
    padding:8px 12px;
    font-size:0.85rem;
    color:#92400e;
    margin-bottom:0.5rem;
}

/* ---- Relevance bar ---- */
.relevance-bar {
    height:4px;
    background:#e5e7eb;
    border-radius:2px;
    margin-top:4px;
}
.relevance-fill {
    height:4px;
    border-radius:2px;
    background:linear-gradient(90deg,#f59e0b,#d97706);
}

/* ---- Scenario card buttons ---- */
div[data-testid="stButton"] > button {
    border-radius:10px!important;
    border:1px solid #e5e7eb!important;
    background:#ffffff!important;
    padding:14px 10px!important;
    text-align:left!important;
    width:100%!important;
    transition:border-color 0.15s, box-shadow 0.15s!important;
    white-space:normal!important;
    height:auto!important;
}
div[data-testid="stButton"] > button:hover {
    border-color:#f59e0b!important;
    box-shadow:0 2px 8px rgba(245,158,11,0.15)!important;
}

/* ---- API status dot ---- */
.dot-green {color:#059669; font-size:1rem;}
.dot-red   {color:#dc2626; font-size:1rem;}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Namaste! 🙏 I am your **Government Scheme Eligibility Navigator**.\n\n"
                "Describe your situation in plain language — your occupation, state, landholding, and income — "
                "or ask about any central or state scheme like **PM-KISAN**, **Ayushman Bharat**, or **PM-MUDRA**.\n\n"
                "Try one of the sample citizen scenarios below to get started!"
            ),
            "intent": "greeting",
            "trace": None
        }
    ]

if "profile" not in st.session_state:
    st.session_state.profile = CitizenProfile()

if "pending_input" not in st.session_state:
    st.session_state.pending_input = None

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="gov-header">
    <div>
        <span style="font-size:1.6rem">🇮🇳</span>
        <span class="gov-header-title"> Scheme Navigator</span>
        <div style="font-size:0.8rem;color:#93c5fd;margin-top:2px">
            AI-assisted eligibility checker for central and state government schemes
        </div>
    </div>
    <div style="text-align:right;font-size:0.75rem;color:#93c5fd">
        Data from Official Government Portals<br>
        <span style="color:#fbbf24">●</span> AI-Assisted | Not an official government service
    </div>
</div>
<div class="gov-divider"></div>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
SCHEME_DISPLAY_NAMES = {
    "pm_kisan_guidelines.pdf":           "PM-KISAN",
    "pm_awas_yojana_gramin.pdf":         "PMAY-G (Gramin Housing)",
    "ayushman_bharat_pmjay.pdf":         "Ayushman Bharat PM-JAY",
    "pm_svanidhi_guidelines.pdf":        "PM SVANidhi",
    "karnataka_raitha_vidya_nidhi.pdf":  "Karnataka Raitha Vidya Nidhi",
    "pm_fasal_bima_yojana.pdf":          "PM Fasal Bima Yojana",
    "sukanya_samriddhi_yojana.pdf":      "Sukanya Samriddhi Yojana",
    "pm_mudra_yojana.pdf":               "PM MUDRA Yojana",
    "atal_pension_yojana.pdf":           "Atal Pension Yojana",
    "pmegp.pdf":                         "PMEGP",
    "e_shram_card.pdf":                  "e-Shram Card",
    "pm_jan_dhan_yojana.pdf":            "PM Jan Dhan Yojana",
    "nfsa_ration_card.pdf":              "NFSA Ration Card",
    "senior_citizen_savings_scheme.pdf": "Senior Citizen Savings Scheme",
    "ladli_behna_yojana_mp.pdf":         "Ladli Behna Yojana (MP)",
}

def pretty_scheme_name(filename: str) -> str:
    return SCHEME_DISPLAY_NAMES.get(filename, filename.replace("_", " ").replace(".pdf", "").title())

def is_followup_question(response: str) -> bool:
    """Detect if the bot response is a short follow-up question asking for more info."""
    if "?" not in response:
        return False
    if len(response) > 300:
        return False
    scheme_keywords = ["pm-kisan", "ayushman", "pmay", "nrega", "svnidhi", "mudra",
                       "fasal bima", "sukanya", "atal pension", "pmegp", "jan dhan",
                       "ration", "ladli", "e-shram", "mgnregs"]
    lower = response.lower()
    return not any(kw in lower for kw in scheme_keywords)

def format_chat_export(messages) -> str:
    lines = ["SCHEME NAVIGATOR — CHAT EXPORT", "=" * 50, ""]
    for m in messages:
        role = "YOU" if m["role"] == "user" else "NAVIGATOR"
        lines.append(f"[{role}]")
        lines.append(m["content"])
        lines.append("")
    return "\n".join(lines)

def distance_color(d: float) -> str:
    if d < 0.8:
        return "#059669"   # green
    elif d <= 1.1:
        return "#f59e0b"   # yellow
    return "#dc2626"       # red

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo + branding
    try:
        st.image("https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg", width=55)
    except Exception:
        st.markdown("🇮🇳")

    st.markdown("<div style='height:4px;background:#f59e0b;border-radius:2px;margin:6px 0 14px 0'></div>",
                unsafe_allow_html=True)

    # ── 1. LLM selector ──────────────────────────────────────────────────────
    st.markdown("""
    <div class="sidebar-section">
        <h4>🤖 AI Model</h4>
    </div>
    """, unsafe_allow_html=True)

    api_keys = get_api_keys()
    provider_options = ["gemini", "groq", "openai"]
    display_names = {
        "gemini": "Google Gemini (Flash)",
        "groq":   "Groq (Llama-3.3-70B)",
        "openai": "OpenAI (GPT-4o-mini)",
    }
    selected_provider = st.selectbox(
        "LLM Provider",
        options=provider_options,
        index=0,
        format_func=lambda x: display_names.get(x, x),
        label_visibility="collapsed"
    )

    active_key = api_keys.get(selected_provider, "")
    is_key_present = bool(active_key and "your_" not in active_key)

    if is_key_present:
        st.markdown(
            f'<span class="dot-green">●</span> '
            f'<span style="font-size:0.8rem;color:#374151">{display_names[selected_provider]} API key active</span>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<span class="dot-red">●</span> '
            f'<span style="font-size:0.8rem;color:#374151">{display_names[selected_provider]} API key missing</span>',
            unsafe_allow_html=True
        )
        custom_key = st.text_input(
            f"Enter {selected_provider.title()} API Key",
            type="password",
            placeholder="Paste key here or update .env",
        )
        if custom_key:
            env_map = {"gemini": "GEMINI_API_KEY", "groq": "GROQ_API_KEY", "openai": "OPENAI_API_KEY"}
            os.environ[env_map[selected_provider]] = custom_key
            st.rerun()

    st.markdown("<div style='margin:14px 0'></div>", unsafe_allow_html=True)

    # ── 2. Citizen Profile ────────────────────────────────────────────────────
    st.markdown("""
    <div class="sidebar-section">
        <h4>👤 Citizen Profile</h4>
    </div>
    """, unsafe_allow_html=True)

    p = st.session_state.profile
    profile_fields = [
        ("State",      p.state,                       p.state or None),
        ("Occupation", p.occupation,                  p.occupation or None),
        ("Age",        f"{p.age} yrs" if p.age else None,          p.age),
        ("Land",       f"{p.landholding_acres} acres" if p.landholding_acres else None, p.landholding_acres),
        ("Income",     f"₹{p.annual_income:,.0f}/yr" if p.annual_income else None,      p.annual_income),
        ("Category",   p.category,                    p.category or None),
        ("Housing",    p.housing_type,                p.housing_type or None),
    ]

    rows_html = ""
    for label, display_val, raw_val in profile_fields:
        if raw_val is not None:
            val_html = f'<span class="profile-value">{display_val}</span>'
        else:
            val_html = '<span class="profile-missing">Not specified</span>'
        rows_html += f'<div class="profile-row"><span>{label}</span>{val_html}</div>'

    st.markdown(f'<div style="margin-bottom:10px">{rows_html}</div>', unsafe_allow_html=True)

    if st.button("🔄 Clear Profile & Chat", use_container_width=True):
        st.session_state.profile = CitizenProfile()
        st.session_state.messages = st.session_state.messages[:1]  # keep greeting
        st.rerun()

    st.markdown("<div style='margin:14px 0'></div>", unsafe_allow_html=True)

    # ── 3. Knowledge Base ─────────────────────────────────────────────────────
    st.markdown("""
    <div class="sidebar-section">
        <h4>📚 Knowledge Base</h4>
    </div>
    """, unsafe_allow_html=True)

    pdf_files = list(DATA_DIR.glob("*.pdf")) if DATA_DIR.exists() else []
    scheme_count = len(pdf_files)
    st.markdown(
        f'<span style="font-size:0.8rem;color:#374151">'
        f'<strong>{scheme_count}</strong> schemes indexed</span>',
        unsafe_allow_html=True
    )

    # Last indexed date
    index_meta_path = Path(CHROMA_PERSIST_DIR) / "index_meta.json"
    try:
        with open(index_meta_path) as f:
            meta = json.load(f)
        last_idx = meta.get("last_indexed", "")
        if last_idx:
            try:
                dt = datetime.fromisoformat(last_idx)
                last_idx = dt.strftime("%d %b %Y, %H:%M")
            except Exception:
                pass
            st.markdown(
                f'<span style="font-size:0.75rem;color:#9ca3af">Last indexed: {last_idx}</span>',
                unsafe_allow_html=True
            )
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass

    if pdf_files:
        pills_html = " ".join(
            f'<span class="source-pill">{pretty_scheme_name(f.name)}</span>'
            for f in sorted(pdf_files)
        )
        st.markdown(f'<div style="margin-top:6px;line-height:2">{pills_html}</div>',
                    unsafe_allow_html=True)

    with st.expander("⚙️ Re-ingest Documents"):
        if st.button("🔃 Ingest / Re-index Now", use_container_width=True):
            with st.spinner("Ingesting documents into ChromaDB…"):
                try:
                    ingest_documents()
                    st.success("✅ Ingestion complete!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Ingestion failed: {e}")

    st.markdown("<div style='margin:14px 0'></div>", unsafe_allow_html=True)

    # ── 4. Export ─────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="sidebar-section">
        <h4>💾 Export</h4>
    </div>
    """, unsafe_allow_html=True)

    chat_export_text = format_chat_export(st.session_state.messages)
    st.download_button(
        label="⬇️ Export Chat as Text",
        data=chat_export_text,
        file_name="scheme_navigator_chat.txt",
        mime="text/plain",
        use_container_width=True
    )

    # ── Disclaimer ────────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="disclaimer">
        ⚠️ <strong>Disclaimer:</strong> This tool provides informational guidance only.
        For official applications, visit <strong>india.gov.in</strong> or
        <strong>myscheme.gov.in</strong>. Not an official government service.
    </div>
    """, unsafe_allow_html=True)

# ── MAIN CONTENT AREA ─────────────────────────────────────────────────────────

# ── Scenario cards ─────────────────────────────────────────────────────────
scenarios = [
    {
        "icon": "👨‍🌾",
        "name": "Ramesh, Karnataka Farmer",
        "desc": "45 yrs • 2 acres • ₹90k income",
        "msg": "I'm a 45-year-old farmer in Karnataka with 2 acres of land and an annual income of ₹90,000. What government schemes can I get?"
    },
    {
        "icon": "🏪",
        "name": "Priya, Street Vendor",
        "desc": "Urban vendor • Pune • No fixed income",
        "msg": "I am a 35-year-old street vendor in Pune. I sell vegetables on the roadside. What schemes can help me?"
    },
    {
        "icon": "💊",
        "name": "Check Ayushman Bharat",
        "desc": "Health coverage eligibility",
        "msg": "Am I eligible for Ayushman Bharat PM-JAY health insurance?"
    },
]

cols = st.columns(3)
clicked_prompt = None
for i, scenario in enumerate(scenarios):
    with cols[i]:
        btn_label = (
            f"{scenario['icon']}  **{scenario['name']}**\n\n"
            f"<small style='color:#6b7280'>{scenario['desc']}</small>"
        )
        if st.button(
            f"{scenario['icon']}  {scenario['name']}\n{scenario['desc']}",
            key=f"scenario_{i}",
            use_container_width=True
        ):
            clicked_prompt = scenario["msg"]

st.markdown("<div style='margin-bottom:1rem'></div>", unsafe_allow_html=True)

# ── Render chat messages ───────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="chat-bubble-user">{msg["content"]}</div>',
            unsafe_allow_html=True
        )
    else:
        # Bot message
        response = msg["content"]
        trace = msg.get("trace")
        intent = msg.get("intent", "")

        # Determine if it's a follow-up question
        if is_followup_question(response) and intent != "greeting":
            st.markdown(
                f'<div class="disclaimer">📋 <strong>More information needed</strong><br>{response}</div>',
                unsafe_allow_html=True
            )
        else:
            with st.container():
                st.markdown(f'<div class="chat-bubble-bot">', unsafe_allow_html=True)
                st.markdown(response)
                st.markdown('</div>', unsafe_allow_html=True)

        # Source pills from trace
        if trace and trace.get("citations_summary"):
            raw_citations = trace["citations_summary"]
            # Extract scheme names from citations markdown lines
            import re as _re
            scheme_names = _re.findall(r"\*\*(.+?)\*\*", raw_citations)
            if scheme_names:
                pills = " ".join(
                    f'<span class="source-pill">📄 {name}</span>'
                    for name in scheme_names
                )
                st.markdown(
                    f'<div style="margin-top:4px;margin-left:4px">{pills}</div>',
                    unsafe_allow_html=True
                )

        # Intent label
        if intent and intent != "greeting":
            label_text = intent.replace("_", " ").title()
            st.markdown(
                f'<span class="intent-label">⚡ {label_text}</span>',
                unsafe_allow_html=True
            )

        # Agent Decision Log expander
        if trace:
            with st.expander("🔍 Agent Decision Log"):
                # Routing table
                routing = trace.get("intent_routing", {})
                if routing:
                    intent_val = routing.get("intent", "—")
                    needs_ret  = "✅ Yes" if routing.get("needs_retrieval") else "❌ No"
                    search_q   = routing.get("search_query", "—")
                    st.markdown(
                        f"""
                        <table style="width:100%;font-size:0.8rem;border-collapse:collapse">
                        <tr style="background:#f8fafc">
                            <th style="padding:6px 8px;text-align:left;border:1px solid #e2e8f0">Intent</th>
                            <th style="padding:6px 8px;text-align:left;border:1px solid #e2e8f0">Needs Retrieval</th>
                            <th style="padding:6px 8px;text-align:left;border:1px solid #e2e8f0">Search Query</th>
                        </tr>
                        <tr>
                            <td style="padding:6px 8px;border:1px solid #e2e8f0"><code>{intent_val}</code></td>
                            <td style="padding:6px 8px;border:1px solid #e2e8f0">{needs_ret}</td>
                            <td style="padding:6px 8px;border:1px solid #e2e8f0;font-style:italic">{search_q}</td>
                        </tr>
                        </table>
                        """,
                        unsafe_allow_html=True
                    )

                # Retrieved chunks
                chunks = trace.get("retrieved_chunks", [])
                if chunks:
                    st.markdown(
                        f"<div style='margin-top:12px;font-size:0.8rem;font-weight:600;color:#374151'>"
                        f"Retrieved Chunks ({len(chunks)})</div>",
                        unsafe_allow_html=True
                    )
                    for idx, c in enumerate(chunks, 1):
                        dist = c.get("distance", 0)
                        d_color = distance_color(dist)
                        with st.expander(
                            f"Chunk {idx}: {c.get('scheme', '—')}  |  dist={dist:.3f}"
                        ):
                            st.markdown(
                                f'<div style="font-size:0.75rem;color:{d_color};font-weight:600">'
                                f'Distance: {dist:.3f}</div>',
                                unsafe_allow_html=True
                            )
                            st.text(c.get("content", "")[:200] + ("…" if len(c.get("content", "")) > 200 else ""))
                else:
                    st.info("No retrieval needed for this turn.")

                # CoT reasoning
                if trace.get("eligibility_findings"):
                    st.markdown("**Chain-of-Thought Reasoning:**")
                    st.markdown(trace["eligibility_findings"])

# ── Chat input ─────────────────────────────────────────────────────────────
user_input = st.chat_input("Describe your profile or ask about a scheme…")
if clicked_prompt:
    user_input = clicked_prompt

st.caption("🔒 Your inputs are processed privately. We do not store personal information.")

# ── Process input ──────────────────────────────────────────────────────────
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Show thinking status
    with st.status("🤖 Multi-Agent Crew processing…", expanded=True) as status:
        st.write("🧠 Extracting profile details & detecting intent…")
        try:
            orchestrator = SchemeNavigatorOrchestrator(provider=selected_provider)
            st.write("🔍 Retrieval Agent querying ChromaDB…")
            st.write("⚖️ Eligibility Agent evaluating criteria with Chain-of-Thought…")
            st.write("📋 Application Agent compiling document checklist…")
            st.write("✍️ Explainer Agent synthesising plain-language response…")

            result = orchestrator.process_message(
                user_message=user_input,
                current_profile=st.session_state.profile,
                chat_history=st.session_state.messages
            )
            status.update(label="✅ Analysis complete!", state="complete", expanded=False)
        except Exception as e:
            status.update(label="❌ Error during processing", state="error", expanded=True)
            st.error(f"Execution error: {e}")
            st.stop()

    intent_val = result["intent_routing"].get("intent", "scheme_discovery")
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["final_response"],
        "intent": intent_val,
        "trace": result
    })
    st.rerun()

# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-bar">
Data compiled from official government portals including pmkisan.gov.in, pmjay.gov.in,
pmsvanidhi.mohua.gov.in and others.
For official applications, visit <strong>india.gov.in</strong> or <strong>myscheme.gov.in</strong>.
This tool is for informational guidance only and is not an official government service.
</div>
""", unsafe_allow_html=True)
