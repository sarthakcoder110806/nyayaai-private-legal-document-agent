"""Legal-themed look and feel for NyayaAI.

Everything here is inline CSS/SVG, so the app makes no external requests
(no web fonts, no remote images) and keeps its privacy promise.
"""

import html
import re

import streamlit as st

GOLD = "#c9a227"
NAVY = "#0b1220"
NAVY_2 = "#101b30"
IVORY = "#f3ead7"


def _compact(markup: str) -> str:
    """Remove newlines/indentation so Streamlit's markdown parser never
    treats the HTML as a code block or splits it at a blank line."""
    return re.sub(r"\s*\n\s*", "", markup).strip()


# ------------------------------------------------------------------ graphics
def logo_svg(size: int = 44) -> str:
    return _compact(f"""
    <svg viewBox="0 0 64 64" width="{size}" height="{size}"
         xmlns="http://www.w3.org/2000/svg" aria-label="NyayaAI logo">
      <circle cx="32" cy="32" r="30" fill="{NAVY_2}" stroke="{GOLD}" stroke-width="2"/>
      <g stroke="{GOLD}" stroke-width="2.5" stroke-linecap="round"
         stroke-linejoin="round" fill="none">
        <line x1="32" y1="13" x2="32" y2="50"/>
        <line x1="16" y1="21" x2="48" y2="21"/>
        <path d="M16 21 L9 35 Q16 40 23 35 Z"/>
        <path d="M48 21 L41 35 Q48 40 55 35 Z"/>
        <line x1="22" y1="50" x2="42" y2="50"/>
      </g>
      <circle cx="32" cy="12" r="2.8" fill="{GOLD}"/>
    </svg>
    """)


def courthouse_svg() -> str:
    columns = "".join(
        f'<rect x="{62 + i * 50}" y="88" width="22" height="84" rx="2" fill="url(#stone)"/>'
        f'<rect x="{58 + i * 50}" y="84" width="30" height="6" fill="{GOLD}" opacity=".85"/>'
        f'<rect x="{58 + i * 50}" y="170" width="30" height="6" fill="{GOLD}" opacity=".85"/>'
        for i in range(6)
    )

    return _compact(f"""
    <svg viewBox="0 0 400 220" xmlns="http://www.w3.org/2000/svg"
         style="width:100%;max-width:420px;height:auto"
         aria-label="Courthouse illustration">
      <defs>
        <linearGradient id="stone" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stop-color="#e9dcb8"/>
          <stop offset=".5" stop-color="#fff6dc"/>
          <stop offset="1" stop-color="#c9b681"/>
        </linearGradient>
        <linearGradient id="roof" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="{GOLD}"/>
          <stop offset="1" stop-color="#8a6d12"/>
        </linearGradient>
      </defs>
      <ellipse cx="200" cy="205" rx="190" ry="10" fill="#000" opacity=".25"/>
      <polygon points="36,72 200,12 364,72" fill="url(#roof)"/>
      <polygon points="64,68 200,20 336,68" fill="{NAVY_2}"/>
      <circle cx="200" cy="52" r="11" fill="none" stroke="{GOLD}" stroke-width="2"/>
      <line x1="200" y1="43" x2="200" y2="61" stroke="{GOLD}" stroke-width="2"/>
      <line x1="191" y1="49" x2="209" y2="49" stroke="{GOLD}" stroke-width="2"/>
      <rect x="36" y="72" width="328" height="12" fill="{GOLD}"/>
      {columns}
      <rect x="40" y="176" width="320" height="10" fill="#d9c88f"/>
      <rect x="28" y="186" width="344" height="10" fill="#bfae74"/>
      <rect x="16" y="196" width="368" height="10" fill="#a8975f"/>
    </svg>
    """)


def background_pattern() -> str:
    """Faint scales-of-justice watermark as a CSS data URI."""
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120'>"
        "<g stroke='%23c9a227' stroke-opacity='0.06' stroke-width='1.5' fill='none'>"
        "<line x1='60' y1='28' x2='60' y2='88'/><line x1='40' y1='40' x2='80' y2='40'/>"
        "<path d='M40 40 L32 58 Q40 63 48 58 Z'/><path d='M80 40 L72 58 Q80 63 88 58 Z'/>"
        "</g></svg>"
    )
    return f'url("data:image/svg+xml;utf8,{svg}")'


