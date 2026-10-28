import base64
from pathlib import Path

import streamlit as st

# Colour palette (works on a dark night-city background)
CYAN, PURPLE, GREEN, ORANGE, PINK = "#22d3ee", "#a78bfa", "#34d399", "#fbbf24", "#fb7185"
PALETTE = [CYAN, PURPLE, GREEN, ORANGE, PINK]


@st.cache_data
def _b64(path: str):
    # Read an image once and return it as a base64 string (None if missing)
    p = Path(path)
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else None


def _image_css():
    bg, side = _b64("assets/bg.jpg"), _b64("assets/sidebar.jpg")
    css = ""
    if bg:  # photo background, lighter at the top so the city lights show through
        css += (".stApp {background:"
                " radial-gradient(900px 500px at 85% -5%, rgba(34,211,238,.14), transparent 60%),"
                " radial-gradient(800px 500px at 5% 10%, rgba(167,139,250,.12), transparent 60%),"
                " linear-gradient(180deg, rgba(6,12,28,.62) 0%, rgba(6,12,28,.84) 100%),"
                f" url(data:image/jpeg;base64,{bg}) center/cover fixed;}}")
    if side:  # sidebar photo with a dark fade
        css += ("[data-testid=stSidebar] > div:first-child {background:"
                " linear-gradient(180deg, rgba(7,13,31,.55) 0%, rgba(7,13,31,.92) 100%),"
                f" url(data:image/jpeg;base64,{side}) center/cover;}}")
    return css


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, .stApp, [class*="css"] {font-family: 'Plus Jakarta Sans', sans-serif;}
.stApp {color: #e8f0ff; font-size: 16px;}
[data-testid="stHeader"] {background: transparent;}
[data-testid="stAppDeployButton"], [data-testid="stMainMenu"], footer {display: none !important;}
.block-container {padding-top: 1.6rem; max-width: 1800px;}
::-webkit-scrollbar {width: 8px; height: 8px;} ::-webkit-scrollbar-thumb {background: #27406f; border-radius: 8px;}

/* ---------- headings ---------- */
h1 {font-size: 40px !important; font-weight: 800 !important; letter-spacing: -.5px; color: #f4f8ff !important;}
h2, h3 {color: #f4f8ff !important; font-weight: 700 !important;}
[data-testid="stCaptionContainer"] p {font-size: 15px !important; color: #a9bde0 !important;}
[data-testid="stMarkdownContainer"] p {font-size: 15.5px;}
[data-testid="stWidgetLabel"] p {color: #c4d6f7 !important; font-size: 14px !important; font-weight: 600;}

/* ---------- sidebar ---------- */
.brand {display: flex; align-items: center; gap: 14px; padding: 8px 0 6px 0;}
.brand svg {flex: none; filter: drop-shadow(0 0 14px rgba(34,211,238,.55));}
.brand .name {font-size: 28px; font-weight: 800; letter-spacing: .3px; line-height: 1.1;
    background: linear-gradient(90deg, #ffffff, #67e8f9); -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;}
.brand .tag {font-size: 10.5px; font-weight: 700; letter-spacing: .2em; margin-top: 5px; color: #8fb3e8;}
section[data-testid="stSidebar"][aria-expanded="true"] {width: 320px !important;}
[data-testid="stSidebar"] {border-right: 1px solid rgba(96,165,250,.25);}
[data-testid="stSidebar"] * {color: #dbe8ff !important;}
[data-testid="stSidebar"] h2 {font-size: 30px !important; font-weight: 800 !important; letter-spacing: .3px;
    padding: 6px 0 0 0; text-shadow: 0 0 22px rgba(34,211,238,.55);}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {font-size: 11.5px !important; letter-spacing: .14em; color: #8fb3e8 !important;}
[data-testid="stSidebar"] hr {border-color: rgba(96,165,250,.25);}
[data-testid="stSidebar"] .stRadio > label p {font-size: 12px !important; letter-spacing: .16em; color: #8fb3e8 !important; font-weight: 700;}
[data-testid="stSidebar"] [role="radiogroup"] {gap: 10px; flex-direction: column;}
[data-testid="stSidebar"] [role="radiogroup"] > div {width: 100%;}
[data-testid="stSidebar"] label[data-testid="stRadioOption"] {width: 100%; padding: 14px 18px !important; border-radius: 14px;
    background: rgba(15,28,58,.62); border: 1px solid rgba(96,165,250,.22); transition: all .2s ease; backdrop-filter: blur(6px);}
[data-testid="stSidebar"] label[data-testid="stRadioOption"] p {font-size: 17px !important; font-weight: 600;}
[data-testid="stSidebar"] label[data-testid="stRadioOption"]:hover {border-color: #22d3ee; transform: translateX(4px); background: rgba(34,211,238,.12);}
[data-testid="stSidebar"] label[data-testid="stRadioOption"]:has(input:checked) {
    background: linear-gradient(100deg, rgba(34,211,238,.38), rgba(139,92,246,.38));
    border-color: #67e8f9; box-shadow: 0 0 22px rgba(34,211,238,.35), inset 0 0 12px rgba(255,255,255,.06);}

/* radio buttons everywhere: hide the dot and show pills */
label[data-testid="stRadioOption"] > div:first-child:not(:has(p)),
label[data-testid="stRadioOption"] > div > div:first-child:not(:has(p)),
label[data-baseweb="radio"] > div:first-child:not(:has(p)) {display: none !important;}
[data-testid="stMain"] [role="radiogroup"] {gap: 10px;}
[data-testid="stMain"] label[data-testid="stRadioOption"] {padding: 11px 26px; border-radius: 999px; background: rgba(15,28,58,.7);
    border: 1px solid rgba(96,165,250,.3); transition: all .2s ease;}
[data-testid="stMain"] label[data-testid="stRadioOption"] p {font-size: 16.5px !important; font-weight: 600; color: #cfe0ff !important;}
[data-testid="stMain"] label[data-testid="stRadioOption"]:hover {border-color: #22d3ee;}
[data-testid="stMain"] label[data-testid="stRadioOption"]:has(input:checked) {background: linear-gradient(100deg, #0891b2, #7c3aed);
    border-color: #67e8f9; box-shadow: 0 0 18px rgba(34,211,238,.4);}
[data-testid="stMain"] label[data-testid="stRadioOption"]:has(input:checked) p {color: #ffffff !important;}

/* ---------- hero + glitter chips ---------- */
.hero {position: relative; overflow: hidden; border-radius: 22px; padding: 52px 40px 46px 40px; margin-bottom: 24px; text-align: center;
    border: 1px solid rgba(103,232,249,.45); backdrop-filter: blur(10px);
    background: linear-gradient(115deg, rgba(34,211,238,.22), rgba(139,92,246,.20) 55%, rgba(8,16,38,.78));
    box-shadow: 0 10px 40px rgba(0,0,0,.35), 0 0 30px rgba(34,211,238,.12);}
.hero::before {content: ""; position: absolute; inset: 0; pointer-events: none; opacity: .9;
    background-image: radial-gradient(circle at 12% 30%, #fff 0 1px, transparent 2px),
        radial-gradient(circle at 38% 75%, #bae6fd 0 1px, transparent 2px),
        radial-gradient(circle at 63% 22%, #fff 0 1.5px, transparent 2.5px),
        radial-gradient(circle at 82% 68%, #ddd6fe 0 1px, transparent 2px),
        radial-gradient(circle at 93% 25%, #fff 0 1px, transparent 2px);
    animation: twinkle 3.5s ease-in-out infinite alternate;}
@keyframes twinkle {from {opacity: .25;} to {opacity: 1;}}
.hero h1 {font-size: 54px !important; line-height: 1.12; letter-spacing: -1.2px; margin: 0 0 14px 0; position: relative;
    background: linear-gradient(90deg, #ffffff, #a5f3fc 60%, #c4b5fd); -webkit-background-clip: text;
    background-clip: text; -webkit-text-fill-color: transparent;}
.hero p {color: #c7d8f5; margin: 0 auto; max-width: 760px; font-size: 20px; line-height: 1.6; font-weight: 500; position: relative;}.feat {display: flex; justify-content: center; gap: 18px; margin-top: 30px; flex-wrap: wrap; position: relative;}
.feat div {position: relative; overflow: hidden; padding: 14px 28px; border-radius: 999px; font-size: 16.5px; font-weight: 700;
    color: #f0f9ff; border: 1px solid rgba(165,243,252,.6); cursor: default; transition: all .25s ease;
    background: linear-gradient(135deg, rgba(34,211,238,.30), rgba(139,92,246,.32));
    box-shadow: 0 0 20px rgba(34,211,238,.25), inset 0 0 14px rgba(255,255,255,.08);}
.feat div::after {content: ""; position: absolute; top: 0; left: -70%; width: 45%; height: 100%; transform: skewX(-22deg);
    background: linear-gradient(100deg, transparent, rgba(255,255,255,.55), transparent); animation: shine 3.4s ease-in-out infinite;}
.feat div:nth-child(2)::after {animation-delay: .5s;} .feat div:nth-child(3)::after {animation-delay: 1s;}
.feat div:nth-child(4)::after {animation-delay: 1.5s;}
@keyframes shine {0% {left: -70%;} 55%, 100% {left: 140%;}}
.feat div:hover {transform: translateY(-3px) scale(1.03); box-shadow: 0 0 30px rgba(34,211,238,.55);}

/* ---------- cards ---------- */
.kpi {position: relative; overflow: hidden; border-radius: 16px; padding: 20px 22px; border: 1px solid;
    background: linear-gradient(160deg, rgba(18,34,70,.82), rgba(9,18,42,.82)); backdrop-filter: blur(10px);
    box-shadow: 0 8px 26px rgba(0,0,0,.3); transition: all .25s ease;}
.kpi:hover {transform: translateY(-4px); box-shadow: 0 12px 34px rgba(34,211,238,.18);}
.kpi::before {content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,.7), transparent);}
.kpi .l {font-size: 12.5px; color: #a9bde0; letter-spacing: .1em; font-weight: 700;}
.kpi .v {font-size: 30px; line-height: 1.25; font-weight: 800; margin: 6px 0 4px 0; text-shadow: 0 0 18px currentColor;}
.kpi .s {font-size: 13px; color: #8fa6cf;}
.panel {background: rgba(12,24,52,.78); border: 1px solid rgba(96,165,250,.25); border-radius: 16px;
    padding: 14px 18px 8px 18px; margin-bottom: 14px; backdrop-filter: blur(10px);}
.panel h4 {margin: 0 0 4px 0; font-size: 16px; color: #f4f8ff;}
.insight {background: linear-gradient(160deg, rgba(18,34,70,.82), rgba(9,18,42,.82)); border: 1px solid rgba(96,165,250,.25);
    border-left: 4px solid; border-radius: 14px; padding: 14px 16px; backdrop-filter: blur(10px);}
.insight .t {font-size: 12px; color: #a9bde0; letter-spacing: .09em; font-weight: 700;}
.insight .m {font-size: 20px; font-weight: 800; margin-top: 4px; color: #f4f8ff;}
.insight .d {font-size: 13px; color: #8fa6cf; margin-top: 3px;}
.verdict {border-radius: 16px; padding: 22px 24px; border: 1px solid; margin-bottom: 14px; backdrop-filter: blur(10px);}
.verdict .t {font-size: 12.5px; letter-spacing: .1em; color: #bcd0f0; font-weight: 700;}
.verdict .m {font-size: 30px; font-weight: 800; margin: 6px 0;} .verdict .d {font-size: 14px; color: #bcd0f0;}

/* every chart sits on a glass card (skipped when the page already wraps it in a bordered box) */
[data-testid="stColumn"]:has([data-testid="stPlotlyChart"]):not(:has([data-testid="stVerticalBlockBorderWrapper"])) {
    background: rgba(10,20,46,.68); border: 1px solid rgba(96,165,250,.25); border-radius: 18px;
    padding: 16px 18px 8px 18px; backdrop-filter: blur(12px); box-shadow: 0 8px 28px rgba(0,0,0,.28);}
[data-testid="stVerticalBlockBorderWrapper"] {background: rgba(10,20,46,.68); border-radius: 18px !important;
    border: 1px solid rgba(96,165,250,.25) !important; backdrop-filter: blur(12px); box-shadow: 0 8px 28px rgba(0,0,0,.28);}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] {background: none; border: none !important;
    box-shadow: none; backdrop-filter: none; border-radius: 0 !important;}

/* ---------- widgets ---------- */
[data-testid="stForm"] {border: 1px solid rgba(103,232,249,.4); border-radius: 20px; padding: 26px;
    background: linear-gradient(160deg, rgba(10,20,46,.97), rgba(7,13,32,.97));
    backdrop-filter: blur(18px); box-shadow: 0 14px 44px rgba(0,0,0,.55), 0 0 26px rgba(34,211,238,.10);}
[data-testid="stForm"] [data-testid="stWidgetLabel"] p {color: #e6f0ff !important; font-size: 14.5px !important; font-weight: 600;}
[data-testid="stForm"] [data-testid="stCaptionContainer"] p {color: #b4c8ea !important;}
[data-baseweb="select"] > div, [data-baseweb="input"] > div {background: rgba(22,40,80,.95) !important;
    border: 1px solid rgba(96,165,250,.4) !important;}
[data-baseweb="select"] > div:hover, [data-baseweb="input"] > div:hover {border-color: #22d3ee !important;}    backdrop-filter: blur(12px); padding: 22px;}
.stButton > button, [data-testid="stForm"] button {background: linear-gradient(90deg, #0891b2, #7c3aed); color: #fff;
    border: 0; font-weight: 700; border-radius: 12px; padding: 10px 18px; font-size: 16px; transition: all .2s ease;}
.stButton > button:hover, [data-testid="stForm"] button:hover {box-shadow: 0 0 24px rgba(34,211,238,.55); transform: translateY(-2px); color: #fff;}
[data-testid="stExpander"] {background: rgba(10,20,46,.72); border: 1px solid rgba(96,165,250,.28) !important; border-radius: 14px;}
[data-testid="stAlert"] {background: rgba(34,211,238,.08); border: 1px solid rgba(34,211,238,.35); border-radius: 14px;}
[data-testid="stAlert"] p {color: #d6e9ff !important;}
[data-testid="stElementContainer"]:has([data-testid="stAlert"]) {margin-top: 22px;}
[data-testid="stAlert"] {margin-top: 22px;}
[data-testid="stDataFrame"] {border: 1px solid rgba(96,165,250,.25); border-radius: 12px; overflow: hidden;}
[data-baseweb="select"] > div, [data-baseweb="input"] > div {border-radius: 10px !important;}
</style>
"""

LOGO = ('<svg width="54" height="54" viewBox="0 0 54 54"><defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#22d3ee"/><stop offset="1" stop-color="#8b5cf6"/></linearGradient></defs>'
        '<rect width="54" height="54" rx="15" fill="url(#lg)"/>'
        '<rect x="9" y="28" width="10" height="17" rx="2" fill="#fff" opacity=".8"/>'
        '<rect x="21" y="9" width="12" height="36" rx="2" fill="#fff"/>'
        '<path d="M35 31 L41.5 24 L48 31 V45 H35 Z" fill="#fff" opacity=".85"/>'
        '<g fill="#0e7490"><rect x="24" y="14" width="2.6" height="3"/><rect x="28" y="14" width="2.6" height="3"/>'
        '<rect x="24" y="21" width="2.6" height="3"/><rect x="28" y="21" width="2.6" height="3"/>'
        '<rect x="24" y="28" width="2.6" height="3"/><rect x="28" y="28" width="2.6" height="3"/>'
        '<rect x="12" y="33" width="2.6" height="3"/><rect x="12" y="39" width="2.6" height="3"/>'
        '<rect x="40" y="36" width="3" height="9"/></g></svg>')


def brand():
    # Sidebar logo + product name (custom SVG, no emoji)
    st.sidebar.markdown(f'<div class="brand">{LOGO}<div><div class="name">EstateIQ</div>'
                        '<div class="tag">PROPERTY INTELLIGENCE</div></div></div>', unsafe_allow_html=True)

def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(f"<style>{_image_css()}</style>", unsafe_allow_html=True)


def inject_images():
    pass  # kept for compatibility: images are applied inside inject_css()


def kpi(label, value, sub, color):
    return (f'<div class="kpi" style="border-color:{color}77"><div class="l">{label}</div>'
            f'<div class="v" style="color:{color}">{value}</div><div class="s">{sub}</div></div>')


def insight(title, main, detail, color):
    return (f'<div class="insight" style="border-left-color:{color}"><div class="t">{title}</div>'
            f'<div class="m">{main}</div><div class="d">{detail}</div></div>')


def panel_title(text):
    st.markdown(f'<div class="panel"><h4>{text}</h4></div>', unsafe_allow_html=True)


def verdict(title, main, detail, color):
    return (f'<div class="verdict" style="border-color:{color}99; background:{color}22">'
            f'<div class="t">{title}</div><div class="m" style="color:{color}">{main}</div>'
            f'<div class="d">{detail}</div></div>')


def style_fig(fig, height=300):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="#c4d6f7", size=13, family="Plus Jakarta Sans, sans-serif"),
                      legend=dict(font=dict(color="#c4d6f7", size=12)),
                      hoverlabel=dict(bgcolor="#0c1f45", font_color="#ffffff", bordercolor="#22d3ee"),
                      bargap=0.3)
    fig.update_layout(xaxis_title=None, yaxis_title=None)
    fig.update_xaxes(gridcolor="rgba(148,163,184,.14)", zeroline=False, tickfont=dict(size=12))
    fig.update_yaxes(gridcolor="rgba(148,163,184,.14)", zeroline=False, tickfont=dict(size=12))
    fig.update_traces(marker_line_width=0, textangle=0, selector=dict(type="bar"))
    fig.update_traces(marker_line_color="#0a1430", marker_line_width=2, selector=dict(type="pie"))
    try:
        fig.update_layout(barcornerradius=8)      # rounded bars (newer Plotly only)
    except (ValueError, TypeError):
        pass
    return fig
LOGO = ('<svg width="54" height="54" viewBox="0 0 54 54"><defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#22d3ee"/><stop offset="1" stop-color="#8b5cf6"/></linearGradient></defs>'
        '<rect width="54" height="54" rx="15" fill="url(#lg)"/>'
        '<rect x="9" y="28" width="10" height="17" rx="2" fill="#fff" opacity=".8"/>'
        '<rect x="21" y="9" width="12" height="36" rx="2" fill="#fff"/>'
        '<path d="M35 31 L41.5 24 L48 31 V45 H35 Z" fill="#fff" opacity=".85"/>'
        '<g fill="#0e7490"><rect x="24" y="14" width="2.6" height="3"/><rect x="28" y="14" width="2.6" height="3"/>'
        '<rect x="24" y="21" width="2.6" height="3"/><rect x="28" y="21" width="2.6" height="3"/>'
        '<rect x="24" y="28" width="2.6" height="3"/><rect x="28" y="28" width="2.6" height="3"/>'
        '<rect x="12" y="33" width="2.6" height="3"/><rect x="12" y="39" width="2.6" height="3"/>'
        '<rect x="40" y="36" width="3" height="9"/></g></svg>')


def brand():
    # Sidebar logo + product name (custom SVG, no emoji)
    st.sidebar.markdown(f'<div class="brand">{LOGO}<div><div class="name">EstateIQ</div>'
                        '<div class="tag">PROPERTY INTELLIGENCE</div></div></div>', unsafe_allow_html=True)