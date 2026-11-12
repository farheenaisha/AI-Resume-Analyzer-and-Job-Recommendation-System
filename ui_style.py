"""Global stylesheet for CareerLens AI.

Design rules:
- Light theme is forced in .streamlit/config.toml, and every text colour is also set explicitly here,
  so text stays readable whatever the browser / OS theme is.
- All text/background pairs have a contrast ratio of at least 4.5:1 (WCAG AA).
"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

:root{
  --brand:#5b47c9; --brand-dark:#3d2f86; --ink:#1f2240; --muted:#5f6380;
  --line:#e4e0f7; --soft:#f1eeff; --bg:#f6f5fd;
  --ok:#0b6b45; --ok-bg:#e3f6ec; --warn:#7a4f00; --warn-bg:#fff3d6; --bad:#a3262a; --bad-bg:#fde8e8;
}
html, body, [class*="css"], .stApp {font-family:'DM Sans',sans-serif; color:var(--ink); color-scheme:light;}
.stApp {background:linear-gradient(135deg,#f6f5fd 0%,#f8fbff 60%,#f3f7ff 100%);}
h1,h2,h3,h4 {font-family:Manrope,sans-serif; color:var(--ink); letter-spacing:-.01em;}
h3 {font-size:1.25rem; margin-top:.4rem;}
p, li, label, span {color:inherit;}
.block-container {padding-top:2.2rem; padding-bottom:3rem; max-width:1180px;}
header[data-testid="stHeader"] {background:transparent;}
#MainMenu, footer {visibility:hidden;}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {background:linear-gradient(185deg,#1c1644 0%,#2f2362 100%);}
[data-testid="stSidebar"] * {color:#f4f2ff !important;}
[data-testid="stSidebar"] .block-container {padding-top:1.2rem;}
.brand {font-family:Manrope,sans-serif; font-weight:800; font-size:1.35rem; display:flex; gap:10px; align-items:center;}
.brand small {display:block; font-family:'DM Sans'; font-weight:500; font-size:.78rem; color:#cfc8f5 !important; margin-top:2px;}
.usercard {display:flex; gap:12px; align-items:center; background:#ffffff14; border:1px solid #ffffff26; border-radius:14px; padding:12px 14px; margin:14px 0 8px;}
.avatar {width:40px; height:40px; border-radius:50%; background:#fff; display:flex; align-items:center; justify-content:center; font-weight:800; flex:none;}
.avatar, .avatar * {color:#3d2f86 !important;}
.usercard .nm {font-weight:700; line-height:1.2; word-break:break-word;}
.usercard .gl {font-size:.78rem; color:#cfc8f5 !important; line-height:1.3;}
.navlabel {font-size:.72rem; font-weight:700; letter-spacing:1.5px; color:#b9b0ee !important; margin:18px 0 6px 4px;}
[data-testid="stSidebar"] button {border-radius:12px; text-align:left; justify-content:flex-start; font-weight:600; border:1px solid transparent; min-height:44px;}
[data-testid="stSidebar"] button[kind="secondary"], [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {background:transparent; border-color:transparent;}
[data-testid="stSidebar"] button[kind="secondary"]:hover, [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {background:#ffffff1f;}
[data-testid="stSidebar"] button[kind="primary"], [data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {background:#ffffff; border-color:#fff;}
[data-testid="stSidebar"] button[kind="primary"] *, [data-testid="stSidebar"] [data-testid="stBaseButton-primary"] * {color:#3d2f86 !important; font-weight:800;}
.logout-wrap button {border:1px solid #ffffff55 !important;}

/* ---------- Hero ---------- */
.hero {padding:30px 34px; border-radius:24px; background:linear-gradient(115deg,#29205d,#5943a5 62%,#7565c9); margin-bottom:24px; box-shadow:0 14px 38px #3d2d8030;}
.hero h1 {font-size:2.1rem; font-weight:800; margin:0 0 8px 0; color:#fff !important;}
.hero p {color:#ece8ff !important; font-size:1.02rem; margin:0; max-width:720px;}
.hero .chips {margin-top:16px;}
.hero .chip {display:inline-block; background:#ffffff24; color:#fff !important; border:1px solid #ffffff3d; padding:5px 12px; border-radius:20px; font-size:.8rem; font-weight:600; margin:0 8px 6px 0;}

/* ---------- Cards ---------- */
[class*="st-key-card"] {background:#fff; border:1px solid var(--line); border-radius:18px; padding:6px 10px; box-shadow:0 8px 24px #30265d0d; margin-bottom:6px;}
.kpi {background:#fff; border:1px solid var(--line); border-radius:16px; padding:18px 20px; height:100%; box-shadow:0 6px 18px #30265d08;}
.kpi .top {display:flex; justify-content:space-between; align-items:center;}
.kpi .lbl {font-size:.74rem; color:var(--muted); font-weight:700; text-transform:uppercase; letter-spacing:.8px;}
.kpi .ic {font-size:1.2rem;}
.kpi .num {font-family:Manrope,sans-serif; font-size:1.9rem; font-weight:800; color:var(--brand-dark); margin:6px 0 2px;}
.kpi .note {font-size:.82rem; color:var(--muted);}
.step {background:#fff; border:1px solid var(--line); border-radius:18px; padding:20px 22px; height:100%; box-shadow:0 6px 18px #30265d08;}
.step .n {display:inline-flex; width:34px; height:34px; border-radius:10px; background:var(--soft); color:var(--brand-dark); font-weight:800; align-items:center; justify-content:center; margin-bottom:10px;}
.step h4 {margin:0 0 6px; font-size:1.05rem;}
.step p {color:var(--muted); font-size:.92rem; margin:0; line-height:1.5;}
.muted {color:var(--muted); font-size:.9rem;}
.section-title {font-family:Manrope,sans-serif; font-size:1.25rem; font-weight:800; margin:26px 0 12px; color:var(--ink);}

/* ---------- Tags ---------- */
.tag {display:inline-block; background:var(--soft); color:var(--brand-dark); padding:5px 11px; border-radius:20px; margin:3px 4px 3px 0; font-size:.8rem; font-weight:700; border:1px solid #ddd6fb;}
.tag.ok {background:var(--ok-bg); color:var(--ok); border-color:#b6e4cc;}
.tag.gap {background:var(--warn-bg); color:var(--warn); border-color:#f1d9a0;}
.tag.bad {background:var(--bad-bg); color:var(--bad); border-color:#f4c1c3;}

/* ---------- Job card ---------- */
.job-title {font-family:Manrope,sans-serif; font-size:1.2rem; font-weight:800; margin:2px 0 2px; color:var(--ink);}
.job-meta {color:var(--muted); font-size:.88rem; margin-bottom:10px;}
.job-desc {color:#33375a; font-size:.95rem; line-height:1.55; margin-bottom:10px;}
.match {text-align:center; padding-top:4px;}
.match .pct {font-family:Manrope,sans-serif; font-size:2rem; font-weight:800; line-height:1;}
.match .cap {font-size:.72rem; font-weight:700; color:var(--muted); letter-spacing:.8px; text-transform:uppercase; margin:4px 0 8px;}
.bar {height:8px; background:#ebe8fa; border-radius:8px; overflow:hidden;}
.bar > div {height:100%; border-radius:8px;}
.legend {font-size:.82rem; color:var(--muted); margin:2px 0 10px;}

/* ---------- Tips / checklist ---------- */
.tip {display:flex; gap:12px; background:#fff; border:1px solid var(--line); border-left:4px solid var(--brand); border-radius:12px; padding:12px 16px; margin-bottom:10px; color:#2b2f52; line-height:1.5;}
.tip .ico {flex:none;}

/* ---------- Auth ---------- */
.auth-brand {background:linear-gradient(150deg,#251c5c,#5943a5 70%,#7a69cf); border-radius:26px; padding:44px 38px; box-shadow:0 18px 44px #3d2d8038;}
.auth-brand, .auth-brand * {color:#fff !important;}
.auth-brand .eyebrow {font-size:.8rem; font-weight:800; letter-spacing:2px; color:#d9d2ff !important;}
.auth-brand h1 {font-size:2.5rem; line-height:1.12; margin:12px 0 14px; color:#fff !important;}
.auth-brand p {font-size:1.05rem; color:#ece8ff !important; line-height:1.55;}
.auth-brand ul {list-style:none; padding:0; margin:26px 0 0;}
.auth-brand li {display:flex; gap:12px; align-items:flex-start; margin-bottom:14px; font-size:.98rem; line-height:1.4;}
.auth-brand li b {display:block; font-size:1rem;}
.auth-brand li span.i {flex:none; width:34px; height:34px; background:#ffffff26; border-radius:10px; display:flex; align-items:center; justify-content:center;}

/* ---------- Streamlit widgets: guaranteed readable ---------- */
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {color:var(--ink) !important; font-weight:600; font-size:.92rem;}
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"], [data-baseweb="select"] > div {background:#fff !important; border-color:#d3cdf3 !important; border-radius:10px !important;}
input, textarea {color:var(--ink) !important; -webkit-text-fill-color:var(--ink) !important; background:#fff !important;}
input::placeholder, textarea::placeholder {color:#767a94 !important; -webkit-text-fill-color:#767a94 !important;}
input:disabled {-webkit-text-fill-color:#4b4f6b !important; opacity:1 !important; background:#f3f1fb !important;}
[data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within, [data-baseweb="select"] > div:focus-within {border-color:var(--brand) !important; box-shadow:0 0 0 3px #5b47c933 !important;}
[data-baseweb="select"] * {color:var(--ink) !important;}
[data-baseweb="popover"] * {color:var(--ink);}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {color:var(--muted) !important;}
[data-testid="stMarkdownContainer"] p {color:inherit;}
[data-testid="stForm"] {border:0 !important; padding:0 !important; background:transparent !important;}
[data-testid="stCheckbox"] p {color:var(--ink) !important;}

/* Buttons */
[data-testid^="stBaseButton"] p {color:inherit !important; font-weight:700;}
.stMain button[kind="primary"], .stMain [data-testid^="stBaseButton-primary"] {background:var(--brand); color:#fff; border:0; border-radius:12px; font-weight:700; min-height:44px;}
.stMain button[kind="primary"]:hover, .stMain [data-testid^="stBaseButton-primary"]:hover {background:var(--brand-dark); color:#fff;}
.stMain button[kind="secondary"], .stMain [data-testid^="stBaseButton-secondary"] {background:#fff; color:var(--brand-dark); border:1px solid #cfc7f3; border-radius:12px; font-weight:700; min-height:42px;}
.stMain button[kind="secondary"]:hover, .stMain [data-testid^="stBaseButton-secondary"]:hover {border-color:var(--brand); background:var(--soft); color:var(--brand-dark);}
.stMain button:disabled {opacity:.75;}
.stMain button:disabled p {color:var(--ok) !important;}

/* Tabs */
button[role="tab"] p {color:var(--muted) !important; font-weight:700; font-size:.98rem;}
button[role="tab"][aria-selected="true"] p {color:var(--brand-dark) !important;}
[data-baseweb="tab-highlight"] {background:var(--brand) !important;}

/* File uploader */
[data-testid="stFileUploaderDropzone"] {background:#faf9ff; border:2px dashed #b9b0ec; border-radius:14px;}
[data-testid="stFileUploaderDropzone"] * {color:#3b3566 !important;}
[data-testid="stFileUploaderDropzone"] button {background:#fff !important; border:1px solid #cfc7f3 !important;}

/* Alerts, tables, expanders */
[data-testid="stAlert"] {border-radius:12px;}
[data-testid="stAlert"] p {color:var(--ink) !important;}
[data-testid="stExpander"] {background:#fff; border:1px solid var(--line) !important; border-radius:14px;}
[data-testid="stExpander"] summary p {color:var(--ink) !important; font-weight:700;}
[data-testid="stDataFrame"] {border:1px solid var(--line); border-radius:12px; overflow:hidden;}
[data-testid="stSlider"] p {color:var(--ink);}

@media (max-width:760px){
  .hero {padding:22px 20px;} .hero h1 {font-size:1.6rem;}
  .auth-brand {padding:28px 22px;} .auth-brand h1 {font-size:1.9rem;}
  .block-container {padding-left:1rem; padding-right:1rem;}
}
</style>
"""