# --------------------------------------------------------------------- CSS
def _css() -> str:
    return f"""
<style>
#MainMenu, footer {{visibility: hidden;}}
[data-testid="stHeader"] {{background: transparent;}}

.stApp {{
    background:
        radial-gradient(1200px 600px at 85% -10%, rgba(201,162,39,.10), transparent 60%),
        radial-gradient(900px 500px at -10% 110%, rgba(60,90,160,.14), transparent 60%),
        {background_pattern()},
        {NAVY};
    color: {IVORY};
}}

.block-container {{max-width: 860px; padding-top: 2rem; padding-bottom: 7rem;}}

h1, h2, h3, h4, .brand-name, .hero h1 {{
    font-family: Georgia, "Times New Roman", serif !important;
    letter-spacing: .01em;
}}
h2, h3, h4 {{color: {IVORY};}}

/* ---------- sidebar */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0a1020 0%, #0d1628 100%);
    border-right: 1px solid rgba(201,162,39,.25);
}}
[data-testid="stSidebar"] .stButton > button {{
    text-align: left; justify-content: flex-start;
    border-radius: 10px; border: 1px solid transparent;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    border-color: rgba(201,162,39,.5);
}}
.brand {{display:flex; align-items:center; gap:.7rem; margin:.2rem 0 1rem 0;}}
.brand-name {{font-size:1.5rem; font-weight:700; color:{GOLD}; line-height:1;}}
.brand-tag {{font-size:.7rem; opacity:.65; text-transform:uppercase; letter-spacing:.12em;}}
.side-group {{
    font-size:.7rem; opacity:.6; margin:.9rem 0 .2rem .2rem;
    text-transform:uppercase; letter-spacing:.08em;
}}

/* ---------- buttons */
.stButton > button[kind="primary"], .stDownloadButton > button {{
    background: linear-gradient(180deg, {GOLD}, #a98414);
    color: #1a1405; border: none; font-weight: 600; border-radius: 10px;
}}
.stButton > button[kind="primary"]:hover, .stDownloadButton > button:hover {{
    filter: brightness(1.1); color:#1a1405;
}}
.stButton > button[kind="secondary"] {{border-radius: 10px;}}

/* ---------- hero */
.hero {{text-align:center; padding: 3vh 0 1rem 0;}}
.hero h1 {{
    font-size: 3rem; margin: .6rem 0 .2rem 0;
    background: linear-gradient(90deg, #f6e6a8, {GOLD}, #f6e6a8);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
}}
.hero p {{opacity:.8; font-size:1.08rem; margin:0;}}
.ornament {{
    display:flex; align-items:center; gap:.8rem; justify-content:center;
    color:{GOLD}; margin:1.2rem 0;
}}
.ornament::before, .ornament::after {{
    content:""; height:1px; width:90px;
    background: linear-gradient(90deg, transparent, {GOLD}, transparent);
}}

/* ---------- feature cards */
.features {{display:grid; grid-template-columns:repeat(3, 1fr); gap:.9rem; margin:1.2rem 0;}}
.feature {{
    background: rgba(16,27,48,.85); border:1px solid rgba(201,162,39,.28);
    border-radius:16px; padding:1.1rem 1rem; text-align:center;
    transition: transform .15s ease, border-color .15s ease;
}}
.feature:hover {{transform: translateY(-3px); border-color:{GOLD};}}
.feature .icon {{font-size:1.8rem;}}
.feature h4 {{margin:.4rem 0 .2rem 0; color:{GOLD}; font-size:1.02rem;}}
.feature p {{margin:0; font-size:.86rem; opacity:.78;}}
@media (max-width: 700px) {{.features {{grid-template-columns:1fr;}}}}

/* ---------- uploader */
[data-testid="stFileUploader"] section {{
    background: rgba(16,27,48,.7);
    border: 2px dashed rgba(201,162,39,.55); border-radius: 16px;
}}

/* ---------- chat */
[data-testid="stChatMessage"] {{
    background: rgba(16,27,48,.75); border:1px solid rgba(201,162,39,.18);
    border-radius: 16px; padding: 1rem 1.2rem; margin-bottom:.6rem;
}}
[data-testid="stChatInput"] {{border-radius: 24px; border:1px solid rgba(201,162,39,.4);}}
blockquote {{
    border-left: 3px solid {GOLD}; background: rgba(201,162,39,.07);
    padding: .4rem .9rem; border-radius: 0 8px 8px 0;
}}
[data-testid="stExpander"] {{
    border-radius: 14px; border: 1px solid rgba(201,162,39,.28);
    background: rgba(16,27,48,.6);
}}

/* ---------- document header */
.doc-header {{
    display:flex; align-items:center; gap:.9rem;
    padding: .9rem 1.1rem; margin-bottom:1rem; border-radius:16px;
    background: linear-gradient(90deg, rgba(201,162,39,.14), rgba(16,27,48,.6));
    border:1px solid rgba(201,162,39,.35);
}}
.doc-icon {{font-size:2rem;}}
.doc-title {{font-family: Georgia, serif; font-size:1.3rem; font-weight:700; color:{IVORY};}}
.doc-meta {{font-size:.8rem; opacity:.7;}}

/* ---------- status badges */
.badge {{
    display:inline-block; padding:.18rem .7rem; border-radius:999px;
    font-size:.75rem; font-weight:700; letter-spacing:.05em; margin:.3rem 0 .6rem 0;
}}
.badge-ok   {{background:rgba(46,160,110,.18); color:#5fe0a5; border:1px solid #2ea06e;}}
.badge-warn {{background:rgba(230,170,40,.18); color:#f2c45a; border:1px solid #d9a22b;}}
.badge-err  {{background:rgba(220,70,70,.18);  color:#ff8d8d; border:1px solid #dc4646;}}
.badge-info {{background:rgba(110,150,230,.18); color:#a9c4ff; border:1px solid #6e96e6;}}
</style>
"""


