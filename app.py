import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from google import genai
from dotenv import load_dotenv
import os
import json
import re
import csv
from datetime import datetime
from pathlib import Path

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

st.set_page_config(
    page_title="Drishti Analytics",
    page_icon="👁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── PALETTE ──────────────────────────────────────────────────────
BG      = "#F5F7FA"
CARD    = "#FFFFFF"
SB      = "#0F1C2E"
ACC     = "#1B6CA8"
ACC2    = "#2E8BC0"
ACC3    = "#0D4F8B"
TXT     = "#0D1B2A"
MID     = "#4A5568"
LITE    = "#8896A5"
BDR     = "#E2E8F0"
DANGER  = "#C0392B"
SUCCESS = "#27AE60"
WARN    = "#F39C12"
CSEQ    = ["#1B6CA8","#2E8BC0","#48A9C5","#5BC0D8","#3A7BD5","#0D4F8B"]

# ── GLOBAL CSS ────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
html,body,[class*="css"]{{font-family:'Inter',sans-serif!important;}}

/* ── SIDEBAR ── */
[data-testid="stSidebar"]{{background:{SB}!important;}}
[data-testid="stSidebar"]>div:first-child{{background:{SB}!important;padding:0!important;}}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div{{color:#8896A5!important;font-family:'Inter',sans-serif!important;}}
[data-testid="stSidebar"] .stRadio>div{{gap:0!important;}}
[data-testid="stSidebar"] .stRadio label{{
  display:flex!important;align-items:center!important;
  padding:10px 20px!important;border-radius:0!important;
  font-size:0.85rem!important;font-weight:500!important;
  color:#8896A5!important;cursor:pointer;
  border-left:3px solid transparent!important;transition:all 0.15s;
}}
[data-testid="stSidebar"] .stRadio label:hover{{
  background:rgba(255,255,255,0.05)!important;
  color:#E2E8F0!important;border-left-color:{ACC}!important;
}}

/* ── MAIN ── */
.main .block-container{{padding:2rem 2.5rem 3rem;max-width:1400px;background:{BG};}}
html,body,[class*="css"]{{background:{BG};color:{TXT};}}

/* ── PAGE HEADER ── */
.ph{{margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid {BDR};}}
.pt{{font-size:1.55rem;font-weight:800;letter-spacing:-0.03em;color:{TXT};margin:0 0 4px;}}
.ps{{font-size:0.8rem;color:{LITE};margin:0;}}

/* ── METRIC CARDS ── */
div[data-testid="stMetric"]{{
  background:{CARD}!important;border:1px solid {BDR}!important;
  border-top:3px solid {ACC}!important;border-radius:10px!important;
  padding:18px 20px!important;box-shadow:0 1px 4px rgba(0,0,0,0.04);
}}
div[data-testid="stMetricLabel"]>div{{font-size:0.68rem!important;font-weight:600!important;color:{LITE}!important;text-transform:uppercase!important;letter-spacing:0.08em!important;}}
div[data-testid="stMetricValue"]>div{{font-size:1.5rem!important;font-weight:800!important;color:{TXT}!important;letter-spacing:-0.02em!important;}}

/* ── CHART CARDS ── */
.cc{{background:{CARD};border:1px solid {BDR};border-radius:10px;padding:20px 22px 6px;margin-bottom:16px;box-shadow:0 1px 4px rgba(0,0,0,0.04);}}
.ct{{font-size:0.68rem;font-weight:700;color:{LITE};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:14px;padding-bottom:12px;border-bottom:1px solid {BDR};}}

/* ── AI BOX ── */
.ai{{background:{CARD};border:1px solid {BDR};border-left:4px solid {ACC};border-radius:10px;padding:22px 26px;margin-top:8px;font-size:0.875rem;line-height:1.8;color:{MID};white-space:pre-wrap;box-shadow:0 1px 4px rgba(0,0,0,0.04);}}

/* ── ANOMALY / INSIGHT / CROSS CARDS ── */
.anomaly-card{{background:#FFF5F5;border:1px solid #FED7D7;border-left:4px solid {DANGER};border-radius:10px;padding:16px 20px;margin:6px 0;}}
.anomaly-title{{font-size:0.78rem;font-weight:700;color:{DANGER};margin-bottom:4px;}}
.anomaly-body{{font-size:0.82rem;color:{MID};line-height:1.6;}}
.cross-card{{background:#EBF8FF;border:1px solid #BEE3F8;border-left:4px solid {ACC};border-radius:10px;padding:16px 20px;margin:6px 0;}}
.cross-title{{font-size:0.78rem;font-weight:700;color:{ACC};margin-bottom:4px;}}
.cross-body{{font-size:0.82rem;color:{MID};line-height:1.6;}}

/* ── MISC ── */
.sl{{font-size:0.68rem;font-weight:700;color:{LITE};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;}}
.dv{{border:none;border-top:1px solid {BDR};margin:1.5rem 0 1.2rem;}}
.forecast-badge{{display:inline-block;background:rgba(27,108,168,0.1);color:{ACC};border-radius:4px;padding:2px 8px;font-size:0.65rem;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;margin-left:8px;}}
.qa-answer{{background:#F7FAFC;border-radius:8px;padding:16px 18px;margin-top:12px;font-size:0.875rem;line-height:1.8;color:{MID};}}

/* ── BUTTONS ── */
.stButton>button{{
  background:{ACC}!important;color:#fff!important;border:none!important;
  border-radius:6px!important;padding:9px 24px!important;
  font-size:0.8rem!important;font-weight:600!important;
  font-family:'Inter',sans-serif!important;letter-spacing:0.03em!important;
}}
.stButton>button:hover{{background:{ACC2}!important;}}

/* ── INPUTS ── */
.stTextInput>div>div>input,.stTextArea>div>div>textarea{{
  border-radius:8px!important;border:1px solid {BDR}!important;
  background:{CARD}!important;
}}
.stMultiSelect label,.stSelectbox label,.stFileUploader label,
.stTextInput label,.stTextArea label{{
  font-size:0.68rem!important;font-weight:700!important;color:{LITE}!important;
  text-transform:uppercase!important;letter-spacing:0.08em!important;
}}

/* ── HERO (landing) ── */
.hero-wrap{{
  min-height:100vh; display:flex; flex-direction:column;
  align-items:center; justify-content:center;
  background:linear-gradient(135deg,#060D1A 0%,#0E1E38 50%,#060D1A 100%);
  text-align:center; padding:60px 40px; position:relative; overflow:hidden;
}}
.hero-glow{{
  position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  width:700px;height:400px;border-radius:50%;
  background:radial-gradient(ellipse,rgba(27,108,168,0.18) 0%,transparent 70%);
  pointer-events:none;
}}
.hero-title{{
  font-size:clamp(4rem,12vw,9rem);font-weight:900;
  letter-spacing:-0.06em;line-height:1;
  background:linear-gradient(180deg,#fff 0%,#BDD5EA 50%,rgba(91,163,208,0.5) 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  margin-bottom:16px;
}}
.hero-sub{{
  font-size:0.82rem;font-weight:500;letter-spacing:0.26em;text-transform:uppercase;
  color:rgba(255,255,255,0.28);margin-bottom:20px;
}}
.hero-tagline{{
  font-size:clamp(0.9rem,1.5vw,1.05rem);color:rgba(255,255,255,0.4);
  max-width:520px;line-height:1.8;margin:0 auto 44px;
}}
.hero-ring{{
  position:absolute;border-radius:50%;
  border:1px solid rgba(91,163,208,0.07);
  left:50%;top:50%;transform:translate(-50%,-50%);
  animation:ringPulse 4s ease-out infinite;
}}
@keyframes ringPulse{{
  0%{{transform:translate(-50%,-50%) scale(0.7);opacity:0.8;}}
  100%{{transform:translate(-50%,-50%) scale(2.4);opacity:0;}}
}}

/* ── AUTH FORM ── */
.auth-wrap{{
  max-width:440px;margin:0 auto;padding:48px 44px;
  background:{CARD};border:1px solid {BDR};border-radius:16px;
  box-shadow:0 4px 24px rgba(0,0,0,0.06);
}}
.auth-logo{{font-size:1.4rem;font-weight:900;color:{TXT};letter-spacing:-0.03em;margin-bottom:6px;text-align:center;}}
.auth-logo span{{color:{ACC};}}
.auth-title{{font-size:1.25rem;font-weight:800;color:{TXT};letter-spacing:-0.02em;margin-bottom:6px;text-align:center;}}
.auth-sub{{font-size:0.8rem;color:{LITE};text-align:center;margin-bottom:28px;}}
.auth-divider{{display:flex;align-items:center;gap:12px;margin:20px 0;}}
.auth-divider-line{{flex:1;height:1px;background:{BDR};}}
.auth-divider-txt{{font-size:0.7rem;color:{LITE};font-weight:600;letter-spacing:0.08em;text-transform:uppercase;}}
.auth-switch{{font-size:0.8rem;color:{LITE};text-align:center;margin-top:20px;}}
.auth-switch a{{color:{ACC};font-weight:600;cursor:pointer;text-decoration:none;}}
.auth-error{{background:#FFF5F5;border:1px solid #FED7D7;border-left:4px solid {DANGER};border-radius:8px;padding:10px 14px;font-size:0.8rem;color:{DANGER};margin-bottom:16px;}}
.auth-success{{background:#F0FFF4;border:1px solid #C6F6D5;border-left:4px solid {SUCCESS};border-radius:8px;padding:10px 14px;font-size:0.8rem;color:{SUCCESS};margin-bottom:16px;}}

/* ── CONTACT FORM ── */
.contact-wrap{{
  max-width:600px;margin:0 auto;
  background:{CARD};border:1px solid {BDR};border-radius:14px;
  padding:36px 40px;box-shadow:0 1px 4px rgba(0,0,0,0.04);
}}
.contact-label{{font-size:0.68rem;font-weight:700;color:{LITE};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;}}

#MainMenu,footer,header{{visibility:hidden;}}
.stDeployButton{{display:none;}}
</style>
""", unsafe_allow_html=True)

# ── HELPERS ──────────────────────────────────────────────────────
BLUE_SCALE  = [[0,"#BDD5EA"],[1,ACC]]
BLUE_SCALE2 = [[0,"#BDD5EA"],[1,ACC2]]
RED_SCALE   = [[0,"#F5C6CB"],[1,DANGER]]

def fig_clean(fig, h=300):
    fig.update_layout(
        height=h, margin=dict(t=8,b=8,l=4,r=4),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter",size=11,color=MID),
        legend=dict(bgcolor="rgba(0,0,0,0)",borderwidth=0,font=dict(size=10)),
        xaxis=dict(gridcolor=BDR,linecolor=BDR,tickfont=dict(size=10),title_font=dict(size=10,color=LITE)),
        yaxis=dict(gridcolor=BDR,linecolor=BDR,tickfont=dict(size=10),title_font=dict(size=10,color=LITE)),
        coloraxis_showscale=False
    )
    fig.update_traces(marker_line_width=0)
    return fig

def gemini(prompt, max_tokens=1500):
    try:
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# ── DATA ─────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    s = pd.read_csv('data/sales_data.csv',      parse_dates=['date'])
    m = pd.read_csv('data/marketing_data.csv',  parse_dates=['date'])
    f = pd.read_csv('data/finance_data.csv',    parse_dates=['date'])
    h = pd.read_csv('data/healthcare_data.csv', parse_dates=['admission_date'])
    return s, m, f, h

# ── USER STORE (simple CSV) ───────────────────────────────────────
USERS_FILE = "users.csv"
CONTACTS_FILE = "contacts.csv"

def load_users():
    if not Path(USERS_FILE).exists():
        return {}
    users = {}
    with open(USERS_FILE, newline='') as f:
        for row in csv.DictReader(f):
            users[row['email']] = row
    return users

def save_user(name, email, company, password):
    exists = Path(USERS_FILE).exists()
    with open(USERS_FILE, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['name','email','company','password','joined'])
        if not exists:
            w.writeheader()
        w.writerow({'name':name,'email':email,'company':company,
                    'password':password,'joined':datetime.now().strftime('%Y-%m-%d %H:%M')})

def save_contact(name, email, company, message):
    exists = Path(CONTACTS_FILE).exists()
    with open(CONTACTS_FILE, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['name','email','company','message','timestamp'])
        if not exists:
            w.writeheader()
        w.writerow({'name':name,'email':email,'company':company,
                    'message':message,'timestamp':datetime.now().strftime('%Y-%m-%d %H:%M')})

# ── AI FEATURES ──────────────────────────────────────────────────
def detect_anomalies(df, value_col, group_col=None, domain=""):
    prompt = f"""You are a data anomaly detection system. Analyze this data and find unusual patterns.
Domain: {domain}
Data statistics: {df[value_col].describe().to_string()}
{"Group breakdown:\n" + df.groupby(group_col)[value_col].mean().to_string() if group_col and group_col in df.columns else ""}
Identify exactly 3 anomalies. Format:
ANOMALY: [title]
DETAIL: [specific finding with numbers]
SEVERITY: [High/Medium/Low]
---
No other text."""
    return gemini(prompt)

def parse_anomalies(text):
    anomalies = []
    for block in text.strip().split('---'):
        block = block.strip()
        if not block: continue
        a = {}
        for line in block.split('\n'):
            if line.startswith('ANOMALY:'): a['title'] = line.replace('ANOMALY:','').strip()
            elif line.startswith('DETAIL:'): a['detail'] = line.replace('DETAIL:','').strip()
            elif line.startswith('SEVERITY:'): a['severity'] = line.replace('SEVERITY:','').strip()
        if 'title' in a: anomalies.append(a)
    return anomalies

def generate_forecast(df, date_col, value_col, periods=3):
    df_copy = df.copy()
    df_copy['month'] = pd.to_datetime(df_copy[date_col]).dt.to_period('M')
    monthly = df_copy.groupby('month')[value_col].sum().reset_index()
    monthly['month_num'] = range(len(monthly))
    if len(monthly) < 3: return None, None, None, None
    x, y = monthly['month_num'].values, monthly[value_col].values
    slope, intercept = np.polyfit(x, y, 1)
    last_month = monthly['month'].iloc[-1]
    future_months, future_vals = [], []
    for i in range(1, periods+1):
        future_months.append(str(last_month+i))
        future_vals.append(max(0, slope*(len(monthly)+i-1)+intercept))
    return future_months, future_vals, slope, monthly

def parse_nl_filter(query, df, domain):
    cols, sample = list(df.columns), df.head(3).to_dict('records')
    prompt = f"""Convert this natural language query into a filter dict.
Available columns: {cols}
Sample data: {sample}
Domain: {domain}
Query: "{query}"
Respond ONLY with a valid Python dict. Examples:
{{"column":"region","value":"West","operator":"equals"}}
{{"column":"revenue","value":50000,"operator":"greater_than"}}
If cannot parse: {{"error":"cannot parse"}}"""
    result = gemini(prompt, max_tokens=200)
    try:
        result = result.strip()
        if result.startswith('```'): result = re.sub(r'```[a-z]*\n?','',result).strip()
        return json.loads(result)
    except: return {"error":"cannot parse"}

def apply_nl_filter(df, fd):
    if "error" in fd: return df, False
    try:
        col, op = fd.get("column"), fd.get("operator","equals")
        if col not in df.columns: return df, False
        if op == "equals":
            return df[df[col].astype(str).str.lower()==str(fd.get("value","")).lower()], True
        elif op == "between" and "start" in fd:
            return df[(df[col]>=fd["start"])&(df[col]<=fd["end"])], True
        elif op == "greater_than":
            return df[df[col]>float(fd.get("value",0))], True
        elif op == "less_than":
            return df[df[col]<float(fd.get("value",0))], True
        elif op == "contains":
            return df[df[col].astype(str).str.contains(str(fd.get("value","")),case=False)], True
        return df, False
    except: return df, False

def cross_domain_insights(s, m, f, h):
    prompt = f"""You are Drishti's cross-domain AI analyst. Find hidden correlations.
Sales total: ${s['revenue'].sum():,.0f}
Marketing avg ROI: {m['roi'].mean():.2f}x
Finance over-budget rate: {f['over_budget'].mean()*100:.1f}%
Healthcare readmission rate: {h['readmitted'].mean()*100:.1f}%
Healthcare avg satisfaction: {h['satisfaction_score'].mean():.1f}/10
Find 3 cross-domain correlations. Format:
INSIGHT: [title]
FINDING: [specific data-backed finding]
ACTION: [recommended action]
---"""
    return gemini(prompt, max_tokens=600)

def parse_cross_insights(text):
    insights = []
    for block in text.strip().split('---'):
        block = block.strip()
        if not block: continue
        ins = {}
        for line in block.split('\n'):
            if line.startswith('INSIGHT:'): ins['title'] = line.replace('INSIGHT:','').strip()
            elif line.startswith('FINDING:'): ins['finding'] = line.replace('FINDING:','').strip()
            elif line.startswith('ACTION:'): ins['action'] = line.replace('ACTION:','').strip()
        if 'title' in ins: insights.append(ins)
    return insights

def ai_section(key, summary, domain):
    st.markdown("<hr class='dv'>", unsafe_allow_html=True)
    st.markdown("<div class='sl'>AI-Generated Analysis</div>", unsafe_allow_html=True)
    if st.button("Generate Insights", key=key):
        with st.spinner("Analyzing..."):
            result = gemini(f"""You are a senior business analyst reviewing {domain} data.
{summary}
Write exactly:
Insight 1: [specific finding]
Insight 2: [specific finding]
Insight 3: [specific finding]
Risk 1: [specific risk]
Risk 2: [specific risk]
Recommendation 1: [specific action]
Recommendation 2: [specific action]
Be concise, professional, data-driven. No markdown, no dashes.""")
        st.markdown(f'<div class="ai">{result}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ════════════════════════════════════════════════════════════════
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = {}
if "screen" not in st.session_state:
    st.session_state.screen = "landing"   # landing | login | signup | app
if "active" not in st.session_state:
    st.session_state.active = "Overview"

# ════════════════════════════════════════════════════════════════
# SCREEN: LANDING PAGE
# ════════════════════════════════════════════════════════════════
if st.session_state.screen == "landing":
    # Hide sidebar on landing
    st.markdown("""<style>[data-testid="stSidebar"]{display:none!important;}
    .main .block-container{padding:0!important;max-width:100%!important;}
    </style>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-wrap">
      <div class="hero-ring" style="width:300px;height:300px;animation-delay:0s;"></div>
      <div class="hero-ring" style="width:300px;height:300px;animation-delay:1.5s;"></div>
      <div class="hero-ring" style="width:300px;height:300px;animation-delay:3s;"></div>
      <div class="hero-glow"></div>
      <div style="position:relative;z-index:2;">
        <div class="hero-title">Drishti</div>
        <div class="hero-sub">Vision · Intelligence · Clarity</div>
        <div class="hero-tagline">
          Intelligent business foresight powered by Google Gemini AI.<br>
          Transform raw data into executive-level decisions — instantly.
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Centered launch button
    col1, col2, col3 = st.columns([2,1,2])
    with col2:
        if st.button("🚀  Launch Drishti", key="hero_launch", use_container_width=True):
            st.session_state.screen = "login"
            st.rerun()

    # Features strip
    st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background:{SB};padding:48px 56px;'>
      <div style='text-align:center;margin-bottom:36px;'>
        <div style='font-size:0.65rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:{ACC};margin-bottom:10px;'>Core Capabilities</div>
        <div style='font-size:1.6rem;font-weight:800;color:#fff;letter-spacing:-0.03em;'>Six ways Drishti gives you an unfair advantage.</div>
      </div>
      <div style='display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:rgba(255,255,255,0.04);border-radius:12px;overflow:hidden;max-width:1100px;margin:0 auto;'>
        <div style='background:#060F1C;padding:28px 24px;'>
          <div style='font-size:1.4rem;margin-bottom:12px;'>📊</div>
          <div style='font-size:0.88rem;font-weight:700;color:rgba(255,255,255,0.8);margin-bottom:8px;'>AI Executive Summary</div>
          <div style='font-size:0.76rem;color:rgba(255,255,255,0.3);line-height:1.7;'>Board-ready narrative across all four data domains simultaneously.</div>
        </div>
        <div style='background:#060F1C;padding:28px 24px;'>
          <div style='font-size:1.4rem;margin-bottom:12px;'>🔮</div>
          <div style='font-size:0.88rem;font-weight:700;color:rgba(255,255,255,0.8);margin-bottom:8px;'>Predictive Forecasting</div>
          <div style='font-size:0.76rem;color:rgba(255,255,255,0.3);line-height:1.7;'>3-month revenue projections overlaid on every chart.</div>
        </div>
        <div style='background:#060F1C;padding:28px 24px;'>
          <div style='font-size:1.4rem;margin-bottom:12px;'>⚠️</div>
          <div style='font-size:0.88rem;font-weight:700;color:rgba(255,255,255,0.8);margin-bottom:8px;'>Anomaly Detection</div>
          <div style='font-size:0.76rem;color:rgba(255,255,255,0.3);line-height:1.7;'>AI scans for outliers and risk signals ranked by severity.</div>
        </div>
        <div style='background:#060F1C;padding:28px 24px;'>
          <div style='font-size:1.4rem;margin-bottom:12px;'>💬</div>
          <div style='font-size:0.88rem;font-weight:700;color:rgba(255,255,255,0.8);margin-bottom:8px;'>Natural Language Query</div>
          <div style='font-size:0.76rem;color:rgba(255,255,255,0.3);line-height:1.7;'>Ask your data anything in plain English — no SQL needed.</div>
        </div>
        <div style='background:#060F1C;padding:28px 24px;'>
          <div style='font-size:1.4rem;margin-bottom:12px;'>🔗</div>
          <div style='font-size:0.88rem;font-weight:700;color:rgba(255,255,255,0.8);margin-bottom:8px;'>Cross-Domain Insights</div>
          <div style='font-size:0.76rem;color:rgba(255,255,255,0.3);line-height:1.7;'>Hidden correlations connecting Sales, Finance, Marketing & Healthcare.</div>
        </div>
        <div style='background:#060F1C;padding:28px 24px;'>
          <div style='font-size:1.4rem;margin-bottom:12px;'>🏆</div>
          <div style='font-size:0.88rem;font-weight:700;color:rgba(255,255,255,0.8);margin-bottom:8px;'>Industry Benchmarking</div>
          <div style='font-size:0.76rem;color:rgba(255,255,255,0.3);line-height:1.7;'>Upload any dataset and benchmark it against industry data.</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown(f"""
    <div style='background:#040910;padding:22px 56px;display:flex;align-items:center;
                justify-content:space-between;border-top:1px solid rgba(255,255,255,0.04);
                font-size:0.7rem;color:rgba(255,255,255,0.16);'>
      <div style='font-weight:800;color:rgba(255,255,255,0.5);font-size:0.85rem;'>Drishti<span style="color:{ACC};">.</span></div>
      <div>© 2025 Drishti Analytics. All rights reserved.</div>
      <div>Python · Streamlit · Gemini AI</div>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# SCREEN: LOGIN
# ════════════════════════════════════════════════════════════════
elif st.session_state.screen == "login":
    st.markdown("""<style>[data-testid="stSidebar"]{display:none!important;}
    .main .block-container{padding:3rem 1rem!important;max-width:100%!important;}
    </style>""", unsafe_allow_html=True)

    # Back to landing
    if st.button("← Back to home"):
        st.session_state.screen = "landing"
        st.rerun()

    st.markdown(f"""
    <div class="auth-wrap">
      <div class="auth-logo">Drishti<span>.</span></div>
      <div class="auth-title">Welcome back</div>
      <div class="auth-sub">Sign in to access your analytics dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    # Center the form
    col1, col2, col3 = st.columns([1,1.4,1])
    with col2:
        with st.container():
            st.markdown(f"<div style='background:{CARD};border:1px solid {BDR};border-radius:16px;padding:36px 40px;box-shadow:0 4px 24px rgba(0,0,0,0.06);'>", unsafe_allow_html=True)

            st.markdown(f"<div style='text-align:center;font-size:1.4rem;font-weight:900;color:{TXT};margin-bottom:4px;'>Drishti<span style='color:{ACC};'>.</span></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;font-size:1.1rem;font-weight:800;color:{TXT};margin-bottom:4px;'>Welcome back</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;font-size:0.8rem;color:{LITE};margin-bottom:24px;'>Sign in to access your analytics dashboard</div>", unsafe_allow_html=True)

            login_email = st.text_input("Email Address", placeholder="you@company.com", key="login_email")
            login_pass  = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")

            if st.button("Sign In →", key="login_btn", use_container_width=True):
                users = load_users()
                if login_email in users and users[login_email]['password'] == login_pass:
                    st.session_state.authenticated = True
                    st.session_state.user = users[login_email]
                    st.session_state.screen = "app"
                    st.session_state.active = "Overview"
                    st.rerun()
                else:
                    st.markdown(f"<div class='auth-error'>Invalid email or password. Please try again.</div>", unsafe_allow_html=True)

            st.markdown(f"""
            <div class="auth-divider">
              <div class="auth-divider-line"></div>
              <div class="auth-divider-txt">or</div>
              <div class="auth-divider-line"></div>
            </div>""", unsafe_allow_html=True)

            if st.button("Create a free account", key="go_signup", use_container_width=True):
                st.session_state.screen = "signup"
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# SCREEN: SIGNUP
# ════════════════════════════════════════════════════════════════
elif st.session_state.screen == "signup":
    st.markdown("""<style>[data-testid="stSidebar"]{display:none!important;}
    .main .block-container{padding:3rem 1rem!important;max-width:100%!important;}
    </style>""", unsafe_allow_html=True)

    if st.button("← Back to sign in"):
        st.session_state.screen = "login"
        st.rerun()

    col1, col2, col3 = st.columns([1,1.4,1])
    with col2:
        st.markdown(f"<div style='background:{CARD};border:1px solid {BDR};border-radius:16px;padding:36px 40px;box-shadow:0 4px 24px rgba(0,0,0,0.06);'>", unsafe_allow_html=True)

        st.markdown(f"<div style='text-align:center;font-size:1.4rem;font-weight:900;color:{TXT};margin-bottom:4px;'>Drishti<span style='color:{ACC};'>.</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;font-size:1.1rem;font-weight:800;color:{TXT};margin-bottom:4px;'>Create your account</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;font-size:0.8rem;color:{LITE};margin-bottom:24px;'>Free access to all AI-powered dashboards</div>", unsafe_allow_html=True)

        signup_name    = st.text_input("Full Name", placeholder="Samhitha Macha", key="signup_name")
        signup_email   = st.text_input("Email Address", placeholder="you@company.com", key="signup_email")
        signup_company = st.text_input("Company Name", placeholder="Acme Corp", key="signup_company")
        signup_pass    = st.text_input("Password", type="password", placeholder="Choose a strong password", key="signup_pass")
        signup_pass2   = st.text_input("Confirm Password", type="password", placeholder="Repeat your password", key="signup_pass2")

        if st.button("Create Account →", key="signup_btn", use_container_width=True):
            users = load_users()
            if not signup_name or not signup_email or not signup_company or not signup_pass:
                st.markdown("<div class='auth-error'>Please fill in all fields.</div>", unsafe_allow_html=True)
            elif signup_pass != signup_pass2:
                st.markdown("<div class='auth-error'>Passwords do not match.</div>", unsafe_allow_html=True)
            elif signup_email in users:
                st.markdown("<div class='auth-error'>An account with this email already exists.</div>", unsafe_allow_html=True)
            elif len(signup_pass) < 6:
                st.markdown("<div class='auth-error'>Password must be at least 6 characters.</div>", unsafe_allow_html=True)
            else:
                save_user(signup_name, signup_email, signup_company, signup_pass)
                st.session_state.authenticated = True
                st.session_state.user = {
                    'name': signup_name, 'email': signup_email, 'company': signup_company
                }
                st.session_state.screen = "app"
                st.session_state.active = "Overview"
                st.rerun()

        st.markdown(f"""
        <div class="auth-divider">
          <div class="auth-divider-line"></div>
          <div class="auth-divider-txt">already have an account?</div>
          <div class="auth-divider-line"></div>
        </div>""", unsafe_allow_html=True)

        if st.button("Sign in instead", key="go_login", use_container_width=True):
            st.session_state.screen = "login"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# SCREEN: MAIN APP (authenticated)
# ════════════════════════════════════════════════════════════════
elif st.session_state.screen == "app":

    if not st.session_state.authenticated:
        st.session_state.screen = "login"
        st.rerun()

    sales_df, mkt_df, fin_df, hc_df = load_data()
    user = st.session_state.user

    # ── SIDEBAR ──────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style='padding:24px 20px 12px;'>
          <div style='font-size:1.1rem;font-weight:900;color:#F0F4F8;letter-spacing:-0.02em;'>Drishti<span style='color:{ACC};'>.</span></div>
          <div style='font-size:0.62rem;color:#4A5568;text-transform:uppercase;letter-spacing:0.1em;margin-top:2px;'>Analytics Platform</div>
        </div>
        <div style='height:1px;background:rgba(255,255,255,0.07);margin:0 20px 8px;'></div>
        """, unsafe_allow_html=True)

        # User info chip
        name = user.get('name', 'User')
        company = user.get('company', '')
        initials = ''.join([w[0].upper() for w in name.split()[:2]])
        st.markdown(f"""
        <div style='margin:0 16px 12px;padding:10px 14px;background:rgba(255,255,255,0.05);
                    border-radius:8px;display:flex;align-items:center;gap:10px;'>
          <div style='width:32px;height:32px;border-radius:50%;background:{ACC};
                      display:flex;align-items:center;justify-content:center;
                      font-size:0.72rem;font-weight:700;color:#fff;flex-shrink:0;'>{initials}</div>
          <div>
            <div style='font-size:0.78rem;font-weight:700;color:#E2E8F0;'>{name}</div>
            <div style='font-size:0.65rem;color:#4A5568;'>{company}</div>
          </div>
        </div>
        <div style='height:1px;background:rgba(255,255,255,0.07);margin:0 20px 8px;'></div>
        <div style='padding:6px 20px 4px;font-size:0.6rem;font-weight:700;color:#2D3748;text-transform:uppercase;letter-spacing:0.12em;'>Dashboards</div>
        """, unsafe_allow_html=True)

        page = st.radio("Navigation", [
            "Overview", "Sales", "Marketing", "Finance", "Healthcare"
        ], label_visibility="collapsed")

        st.markdown(f"""
        <div style='height:1px;background:rgba(255,255,255,0.07);margin:8px 20px;'></div>
        <div style='padding:6px 20px 4px;font-size:0.6rem;font-weight:700;color:#2D3748;text-transform:uppercase;letter-spacing:0.12em;'>AI Tools</div>
        """, unsafe_allow_html=True)

        page2 = st.radio("AI Tools", [
            "Ask Drishti", "Executive Summary", "Cross-Domain Insights", "Upload Dataset"
        ], label_visibility="collapsed")

        st.markdown(f"""
        <div style='height:1px;background:rgba(255,255,255,0.07);margin:8px 20px;'></div>
        <div style='padding:6px 20px 4px;font-size:0.6rem;font-weight:700;color:#2D3748;text-transform:uppercase;letter-spacing:0.12em;'>More</div>
        """, unsafe_allow_html=True)

        page3 = st.radio("More", ["Contact Us"], label_visibility="collapsed")

        st.markdown(f"""
        <div style='height:1px;background:rgba(255,255,255,0.07);margin:8px 20px;'></div>
        <div style='padding:8px 20px 4px;font-size:0.62rem;color:#2D3748;line-height:1.7;'>
          Jan 2022 – Dec 2023<br>11,000+ records · 4 domains
        </div>
        """, unsafe_allow_html=True)

        if st.button("Sign Out", key="signout"):
            st.session_state.authenticated = False
            st.session_state.user = {}
            st.session_state.screen = "landing"
            st.rerun()

    # Resolve active page
    if st.session_state.get("last_page") != page:
        st.session_state.active = page
        st.session_state.last_page = page
    elif st.session_state.get("last_page2") != page2:
        st.session_state.active = page2
        st.session_state.last_page2 = page2
    elif st.session_state.get("last_page3") != page3:
        st.session_state.active = page3
        st.session_state.last_page3 = page3

    active = st.session_state.active

    # ════════════════════════════════════════════════════════════
    # OVERVIEW
    # ════════════════════════════════════════════════════════════
    if active == "Overview":
        st.markdown("<div class='ph'><p class='pt'>Business Overview</p><p class='ps'>Cross-domain performance summary — Sales, Marketing, Finance & Healthcare</p></div>", unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("Total Revenue",      f"${sales_df['revenue'].sum()/1e6:.2f}M")
        with c2: st.metric("Avg Marketing ROI",  f"{mkt_df['roi'].mean():.2f}x")
        with c3:
            v = fin_df['variance'].mean()
            st.metric("Budget Variance", f"${abs(v):,.0f}", "Under" if v>0 else "Over")
        with c4: st.metric("Avg Treatment Cost", f"${hc_df['treatment_cost'].mean():,.0f}")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("<div class='cc'><div class='ct'>Monthly Revenue Trend</div>", unsafe_allow_html=True)
            m = sales_df.groupby(sales_df['date'].dt.to_period('M').astype(str))['revenue'].sum().reset_index()
            m.columns = ['month','revenue']
            fig = px.area(m, x='month', y='revenue', color_discrete_sequence=[ACC])
            fig.update_traces(fillcolor="rgba(27,108,168,0.1)", line_color=ACC)
            st.plotly_chart(fig_clean(fig), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='cc'><div class='ct'>Campaign ROI by Type</div>", unsafe_allow_html=True)
            r = mkt_df.groupby('campaign_type')['roi'].mean().sort_values(ascending=True).reset_index()
            fig = px.bar(r, x='roi', y='campaign_type', orientation='h', color='roi', color_continuous_scale=BLUE_SCALE)
            st.plotly_chart(fig_clean(fig), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        c3,c4 = st.columns(2)
        with c3:
            st.markdown("<div class='cc'><div class='ct'>Budget vs Actual by Department</div>", unsafe_allow_html=True)
            d = fin_df.groupby('department')[['budget','actual_spend']].sum().reset_index()
            fig = px.bar(d, x='department', y=['budget','actual_spend'], barmode='group',
                         color_discrete_map={'budget':ACC,'actual_spend':ACC2})
            st.plotly_chart(fig_clean(fig), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with c4:
            st.markdown("<div class='cc'><div class='ct'>Patient Admissions by Department</div>", unsafe_allow_html=True)
            a = hc_df['department'].value_counts().reset_index()
            a.columns = ['dept','count']
            fig = px.pie(a, names='dept', values='count', color_discrete_sequence=CSEQ, hole=0.52)
            fig.update_traces(textposition='outside', textfont_size=10)
            st.plotly_chart(fig_clean(fig, h=290), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════
    # SALES
    # ════════════════════════════════════════════════════════════
    elif active == "Sales":
        st.markdown("<div class='ph'><p class='pt'>Sales Analytics</p><p class='ps'>Revenue, profitability, and channel performance</p></div>", unsafe_allow_html=True)

        st.markdown("<div class='cc'><div class='ct'>Natural Language Filter</div>", unsafe_allow_html=True)
        nl_col1, nl_col2 = st.columns([4,1])
        with nl_col1:
            nl_query = st.text_input("NL Filter", placeholder='"show only West region" or "revenue above 5000"', label_visibility="collapsed")
        with nl_col2:
            nl_apply = st.button("Apply Filter", key="sales_nl")
        st.markdown("</div>", unsafe_allow_html=True)

        c1,c2 = st.columns(2)
        with c1: reg = st.multiselect("Region", sales_df['region'].unique(), default=list(sales_df['region'].unique()))
        with c2: ch  = st.multiselect("Channel", sales_df['channel'].unique(), default=list(sales_df['channel'].unique()))
        df = sales_df[sales_df['region'].isin(reg) & sales_df['channel'].isin(ch)]
        if nl_apply and nl_query:
            fd = parse_nl_filter(nl_query, df, "Sales")
            df, applied = apply_nl_filter(df, fd)
            if applied: st.success(f"Filter applied: {fd}")
            else: st.warning("Could not parse filter.")

        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("Total Revenue", f"${df['revenue'].sum()/1e6:.2f}M")
        with c2: st.metric("Total Profit",  f"${df['profit'].sum()/1e6:.2f}M")
        with c3: st.metric("Avg Discount",  f"{df['discount_pct'].mean()*100:.1f}%")
        with c4: st.metric("Return Rate",   f"{df['returned'].mean()*100:.1f}%")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("<div class='cc'><div class='ct'>Monthly Revenue + Forecast</div>", unsafe_allow_html=True)
            m = df.groupby(df['date'].dt.to_period('M').astype(str))['revenue'].sum().reset_index()
            m.columns = ['month','revenue']
            result = generate_forecast(df, 'date', 'revenue', periods=3)
            if result and result[0]:
                future_months, future_vals, _, _ = result
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=m['month'], y=m['revenue'], name='Actual', line=dict(color=ACC, width=2.5)))
                fig.add_trace(go.Scatter(x=future_months, y=future_vals, name='Forecast',
                    line=dict(color=WARN, width=2, dash='dot'), mode='lines+markers', marker=dict(size=6, color=WARN)))
            else:
                fig = px.line(m, x='month', y='revenue', color_discrete_sequence=[ACC])
            st.plotly_chart(fig_clean(fig), use_container_width=True)
            st.markdown('<span class="forecast-badge">3-Month Forecast Shown</span>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='cc'><div class='ct'>Revenue by Product</div>", unsafe_allow_html=True)
            p = df.groupby('product')['revenue'].sum().sort_values().reset_index()
            fig = px.bar(p, x='revenue', y='product', orientation='h', color='revenue', color_continuous_scale=BLUE_SCALE)
            st.plotly_chart(fig_clean(fig), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        c3,c4 = st.columns(2)
        with c3:
            st.markdown("<div class='cc'><div class='ct'>Revenue & Profit by Region</div>", unsafe_allow_html=True)
            r = df.groupby('region')[['revenue','profit']].sum().reset_index()
            fig = px.bar(r, x='region', y=['revenue','profit'], barmode='group',
                         color_discrete_map={'revenue':ACC,'profit':ACC2})
            st.plotly_chart(fig_clean(fig), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with c4:
            st.markdown("<div class='cc'><div class='ct'>Revenue by Channel</div>", unsafe_allow_html=True)
            cv = df.groupby('channel')['revenue'].sum().reset_index()
            fig = px.pie(cv, names='channel', values='revenue', color_discrete_sequence=CSEQ, hole=0.52)
            fig.update_traces(textposition='outside', textfont_size=10)
            st.plotly_chart(fig_clean(fig, h=290), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<hr class='dv'>", unsafe_allow_html=True)
        st.markdown("<div class='sl'>Anomaly Detection</div>", unsafe_allow_html=True)
        if st.button("Scan for Anomalies", key="s_anomaly"):
            with st.spinner("Scanning..."):
                anomalies = parse_anomalies(detect_anomalies(df, 'revenue', 'region', 'Sales'))
            for a in anomalies:
                st.markdown(f"<div class='anomaly-card'><div class='anomaly-title'>⚠ {a.get('title','')} — {a.get('severity','')}</div><div class='anomaly-body'>{a.get('detail','')}</div></div>", unsafe_allow_html=True)

        ai_section("s_ai", f"""Total Revenue: ${df['revenue'].sum():,.0f}
Total Profit: ${df['profit'].sum():,.0f}
Profit Margin: {(df['profit'].sum()/df['revenue'].sum()*100):.1f}%
Top Region: {df.groupby('region')['revenue'].sum().idxmax()}
Top Product: {df.groupby('product')['revenue'].sum().idxmax()}
Best Channel: {df.groupby('channel')['revenue'].sum().idxmax()}""", "Sales")

    # ════════════════════════════════════════════════════════════
    # MARKETING
    # ════════════════════════════════════════════════════════════
    elif active == "Marketing":
        st.markdown("<div class='ph'><p class='pt'>Marketing Analytics</p><p class='ps'>Campaign performance, ROI, and conversion analysis</p></div>", unsafe_allow_html=True)

        st.markdown("<div class='cc'><div class='ct'>Natural Language Filter</div>", unsafe_allow_html=True)
        nl_col1, nl_col2 = st.columns([4,1])
        with nl_col1:
            nl_query_m = st.text_input("NL Filter M", placeholder='"show only Social Media" or "ROI above 8"', label_visibility="collapsed", key="m_nl_input")
        with nl_col2:
            nl_apply_m = st.button("Apply Filter", key="mkt_nl")
        st.markdown("</div>", unsafe_allow_html=True)

        cf = st.multiselect("Campaign Type", mkt_df['campaign_type'].unique(), default=list(mkt_df['campaign_type'].unique()))
        df = mkt_df[mkt_df['campaign_type'].isin(cf)]
        if nl_apply_m and nl_query_m:
            fd = parse_nl_filter(nl_query_m, df, "Marketing")
            df, applied = apply_nl_filter(df, fd)
            if applied: st.success(f"Filter applied: {fd}")
            else: st.warning("Could not parse filter.")

        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("Average ROI",         f"{df['roi'].mean():.2f}x")
        with c2: st.metric("Average CTR",         f"{df['ctr'].mean()*100:.2f}%")
        with c3: st.metric("Avg Conversion Rate", f"{df['conversion_rate'].mean()*100:.2f}%")
        with c4: st.metric("Total Spend",         f"${df['spend'].sum()/1e6:.2f}M")

        c1,c2 = st.columns(2)
        with c1:
            st.markdown("<div class='cc'><div class='ct'>Avg ROI by Campaign Type</div>", unsafe_allow_html=True)
            r = df.groupby('campaign_type')['roi'].mean().sort_values(ascending=True).reset_index()
            fig = px.bar(r, x='roi', y='campaign_type', orientation='h', color='roi', color_continuous_scale=BLUE_SCALE)
            st.plotly_chart(fig_clean(fig), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='cc'><div class='ct'>Conversion Rate by Segment</div>", unsafe_allow_html=True)
            s = df.groupby('customer_segment')['conversion_rate'].mean().sort_values(ascending=True).reset_index()
            fig = px.bar(s, x='conversion_rate', y='customer_segment', orientation='h', color='conversion_rate', color_continuous_scale=BLUE_SCALE2)
            st.plotly_chart(fig_clean(fig), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='cc'><div class='ct'>Spend vs Revenue Generated</div>", unsafe_allow_html=True)
        fig = px.scatter(df, x='spend', y='revenue_generated', color='campaign_type', size='conversions', color_discrete_sequence=CSEQ, opacity=0.72)
        st.plotly_chart(fig_clean(fig, h=360), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Scan for Anomalies", key="m_anomaly"):
            with st.spinner("Scanning..."):
                anomalies = parse_anomalies(detect_anomalies(df, 'roi', 'campaign_type', 'Marketing'))
            for a in anomalies:
                st.markdown(f"<div class='anomaly-card'><div class='anomaly-title'>⚠ {a.get('title','')} — {a.get('severity','')}</div><div class='anomaly-body'>{a.get('detail','')}</div></div>", unsafe_allow_html=True)

        ai_section("m_ai", f"Avg ROI: {df['roi'].mean():.2f}x\nBest Campaign: {df.groupby('campaign_type')['roi'].mean().idxmax()}\nTotal Spend: ${df['spend'].sum():,.0f}", "Marketing")

    # ════════════════════════════════════════════════════════════
    # FINANCE
    # ════════════════════════════════════════════════════════════
    elif active == "Finance":
        st.markdown("<div class='ph'><p class='pt'>Finance Analytics</p><p class='ps'>Budget performance, variance tracking, and expense analysis</p></div>", unsafe_allow_html=True)

        yr = st.selectbox("Fiscal Year", ['All'] + sorted(fin_df['year'].unique().tolist()))
        df = fin_df if yr == 'All' else fin_df[fin_df['year'] == int(yr)]

        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("Total Budget",       f"${df['budget'].sum()/1e6:.2f}M")
        with c2: st.metric("Total Actual Spend", f"${df['actual_spend'].sum()/1e6:.2f}M")
        with c3: st.metric("Over-Budget Rate",   f"{df['over_budget'].mean()*100:.1f}%")
        with c4: st.metric("Avg Variance",       f"${df['variance'].mean():,.0f}")

        c1,c2 = st.columns(2)
        with c1:
            st.markdown("<div class='cc'><div class='ct'>Budget vs Actual by Department</div>", unsafe_allow_html=True)
            d = df.groupby('department')[['budget','actual_spend']].sum().reset_index()
            fig = px.bar(d, x='department', y=['budget','actual_spend'], barmode='group',
                         color_discrete_map={'budget':ACC,'actual_spend':ACC2})
            st.plotly_chart(fig_clean(fig), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='cc'><div class='ct'>Over-Budget Rate by Department</div>", unsafe_allow_html=True)
            o = df.groupby('department')['over_budget'].mean().reset_index()
            o['pct'] = (o['over_budget']*100).round(1)
            fig = px.bar(o, x='department', y='pct', color='pct', color_continuous_scale=RED_SCALE)
            st.plotly_chart(fig_clean(fig), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        c3,c4 = st.columns(2)
        with c3:
            st.markdown("<div class='cc'><div class='ct'>Expense Category Breakdown</div>", unsafe_allow_html=True)
            e = df.groupby('expense_category')['actual_spend'].sum().reset_index()
            fig = px.pie(e, names='expense_category', values='actual_spend', color_discrete_sequence=CSEQ, hole=0.52)
            fig.update_traces(textposition='outside', textfont_size=10)
            st.plotly_chart(fig_clean(fig, h=290), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with c4:
            st.markdown("<div class='cc'><div class='ct'>Quarterly Budget vs Spend</div>", unsafe_allow_html=True)
            q = df.groupby('quarter')[['budget','actual_spend']].sum().reset_index()
            fig = px.bar(q, x='quarter', y=['budget','actual_spend'], barmode='group',
                         color_discrete_map={'budget':ACC,'actual_spend':ACC2})
            st.plotly_chart(fig_clean(fig), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Scan for Anomalies", key="f_anomaly"):
            with st.spinner("Scanning..."):
                anomalies = parse_anomalies(detect_anomalies(df, 'actual_spend', 'department', 'Finance'))
            for a in anomalies:
                st.markdown(f"<div class='anomaly-card'><div class='anomaly-title'>⚠ {a.get('title','')} — {a.get('severity','')}</div><div class='anomaly-body'>{a.get('detail','')}</div></div>", unsafe_allow_html=True)

        ai_section("f_ai", f"Budget: ${df['budget'].sum():,.0f}\nActual: ${df['actual_spend'].sum():,.0f}\nOver-Budget Rate: {df['over_budget'].mean()*100:.1f}%", "Finance")

    # ════════════════════════════════════════════════════════════
    # HEALTHCARE
    # ════════════════════════════════════════════════════════════
    elif active == "Healthcare":
        st.markdown("<div class='ph'><p class='pt'>Healthcare Analytics</p><p class='ps'>Patient outcomes, treatment costs, and departmental performance</p></div>", unsafe_allow_html=True)

        st.markdown("<div class='cc'><div class='ct'>Natural Language Filter</div>", unsafe_allow_html=True)
        nl_col1, nl_col2 = st.columns([4,1])
        with nl_col1:
            nl_query_h = st.text_input("NL Filter H", placeholder='"show only Cardiology" or "cost above 10000"', label_visibility="collapsed", key="h_nl_input")
        with nl_col2:
            nl_apply_h = st.button("Apply Filter", key="hc_nl")
        st.markdown("</div>", unsafe_allow_html=True)

        dpf = st.multiselect("Department", hc_df['department'].unique(), default=list(hc_df['department'].unique()))
        df  = hc_df[hc_df['department'].isin(dpf)]
        if nl_apply_h and nl_query_h:
            fd = parse_nl_filter(nl_query_h, df, "Healthcare")
            df, applied = apply_nl_filter(df, fd)
            if applied: st.success(f"Filter applied: {fd}")
            else: st.warning("Could not parse filter.")

        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("Total Patients",     f"{len(df):,}")
        with c2: st.metric("Avg Treatment Cost", f"${df['treatment_cost'].mean():,.0f}")
        with c3: st.metric("Readmission Rate",   f"{df['readmitted'].mean()*100:.1f}%")
        with c4: st.metric("Avg Stay",           f"{df['length_of_stay'].mean():.1f} days")

        c1,c2 = st.columns(2)
        with c1:
            st.markdown("<div class='cc'><div class='ct'>Admissions by Department</div>", unsafe_allow_html=True)
            a = df['department'].value_counts().reset_index(); a.columns = ['dept','count']
            fig = px.bar(a, x='dept', y='count', color='count', color_continuous_scale=BLUE_SCALE)
            st.plotly_chart(fig_clean(fig), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='cc'><div class='ct'>Most Common Diagnoses</div>", unsafe_allow_html=True)
            d = df['diagnosis'].value_counts().reset_index(); d.columns = ['diagnosis','count']
            fig = px.bar(d, x='count', y='diagnosis', orientation='h', color='count', color_continuous_scale=RED_SCALE)
            st.plotly_chart(fig_clean(fig), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        c3,c4 = st.columns(2)
        with c3:
            st.markdown("<div class='cc'><div class='ct'>Avg Cost by Age Group</div>", unsafe_allow_html=True)
            ag = df.groupby('age_group', observed=True)['treatment_cost'].mean().reset_index()
            fig = px.bar(ag, x='age_group', y='treatment_cost', color='treatment_cost', color_continuous_scale=BLUE_SCALE)
            st.plotly_chart(fig_clean(fig), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with c4:
            st.markdown("<div class='cc'><div class='ct'>Avg Cost by Insurance Type</div>", unsafe_allow_html=True)
            ins = df.groupby('insurance_type')['treatment_cost'].mean().reset_index()
            fig = px.bar(ins, x='insurance_type', y='treatment_cost', color='treatment_cost', color_continuous_scale=BLUE_SCALE2)
            st.plotly_chart(fig_clean(fig), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Scan for Anomalies", key="h_anomaly"):
            with st.spinner("Scanning..."):
                anomalies = parse_anomalies(detect_anomalies(df, 'treatment_cost', 'department', 'Healthcare'))
            for a in anomalies:
                st.markdown(f"<div class='anomaly-card'><div class='anomaly-title'>⚠ {a.get('title','')} — {a.get('severity','')}</div><div class='anomaly-body'>{a.get('detail','')}</div></div>", unsafe_allow_html=True)

        ai_section("h_ai", f"Patients: {len(df):,}\nAvg Cost: ${df['treatment_cost'].mean():,.0f}\nReadmission: {df['readmitted'].mean()*100:.1f}%", "Healthcare")

    # ════════════════════════════════════════════════════════════
    # ASK DRISHTI
    # ════════════════════════════════════════════════════════════
    elif active == "Ask Drishti":
        st.markdown("<div class='ph'><p class='pt'>Ask Drishti</p><p class='ps'>Ask any question about your data in plain English</p></div>", unsafe_allow_html=True)

        domain_choice = st.selectbox("Domain", ["All Domains","Sales","Marketing","Finance","Healthcare"])
        suggestions = {
            "Sales": ["Which region had the highest revenue?","What is the best performing product?","Which channel has the lowest return rate?"],
            "Marketing": ["Which campaign type has the best ROI?","Which customer segment converts best?","What is our cost per conversion?"],
            "Finance": ["Which department is most over budget?","What is our overall budget utilization?","Which expense category is highest?"],
            "Healthcare": ["Which department has the highest readmission rate?","What diagnosis costs the most?","How does insurance type affect costs?"],
            "All Domains": ["Which domain is performing best overall?","Where are we losing the most money?","What should be our top priority?"]
        }
        st.markdown("<div class='sl'>Suggested Questions</div>", unsafe_allow_html=True)
        s_cols = st.columns(3)
        selected_suggestion = None
        for i, sug in enumerate(suggestions.get(domain_choice, [])):
            with s_cols[i%3]:
                if st.button(sug, key=f"sug_{i}"): selected_suggestion = sug

        question = st.text_input("Your Question", value=selected_suggestion or "", placeholder="e.g. Which region had the worst Q3 performance?")
        if st.button("Ask Drishti", key="qa_submit") and question:
            summaries = []
            if domain_choice in ("Sales","All Domains"):
                summaries.append(f"Sales: Revenue=${sales_df['revenue'].sum():,.0f}, Top Region={sales_df.groupby('region')['revenue'].sum().idxmax()}, Margin={sales_df['profit'].sum()/sales_df['revenue'].sum()*100:.1f}%")
            if domain_choice in ("Marketing","All Domains"):
                summaries.append(f"Marketing: Avg ROI={mkt_df['roi'].mean():.2f}x, Best Campaign={mkt_df.groupby('campaign_type')['roi'].mean().idxmax()}, Spend=${mkt_df['spend'].sum():,.0f}")
            if domain_choice in ("Finance","All Domains"):
                summaries.append(f"Finance: Budget=${fin_df['budget'].sum():,.0f}, Over-Budget={fin_df['over_budget'].mean()*100:.1f}%")
            if domain_choice in ("Healthcare","All Domains"):
                summaries.append(f"Healthcare: Patients={len(hc_df):,}, Avg Cost=${hc_df['treatment_cost'].mean():,.0f}, Readmission={hc_df['readmitted'].mean()*100:.1f}%")

            with st.spinner("Drishti is thinking..."):
                answer = gemini(f"""You are a senior data analyst. Answer this question using the data.
Data: {chr(10).join(summaries)}
Question: {question}
Give a direct, specific, data-driven answer in 2-4 sentences. Include specific numbers. No markdown.""")
            st.markdown(f'<div class="qa-answer">💡 {answer}</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════
    # EXECUTIVE SUMMARY
    # ════════════════════════════════════════════════════════════
    elif active == "Executive Summary":
        st.markdown("<div class='ph'><p class='pt'>Executive Summary</p><p class='ps'>AI-generated boardroom-ready summary across all four domains</p></div>", unsafe_allow_html=True)
        st.markdown(f"""<div style='background:#EBF8FF;border:1px solid #BEE3F8;border-left:4px solid {ACC};border-radius:10px;padding:16px 20px;margin-bottom:20px;'>
            <div style='font-size:0.78rem;font-weight:700;color:{ACC};margin-bottom:4px;'>What this does</div>
            <div style='font-size:0.82rem;color:{MID};'>Generates a comprehensive executive summary covering all 4 domains with AI-identified wins, concerns, and strategic recommendations.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Generate Executive Summary", key="exec_summary"):
            with st.spinner("Preparing boardroom-ready summary..."):
                result = gemini(f"""You are a Chief Analytics Officer preparing a board-level summary.
Sales: Revenue=${sales_df['revenue'].sum():,.0f}, Margin={sales_df['profit'].sum()/sales_df['revenue'].sum()*100:.1f}%
Marketing: Avg ROI={mkt_df['roi'].mean():.2f}x, Spend=${mkt_df['spend'].sum():,.0f}
Finance: Budget=${fin_df['budget'].sum():,.0f}, Over-Budget={fin_df['over_budget'].mean()*100:.1f}%
Healthcare: Patients={len(hc_df):,}, Readmission={hc_df['readmitted'].mean()*100:.1f}%, Satisfaction={hc_df['satisfaction_score'].mean():.1f}/10

Write: EXECUTIVE SUMMARY, PERFORMANCE OVERVIEW, KEY WINS (3), CRITICAL CONCERNS (2), STRATEGIC RECOMMENDATIONS (3), CROSS-DOMAIN INSIGHT.
Professional tone. No markdown symbols.""", max_tokens=2000)
            st.markdown(f'<div class="ai" style="font-size:0.9rem;">{result}</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════
    # CROSS-DOMAIN INSIGHTS
    # ════════════════════════════════════════════════════════════
    elif active == "Cross-Domain Insights":
        st.markdown("<div class='ph'><p class='pt'>Cross-Domain Insights</p><p class='ps'>AI-powered correlations connecting all four domains</p></div>", unsafe_allow_html=True)

        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("Sales Revenue",       f"${sales_df['revenue'].sum()/1e6:.1f}M")
        with c2: st.metric("Marketing ROI",       f"{mkt_df['roi'].mean():.1f}x")
        with c3: st.metric("Finance Over-Budget", f"{fin_df['over_budget'].mean()*100:.0f}%")
        with c4: st.metric("HC Satisfaction",     f"{hc_df['satisfaction_score'].mean():.1f}/10")

        st.markdown("<div class='cc'><div class='ct'>Sales Revenue vs Marketing Spend — Monthly</div>", unsafe_allow_html=True)
        s_m  = sales_df.groupby(sales_df['date'].dt.to_period('M').astype(str))['revenue'].sum().reset_index(); s_m.columns=['month','revenue']
        mk_m = mkt_df.groupby(mkt_df['date'].dt.to_period('M').astype(str))['spend'].sum().reset_index(); mk_m.columns=['month','spend']
        merged = s_m.merge(mk_m, on='month', how='inner')
        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Scatter(x=merged['month'], y=merged['revenue'], name='Sales Revenue', line=dict(color=ACC, width=2)), secondary_y=False)
        fig.add_trace(go.Scatter(x=merged['month'], y=merged['spend'], name='Mkt Spend', line=dict(color=WARN, width=2, dash='dot')), secondary_y=True)
        fig.update_layout(height=300, margin=dict(t=8,b=8,l=4,r=4), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter",size=11,color=MID))
        fig.update_xaxes(gridcolor=BDR); fig.update_yaxes(gridcolor=BDR, secondary_y=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Find Cross-Domain Correlations", key="cross_insights"):
            with st.spinner("Analyzing patterns across all 4 domains..."):
                raw = cross_domain_insights(sales_df, mkt_df, fin_df, hc_df)
                insights = parse_cross_insights(raw)
            for ins in insights:
                st.markdown(f"""<div class='cross-card'>
                    <div class='cross-title'>🔗 {ins.get('title','')}</div>
                    <div class='cross-body'><strong>Finding:</strong> {ins.get('finding','')}<br><strong>Action:</strong> {ins.get('action','')}</div>
                </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════
    # UPLOAD DATASET
    # ════════════════════════════════════════════════════════════
    elif active == "Upload Dataset":
        st.markdown("<div class='ph'><p class='pt'>Upload Dataset</p><p class='ps'>Upload any CSV or Excel file — get instant charts, AI insights, and anomaly detection</p></div>", unsafe_allow_html=True)

        uf = st.file_uploader("Upload CSV or Excel file", type=["csv","xlsx","xls"])
        if uf:
            try:
                df = pd.read_csv(uf) if uf.name.endswith('.csv') else pd.read_excel(uf)
                num = df.select_dtypes(include=[np.number]).columns.tolist()
                cat = df.select_dtypes(include=['object','category']).columns.tolist()

                c1,c2,c3,c4 = st.columns(4)
                with c1: st.metric("Total Rows",      f"{len(df):,}")
                with c2: st.metric("Total Columns",   f"{len(df.columns)}")
                with c3: st.metric("Numeric Columns", f"{len(num)}")
                with c4: st.metric("Missing Values",  f"{df.isnull().sum().sum():,}")

                st.markdown("<div class='cc'><div class='ct'>Data Preview</div>", unsafe_allow_html=True)
                st.dataframe(df.head(10), use_container_width=True, height=260)
                st.markdown("</div>", unsafe_allow_html=True)

                if num and cat:
                    c1,c2 = st.columns(2)
                    tc, tn = cat[0], num[0]
                    grp = df.groupby(tc)[tn].sum().sort_values(ascending=True).reset_index()
                    with c1:
                        st.markdown("<div class='cc'><div class='ct'>Top Category Distribution</div>", unsafe_allow_html=True)
                        fig = px.bar(grp, x=tn, y=tc, orientation='h', color=tn, color_continuous_scale=BLUE_SCALE)
                        st.plotly_chart(fig_clean(fig), use_container_width=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    with c2:
                        st.markdown("<div class='cc'><div class='ct'>Category Share</div>", unsafe_allow_html=True)
                        fig = px.pie(grp, names=tc, values=tn, color_discrete_sequence=CSEQ, hole=0.52)
                        fig.update_traces(textposition='outside', textfont_size=10)
                        st.plotly_chart(fig_clean(fig, h=290), use_container_width=True)
                        st.markdown("</div>", unsafe_allow_html=True)

                if len(num) >= 2:
                    st.markdown("<div class='cc'><div class='ct'>Numeric Correlation</div>", unsafe_allow_html=True)
                    fig = px.scatter(df.sample(min(500,len(df))), x=num[0], y=num[1],
                                     color=cat[0] if cat else None, color_discrete_sequence=CSEQ, opacity=0.7)
                    st.plotly_chart(fig_clean(fig, h=340), use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("<hr class='dv'>", unsafe_allow_html=True)
                st.markdown("<div class='sl'>AI-Generated Analysis</div>", unsafe_allow_html=True)
                if st.button("Generate Insights", key="u_ai"):
                    with st.spinner("Analyzing your data..."):
                        result = gemini(f"""Analyze dataset '{uf.name}'.
Columns: {', '.join(df.columns)}
Rows: {len(df):,}
Sample: {df.head(5).to_string()}
Stats: {df.describe().to_string()}
Write: Insight 1, Insight 2, Insight 3, Risk 1, Risk 2, Recommendation 1, Recommendation 2.""")
                    st.markdown(f'<div class="ai">{result}</div>', unsafe_allow_html=True)

                if num:
                    st.markdown("<hr class='dv'>", unsafe_allow_html=True)
                    st.markdown("<div class='sl'>Anomaly Detection</div>", unsafe_allow_html=True)
                    if st.button("Scan for Anomalies", key="u_anomaly"):
                        with st.spinner("Scanning..."):
                            anomalies = parse_anomalies(detect_anomalies(df, num[0], cat[0] if cat else None, uf.name))
                        for a in anomalies:
                            st.markdown(f"<div class='anomaly-card'><div class='anomaly-title'>⚠ {a.get('title','')} — {a.get('severity','')}</div><div class='anomaly-body'>{a.get('detail','')}</div></div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Could not read file: {e}")
        else:
            st.markdown(f"""
            <div style='background:{CARD};border:2px dashed {BDR};border-radius:12px;
                        padding:56px;text-align:center;color:{LITE};margin-top:8px;'>
              <div style='font-size:2rem;margin-bottom:12px;'>📂</div>
              <div style='font-size:0.9rem;font-weight:600;color:{MID};margin-bottom:8px;'>Drop your file here or click to browse</div>
              <div style='font-size:0.8rem;'>Supports CSV, XLSX, XLS — any domain</div>
            </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════
    # CONTACT US
    # ════════════════════════════════════════════════════════════
    elif active == "Contact Us":
        st.markdown("<div class='ph'><p class='pt'>Contact Us</p><p class='ps'>Get in touch with the Drishti team</p></div>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown(f"""
            <div style='background:{CARD};border:1px solid {BDR};border-radius:14px;
                        padding:40px 44px;box-shadow:0 1px 4px rgba(0,0,0,0.04);margin-bottom:24px;'>
              <div style='font-size:1.1rem;font-weight:800;color:{TXT};letter-spacing:-0.02em;margin-bottom:6px;'>Send us a message</div>
              <div style='font-size:0.82rem;color:{LITE};margin-bottom:24px;'>We typically respond within 24 hours.</div>
            </div>
            """, unsafe_allow_html=True)

            # Pre-fill from logged in user
            default_name    = user.get('name','')
            default_email   = user.get('email','')
            default_company = user.get('company','')

            contact_name    = st.text_input("Full Name",    value=default_name,    key="c_name")
            contact_email   = st.text_input("Email Address",value=default_email,   key="c_email")
            contact_company = st.text_input("Company Name", value=default_company, key="c_company")
            contact_msg     = st.text_area("Message / Use Case", placeholder="Tell us how you'd like to use Drishti, any questions you have, or feedback...", height=140, key="c_msg")

            if st.button("Send Message →", key="contact_submit", use_container_width=True):
                if not contact_name or not contact_email or not contact_msg:
                    st.error("Please fill in your name, email, and message.")
                else:
                    save_contact(contact_name, contact_email, contact_company, contact_msg)
                    st.markdown(f"""
                    <div style='background:#F0FFF4;border:1px solid #C6F6D5;border-left:4px solid {SUCCESS};
                                border-radius:10px;padding:16px 20px;margin-top:12px;'>
                      <div style='font-size:0.82rem;font-weight:700;color:{SUCCESS};margin-bottom:4px;'>Message sent! ✓</div>
                      <div style='font-size:0.8rem;color:{MID};'>Thanks {contact_name}, we'll be in touch at {contact_email} soon.</div>
                    </div>""", unsafe_allow_html=True)

        # Info cards below
        st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
        ci1, ci2, ci3 = st.columns(3)
        for col_w, icon, title, desc in [
            (ci1, "📧", "Email", "samhithamacha@example.com"),
            (ci2, "🌐", "Website", "samhithamacha.github.io/ai-business-dashboard"),
            (ci3, "🚀", "Platform", "samhithamacha-ai-dashboard.streamlit.app"),
        ]:
            with col_w:
                st.markdown(f"""
                <div style='background:{CARD};border:1px solid {BDR};border-radius:10px;
                            padding:20px 22px;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,0.04);'>
                  <div style='font-size:1.6rem;margin-bottom:8px;'>{icon}</div>
                  <div style='font-size:0.78rem;font-weight:700;color:{TXT};margin-bottom:4px;'>{title}</div>
                  <div style='font-size:0.72rem;color:{LITE};'>{desc}</div>
                </div>""", unsafe_allow_html=True)