# ------------------------------------------------------------- components
def inject_theme() -> None:
    st.markdown(_css(), unsafe_allow_html=True)


def sidebar_brand() -> None:
    st.markdown(
        _compact(f"""
        <div class="brand">{logo_svg(46)}
          <div><div class="brand-name">NyayaAI</div>
          <div class="brand-tag">Private legal explainer</div></div>
        </div>
        """),
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        _compact(f"""
        <div class="hero">
          {courthouse_svg()}
          <h1>NyayaAI</h1>
          <p>Understand your legal documents. Protect your privacy.</p>
          <div class="ornament">&#9878;</div>
        </div>
        """),
        unsafe_allow_html=True,
    )


def render_features() -> None:
    st.markdown(
        _compact("""
        <div class="features">
          <div class="feature"><div class="icon">&#128274;</div>
            <h4>100% Private</h4>
            <p>Runs on your computer with a local model. Nothing is sent online.</p></div>
          <div class="feature"><div class="icon">&#128209;</div>
            <h4>Plain Language</h4>
            <p>Get clear summaries and answers instead of legal jargon.</p></div>
          <div class="feature"><div class="icon">&#9989;</div>
            <h4>Verified Quotes</h4>
            <p>Every answer is checked against the exact text and page.</p></div>
        </div>
        """),
        unsafe_allow_html=True,
    )


def render_doc_header(name: str, added: str) -> None:
    st.markdown(
        _compact(f"""
        <div class="doc-header"><div class="doc-icon">&#128220;</div>
          <div><div class="doc-title">{html.escape(name)}</div>
          <div class="doc-meta">Added {html.escape(added)} &middot;
          processed locally with Gemma</div></div>
        </div>
        """),
        unsafe_allow_html=True,
    )


def render_status_badge(status: str) -> None:
    if status in ("SUPPORTED", "SUMMARY_READY"):
        kind = "ok"
    elif status in ("PARTIALLY_SUPPORTED", "AMBIGUOUS"):
        kind = "warn"
    elif status in ("MODEL_ERROR", "ERROR"):
        kind = "err"
    else:
        kind = "info"

    label = html.escape(str(status).replace("_", " "))
    st.markdown(
        f'<span class="badge badge-{kind}">{label}</span>',
        unsafe_allow_html=True,
    )