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
from datetime import datetime, timedelta

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

st.set_page_config(page_title="Drishti Analytics", layout="wide", initial_sidebar_state="expanded")

# ── PALETTE ──────────────────────────────────────────────────────
BG     = "#F5F7FA"
CARD   = "#FFFFFF"
SB     = "#0F1C2E"
ACC    = "#1B6CA8"
ACC2   = "#2E8BC0"
ACC3   = "#0D4F8B"
TXT    = "#0D1B2A"
MID    = "#4A5568"
LITE   = "#8896A5"
BDR    = "#E2E8F0"
DANGER = "#C0392B"
SUCCESS= "#27AE60"
WARN   = "#F39C12"
CSEQ   = ["#1B6CA8","#2E8BC0","#48A9C5","#5BC0D8","#3A7BD5","#0D4F8B"]

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html,body,[class*="css"]{{font-family:'Inter',sans-serif!important;background:{BG};color:{TXT};}}

[data-testid="stSidebar"]{{background:{SB}!important;}}
[data-testid="stSidebar"] > div:first-child{{background:{SB}!important;padding:0!important;}}
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

.main .block-container{{padding:2rem 2.5rem 3rem;max-width:1400px;background:{BG};}}

.ph{{margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid {BDR};}}
.pt{{font-size:1.55rem;font-weight:800;letter-spacing:-0.03em;color:{TXT};margin:0 0 4px;}}
.ps{{font-size:0.8rem;color:{LITE};margin:0;}}

div[data-testid="stMetric"]{{
  background:{CARD}!important;border:1px solid {BDR}!important;
  border-top:3px solid {ACC}!important;border-radius:10px!important;
  padding:18px 20px!important;box-shadow:0 1px 4px rgba(0,0,0,0.04);
}}
div[data-testid="stMetricLabel"]>div{{font-size:0.68rem!important;font-weight:600!important;color:{LITE}!important;text-transform:uppercase!important;letter-spacing:0.08em!important;}}
div[data-testid="stMetricValue"]>div{{font-size:1.5rem!important;font-weight:800!important;color:{TXT}!important;letter-spacing:-0.02em!important;}}

.cc{{background:{CARD};border:1px solid {BDR};border-radius:10px;padding:20px 22px 6px;margin-bottom:16px;box-shadow:0 1px 4px rgba(0,0,0,0.04);}}
.ct{{font-size:0.68rem;font-weight:700;color:{LITE};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:14px;padding-bottom:12px;border-bottom:1px solid {BDR};}}

.ai{{background:{CARD};border:1px solid {BDR};border-left:4px solid {ACC};border-radius:10px;padding:22px 26px;margin-top:8px;font-size:0.875rem;line-height:1.8;color:{MID};white-space:pre-wrap;box-shadow:0 1px 4px rgba(0,0,0,0.04);}}

.anomaly-card{{background:#FFF5F5;border:1px solid #FED7D7;border-left:4px solid {DANGER};border-radius:10px;padding:16px 20px;margin:6px 0;}}
.anomaly-title{{font-size:0.78rem;font-weight:700;color:{DANGER};margin-bottom:4px;}}
.anomaly-body{{font-size:0.82rem;color:{MID};line-height:1.6;}}

.insight-card{{background:#F0FFF4;border:1px solid #C6F6D5;border-left:4px solid {SUCCESS};border-radius:10px;padding:16px 20px;margin:6px 0;}}
.insight-title{{font-size:0.78rem;font-weight:700;color:{SUCCESS};margin-bottom:4px;}}
.insight-body{{font-size:0.82rem;color:{MID};line-height:1.6;}}

.cross-card{{background:#EBF8FF;border:1px solid #BEE3F8;border-left:4px solid {ACC};border-radius:10px;padding:16px 20px;margin:6px 0;}}
.cross-title{{font-size:0.78rem;font-weight:700;color:{ACC};margin-bottom:4px;}}
.cross-body{{font-size:0.82rem;color:{MID};line-height:1.6;}}

.qa-box{{background:{CARD};border:1px solid {BDR};border-radius:10px;padding:20px 22px;margin-top:8px;}}
.qa-answer{{background:#F7FAFC;border-radius:8px;padding:16px 18px;margin-top:12px;font-size:0.875rem;line-height:1.8;color:{MID};}}

.forecast-badge{{display:inline-block;background:rgba(27,108,168,0.1);color:{ACC};border-radius:4px;padding:2px 8px;font-size:0.65rem;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;margin-left:8px;}}

.compare-header{{background:linear-gradient(135deg,{ACC},#0D4F8B);color:white;border-radius:10px;padding:16px 20px;margin-bottom:16px;}}

.sl{{font-size:0.68rem;font-weight:700;color:{LITE};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;}}
.dv{{border:none;border-top:1px solid {BDR};margin:1.5rem 0 1.2rem;}}

.stButton>button{{
  background:{ACC}!important;color:#fff!important;border:none!important;
  border-radius:6px!important;padding:9px 24px!important;
  font-size:0.8rem!important;font-weight:600!important;
  font-family:'Inter',sans-serif!important;letter-spacing:0.03em!important;
}}
.stButton>button:hover{{background:{ACC2}!important;}}

.stTextInput>div>div>input{{border-radius:8px!important;border:1px solid {BDR}!important;}}
.stTextArea>div>div>textarea{{border-radius:8px!important;border:1px solid {BDR}!important;}}
.stMultiSelect label,.stSelectbox label,.stFileUploader label,.stTextInput label,.stTextArea label{{
  font-size:0.68rem!important;font-weight:700!important;color:{LITE}!important;
  text-transform:uppercase!important;letter-spacing:0.08em!important;
}}

#MainMenu,footer,header{{visibility:hidden;}}
.stDeployButton{{display:none;}}
</style>
""", unsafe_allow_html=True)

# ── CHART HELPER ─────────────────────────────────────────────────
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

BLUE_SCALE  = [[0,"#BDD5EA"],[1,ACC]]
BLUE_SCALE2 = [[0,"#BDD5EA"],[1,ACC2]]
RED_SCALE   = [[0,"#F5C6CB"],[1,DANGER]]
GREEN_SCALE = [[0,"#C6F6D5"],[1,SUCCESS]]

# ── DATA ─────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    s = pd.read_csv('data/sales_data.csv',      parse_dates=['date'])
    m = pd.read_csv('data/marketing_data.csv',  parse_dates=['date'])
    f = pd.read_csv('data/finance_data.csv',    parse_dates=['date'])
    h = pd.read_csv('data/healthcare_data.csv', parse_dates=['admission_date'])
    return s, m, f, h

sales_df, mkt_df, fin_df, hc_df = load_data()

# ── GEMINI CALL ───────────────────────────────────────────────────
def gemini(prompt, max_tokens=1500):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error: {e}"

# ── FEATURE 1: CONVERSATIONAL Q&A ────────────────────────────────
def answer_question(question, domain_data_summary):
    prompt = f"""You are a senior data analyst for Drishti Analytics. Answer the following question using the data provided.

Data Summary:
{domain_data_summary}

Question: {question}

Give a direct, specific, data-driven answer in 2-4 sentences. Include specific numbers from the data. Be conversational but precise. No markdown formatting."""
    return gemini(prompt)

# ── FEATURE 2: EXECUTIVE SUMMARY ─────────────────────────────────
def generate_executive_summary(sales_summary, mkt_summary, fin_summary, hc_summary):
    prompt = f"""You are a Chief Analytics Officer preparing a board-level executive summary.

Sales Data: {sales_summary}
Marketing Data: {mkt_summary}
Finance Data: {fin_summary}
Healthcare Data: {hc_summary}

Write a professional executive summary with these exact sections:
EXECUTIVE SUMMARY
Period: [current period]

PERFORMANCE OVERVIEW
[2-3 sentences on overall business health]

KEY WINS
1. [specific win with numbers]
2. [specific win with numbers]
3. [specific win with numbers]

CRITICAL CONCERNS
1. [specific concern with numbers]
2. [specific concern with numbers]

STRATEGIC RECOMMENDATIONS
1. [specific action]
2. [specific action]
3. [specific action]

CROSS-DOMAIN INSIGHT
[1-2 sentences on patterns connecting Sales, Marketing, Finance, and Healthcare]

Be specific with numbers. Professional tone. No markdown symbols."""
    return gemini(prompt, max_tokens=2000)

# ── FEATURE 3: ANOMALY DETECTION ─────────────────────────────────
def detect_anomalies(df, value_col, group_col=None, domain=""):
    prompt = f"""You are a data anomaly detection system. Analyze this data and find unusual patterns.

Domain: {domain}
Data statistics:
{df[value_col].describe().to_string()}

{"Group breakdown:\n" + df.groupby(group_col)[value_col].mean().to_string() if group_col and group_col in df.columns else ""}

Identify exactly 3 anomalies or unusual patterns. For each respond in this exact format:
ANOMALY: [short title]
DETAIL: [specific finding with numbers]
SEVERITY: [High/Medium/Low]
---
No other text."""
    return gemini(prompt)

def parse_anomalies(text):
    anomalies = []
    blocks = text.strip().split('---')
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        a = {}
        for line in block.split('\n'):
            if line.startswith('ANOMALY:'):
                a['title'] = line.replace('ANOMALY:', '').strip()
            elif line.startswith('DETAIL:'):
                a['detail'] = line.replace('DETAIL:', '').strip()
            elif line.startswith('SEVERITY:'):
                a['severity'] = line.replace('SEVERITY:', '').strip()
        if 'title' in a:
            anomalies.append(a)
    return anomalies

# ── FEATURE 4: PREDICTIVE FORECASTING ────────────────────────────
def generate_forecast(df, date_col, value_col, periods=3):
    """Simple linear trend forecast"""
    df_copy = df.copy()
    df_copy['month'] = pd.to_datetime(df_copy[date_col]).dt.to_period('M')
    monthly = df_copy.groupby('month')[value_col].sum().reset_index()
    monthly['month_num'] = range(len(monthly))

    if len(monthly) < 3:
        return None, None

    # Linear regression
    x = monthly['month_num'].values
    y = monthly[value_col].values
    coeffs = np.polyfit(x, y, 1)
    slope, intercept = coeffs

    # Generate future months
    last_month = monthly['month'].iloc[-1]
    future_months = []
    future_vals = []
    for i in range(1, periods + 1):
        future_num = len(monthly) + i - 1
        predicted = slope * future_num + intercept
        future_months.append(str(last_month + i))
        future_vals.append(max(0, predicted))

    return future_months, future_vals, slope, monthly

# ── FEATURE 5: NATURAL LANGUAGE FILTER ───────────────────────────
def parse_nl_filter(query, df, domain):
    cols = list(df.columns)
    sample = df.head(3).to_dict('records')
    prompt = f"""You are a data filter parser. Convert the natural language query into filter conditions.

Available columns: {cols}
Sample data: {sample}
Domain: {domain}
Query: "{query}"

Respond ONLY with a valid Python dictionary like this (no other text):
{{"column": "region", "value": "West", "operator": "equals"}}

Or for date ranges:
{{"column": "date", "start": "2022-01-01", "end": "2022-06-30", "operator": "between"}}

Or for numeric:
{{"column": "revenue", "value": 50000, "operator": "greater_than"}}

If you cannot parse it, return: {{"error": "cannot parse"}}"""
    result = gemini(prompt, max_tokens=200)
    try:
        result = result.strip()
        if result.startswith('```'):
            result = re.sub(r'```[a-z]*\n?', '', result).strip()
        return json.loads(result)
    except:
        return {"error": "cannot parse"}

def apply_nl_filter(df, filter_dict):
    if "error" in filter_dict:
        return df, False
    try:
        col = filter_dict.get("column")
        op  = filter_dict.get("operator", "equals")
        if col not in df.columns:
            return df, False
        if op == "equals":
            val = filter_dict.get("value")
            return df[df[col].astype(str).str.lower() == str(val).lower()], True
        elif op == "between" and "start" in filter_dict:
            return df[(df[col] >= filter_dict["start"]) & (df[col] <= filter_dict["end"])], True
        elif op == "greater_than":
            return df[df[col] > float(filter_dict.get("value", 0))], True
        elif op == "less_than":
            return df[df[col] < float(filter_dict.get("value", 0))], True
        elif op == "contains":
            return df[df[col].astype(str).str.contains(str(filter_dict.get("value","")), case=False)], True
        return df, False
    except:
        return df, False

# ── FEATURE 6: COMPARISON MODE ───────────────────────────────────
def compare_periods(df, date_col, value_col, period1_label, period2_label, period1_data, period2_data):
    prompt = f"""You are a business analyst comparing two time periods.

Period 1 ({period1_label}):
- Total {value_col}: {period1_data[value_col].sum():,.0f}
- Average {value_col}: {period1_data[value_col].mean():,.0f}
- Records: {len(period1_data)}

Period 2 ({period2_label}):
- Total {value_col}: {period2_data[value_col].sum():,.0f}
- Average {value_col}: {period2_data[value_col].mean():,.0f}
- Records: {len(period2_data)}

Change: {((period2_data[value_col].sum() - period1_data[value_col].sum()) / max(period1_data[value_col].sum(), 1) * 100):.1f}%

Write a 3-sentence AI-narrated comparison. Be specific with percentages and numbers. Mention what drove the change and what to watch for. No markdown."""
    return gemini(prompt, max_tokens=300)

# ── FEATURE 7: CROSS-DOMAIN INSIGHTS ─────────────────────────────
def cross_domain_insights(sales_df, mkt_df, fin_df, hc_df):
    # Build monthly aggregates for correlation analysis
    s_monthly = sales_df.groupby(sales_df['date'].dt.to_period('M').astype(str))['revenue'].sum()
    m_monthly = mkt_df.groupby(mkt_df['date'].dt.to_period('M').astype(str))['spend'].sum()
    f_monthly = fin_df.groupby(fin_df.get('date', fin_df.index).astype(str) if 'date' not in fin_df.columns else fin_df['date'].astype(str))['actual_spend'].sum() if 'date' in fin_df.columns else pd.Series(dtype=float)
    h_monthly = hc_df.groupby(hc_df['admission_date'].dt.to_period('M').astype(str))['treatment_cost'].sum()

    prompt = f"""You are Drishti's cross-domain AI analyst. Analyze these multi-domain statistics and find hidden correlations.

Sales monthly revenue (sample): {s_monthly.tail(6).to_dict()}
Marketing monthly spend (sample): {m_monthly.tail(6).to_dict()}
Healthcare monthly treatment costs (sample): {h_monthly.tail(6).to_dict()}

Sales total: ${sales_df['revenue'].sum():,.0f}
Marketing avg ROI: {mkt_df['roi'].mean():.2f}x
Finance over-budget rate: {fin_df['over_budget'].mean()*100:.1f}%
Healthcare readmission rate: {hc_df['readmitted'].mean()*100:.1f}%
Healthcare avg satisfaction: {hc_df['satisfaction_score'].mean():.1f}/10

Find 3 cross-domain correlations or insights that connect multiple domains. Format exactly as:
INSIGHT: [title connecting 2+ domains]
FINDING: [specific data-backed finding]
ACTION: [recommended action]
---
Be specific with numbers. Focus on surprising or non-obvious connections."""
    return gemini(prompt, max_tokens=600)

def parse_cross_insights(text):
    insights = []
    blocks = text.strip().split('---')
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        ins = {}
        for line in block.split('\n'):
            if line.startswith('INSIGHT:'):
                ins['title'] = line.replace('INSIGHT:', '').strip()
            elif line.startswith('FINDING:'):
                ins['finding'] = line.replace('FINDING:', '').strip()
            elif line.startswith('ACTION:'):
                ins['action'] = line.replace('ACTION:', '').strip()
        if 'title' in ins:
            insights.append(ins)
    return insights

# ── FEATURE 8: BENCHMARK MODE ────────────────────────────────────
def benchmark_analysis(uploaded_df, reference_domain, reference_df, key_col):
    if key_col not in uploaded_df.columns or key_col not in reference_df.columns:
        return "Cannot benchmark: key column not found in both datasets."
    
    uploaded_stats = uploaded_df[key_col].describe()
    reference_stats = reference_df[key_col].describe()
    
    prompt = f"""You are a benchmarking analyst. Compare uploaded data against Drishti's industry reference dataset.

Uploaded dataset ({key_col}):
{uploaded_stats.to_string()}

Industry reference ({reference_domain} - {key_col}):
{reference_stats.to_string()}

Write a benchmark report with:
BENCHMARK SCORE: [X/10 with brief explanation]
ABOVE AVERAGE: [what performs better than reference]
BELOW AVERAGE: [what underperforms vs reference]  
PERCENTILE: [estimated percentile vs industry]
TOP RECOMMENDATION: [single most impactful action]

Be specific with numbers. Professional tone."""
    return gemini(prompt, max_tokens=400)

# ── STANDARD AI SECTION ──────────────────────────────────────────
def ai_section(key, summary, domain):
    st.markdown("<hr class='dv'>", unsafe_allow_html=True)
    st.markdown("<div class='sl'>AI-Generated Analysis</div>", unsafe_allow_html=True)
    if st.button("Generate Insights", key=key):
        with st.spinner("Analyzing..."):
            prompt = f"""You are a senior business analyst reviewing {domain} data.

{summary}

Write exactly:
Insight 1: [specific finding]
Insight 2: [specific finding]
Insight 3: [specific finding]

Risk 1: [specific risk]
Risk 2: [specific risk]

Recommendation 1: [specific action]
Recommendation 2: [specific action]

Be concise, professional, data-driven. No markdown, no dashes."""
            result = gemini(prompt)
        st.markdown(f'<div class="ai">{result}</div>', unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='padding:28px 20px 16px;'>
      <div style='font-size:1.1rem;font-weight:800;color:#F0F4F8;letter-spacing:-0.02em;'>Drishti</div>
      <div style='font-size:0.65rem;color:#4A5568;text-transform:uppercase;letter-spacing:0.1em;margin-top:2px;'>Analytics Platform</div>
    </div>
    <div style='height:1px;background:rgba(255,255,255,0.07);margin:0 20px 8px;'></div>
    <div style='padding:8px 20px 4px;font-size:0.62rem;font-weight:700;color:#2D3748;text-transform:uppercase;letter-spacing:0.12em;'>Dashboards</div>
    """, unsafe_allow_html=True)

    page = st.radio("Navigation", [
        "Overview", "Sales", "Marketing", "Finance", "Healthcare"
    ], label_visibility="collapsed")

    st.markdown(f"""
    <div style='height:1px;background:rgba(255,255,255,0.07);margin:8px 20px;'></div>
    <div style='padding:8px 20px 4px;font-size:0.62rem;font-weight:700;color:#2D3748;text-transform:uppercase;letter-spacing:0.12em;'>AI Tools</div>
    """, unsafe_allow_html=True)

    page2 = st.radio("AI Tools", [
        "Ask Drishti", "Executive Summary", "Cross-Domain Insights", "New Dataset"
    ], label_visibility="collapsed")

    st.markdown(f"""
    <div style='height:1px;background:rgba(255,255,255,0.07);margin:8px 20px;'></div>
    <div style='padding:8px 20px 24px;font-size:0.7rem;color:#4A5568;line-height:1.7;'>
      Jan 2022 – Dec 2023<br>11,000+ records · 4 domains
    </div>
    """, unsafe_allow_html=True)

if "active" not in st.session_state:
    st.session_state.active = "Overview"

if st.session_state.get("last_page") != page:
    st.session_state.active = page
    st.session_state.last_page = page
elif st.session_state.get("last_page2") != page2:
    st.session_state.active = page2
    st.session_state.last_page2 = page2

active = st.session_state.active


# ════════════════════════════════════════════════════════════════
# OVERVIEW
# ════════════════════════════════════════════════════════════════
if active == "Overview":
    st.markdown("<div class='ph'><p class='pt'>Business Overview</p><p class='ps'>Cross-domain performance summary — Sales, Marketing, Finance & Healthcare</p></div>", unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Total Revenue",      f"${sales_df['revenue'].sum()/1e6:.2f}M")
    with c2: st.metric("Avg Marketing ROI",  f"{mkt_df['roi'].mean():.2f}x")
    with c3:
        v = fin_df['variance'].mean()
        st.metric("Budget Variance", f"${abs(v):,.0f}", "Under" if v > 0 else "Over")
    with c4: st.metric("Avg Treatment Cost", f"${hc_df['treatment_cost'].mean():,.0f}")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("<div class='cc'><div class='ct'>Monthly Revenue Trend</div>", unsafe_allow_html=True)
        m = sales_df.groupby(sales_df['date'].dt.to_period('M').astype(str))['revenue'].sum().reset_index()
        m.columns = ['month','revenue']
        fig = px.area(m, x='month', y='revenue', color_discrete_sequence=[ACC], labels={'revenue':'Revenue ($)','month':''})
        fig.update_traces(fillcolor="rgba(27,108,168,0.1)", line_color=ACC)
        st.plotly_chart(fig_clean(fig), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='cc'><div class='ct'>Campaign ROI by Type</div>", unsafe_allow_html=True)
        r = mkt_df.groupby('campaign_type')['roi'].mean().sort_values(ascending=True).reset_index()
        fig = px.bar(r, x='roi', y='campaign_type', orientation='h', color='roi', color_continuous_scale=BLUE_SCALE, labels={'roi':'Avg ROI','campaign_type':''})
        st.plotly_chart(fig_clean(fig), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    c3,c4 = st.columns(2)
    with c3:
        st.markdown("<div class='cc'><div class='ct'>Budget vs Actual by Department</div>", unsafe_allow_html=True)
        d = fin_df.groupby('department')[['budget','actual_spend']].sum().reset_index()
        fig = px.bar(d, x='department', y=['budget','actual_spend'], barmode='group',
                     color_discrete_map={'budget':ACC,'actual_spend':ACC2}, labels={'value':'($)','department':'','variable':''})
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


# ════════════════════════════════════════════════════════════════
# SALES
# ════════════════════════════════════════════════════════════════
elif active == "Sales":
    st.markdown("<div class='ph'><p class='pt'>Sales Analytics</p><p class='ps'>Revenue, profitability, and channel performance</p></div>", unsafe_allow_html=True)

    # ── FEATURE 5: Natural Language Filter ──
    st.markdown("<div class='cc'>", unsafe_allow_html=True)
    st.markdown("<div class='ct'>Natural Language Filter</div>", unsafe_allow_html=True)
    nl_col1, nl_col2 = st.columns([4,1])
    with nl_col1:
        nl_query = st.text_input("Filter data in plain English", placeholder='e.g. "show only West region" or "revenue above 5000"', label_visibility="collapsed")
    with nl_col2:
        nl_apply = st.button("Apply Filter", key="sales_nl")
    st.markdown("</div>", unsafe_allow_html=True)

    # Standard filters
    c1,c2 = st.columns(2)
    with c1: reg = st.multiselect("Region", sales_df['region'].unique(), default=list(sales_df['region'].unique()))
    with c2: ch  = st.multiselect("Channel", sales_df['channel'].unique(), default=list(sales_df['channel'].unique()))
    df = sales_df[sales_df['region'].isin(reg) & sales_df['channel'].isin(ch)]

    # Apply NL filter on top
    if nl_apply and nl_query:
        filter_dict = parse_nl_filter(nl_query, df, "Sales")
        df, applied = apply_nl_filter(df, filter_dict)
        if applied:
            st.success(f"Filter applied: {filter_dict}")
        else:
            st.warning("Could not parse filter. Showing unfiltered data.")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Total Revenue", f"${df['revenue'].sum()/1e6:.2f}M")
    with c2: st.metric("Total Profit",  f"${df['profit'].sum()/1e6:.2f}M")
    with c3: st.metric("Avg Discount",  f"{df['discount_pct'].mean()*100:.1f}%")
    with c4: st.metric("Return Rate",   f"{df['returned'].mean()*100:.1f}%")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── FEATURE 7: Comparison Mode ──
    with st.expander("📊 Comparison Mode — Compare Two Time Periods"):
        comp_col1, comp_col2 = st.columns(2)
        with comp_col1:
            years = sorted(df['date'].dt.year.unique())
            p1_year = st.selectbox("Period 1 Year", years, key="s_p1")
        with comp_col2:
            p2_year = st.selectbox("Period 2 Year", years, index=min(1, len(years)-1), key="s_p2")

        if st.button("Compare Periods", key="s_compare"):
            p1_data = df[df['date'].dt.year == p1_year]
            p2_data = df[df['date'].dt.year == p2_year]
            if len(p1_data) > 0 and len(p2_data) > 0:
                cc1, cc2 = st.columns(2)
                with cc1:
                    st.metric(f"{p1_year} Revenue", f"${p1_data['revenue'].sum()/1e6:.2f}M")
                with cc2:
                    delta = (p2_data['revenue'].sum() - p1_data['revenue'].sum()) / p1_data['revenue'].sum() * 100
                    st.metric(f"{p2_year} Revenue", f"${p2_data['revenue'].sum()/1e6:.2f}M", f"{delta:+.1f}%")

                with st.spinner("Generating AI comparison narrative..."):
                    narrative = compare_periods(df, 'date', 'revenue', str(p1_year), str(p2_year), p1_data, p2_data)
                st.markdown(f'<div class="ai">{narrative}</div>', unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown("<div class='cc'><div class='ct'>Monthly Revenue</div>", unsafe_allow_html=True)
        m = df.groupby(df['date'].dt.to_period('M').astype(str))['revenue'].sum().reset_index()
        m.columns = ['month','revenue']

        # ── FEATURE 4: Forecast overlay ──
        result = generate_forecast(df, 'date', 'revenue', periods=3)
        if result and result[0]:
            future_months, future_vals, slope, monthly_hist = result
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=m['month'], y=m['revenue'], name='Actual', line=dict(color=ACC, width=2.5)))
            fig.add_trace(go.Scatter(
                x=future_months, y=future_vals, name='Forecast',
                line=dict(color=WARN, width=2, dash='dot'),
                mode='lines+markers', marker=dict(size=6, color=WARN)
            ))
        else:
            fig = px.line(m, x='month', y='revenue', color_discrete_sequence=[ACC])
            fig.update_traces(line_width=2.5)

        st.plotly_chart(fig_clean(fig), use_container_width=True)
        st.markdown('<span class="forecast-badge">3-Month Forecast Shown</span>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='cc'><div class='ct'>Revenue by Product</div>", unsafe_allow_html=True)
        p = df.groupby('product')['revenue'].sum().sort_values().reset_index()
        fig = px.bar(p, x='revenue', y='product', orientation='h', color='revenue', color_continuous_scale=BLUE_SCALE, labels={'revenue':'Revenue ($)','product':''})
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
        st.markdown("<div class='cc'><div class='ct'>Revenue by Sales Channel</div>", unsafe_allow_html=True)
        cv = df.groupby('channel')['revenue'].sum().reset_index()
        fig = px.pie(cv, names='channel', values='revenue', color_discrete_sequence=CSEQ, hole=0.52)
        fig.update_traces(textposition='outside', textfont_size=10)
        st.plotly_chart(fig_clean(fig, h=290), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── FEATURE 3: Anomaly Detection ──
    st.markdown("<hr class='dv'>", unsafe_allow_html=True)
    st.markdown("<div class='sl'>Anomaly Detection</div>", unsafe_allow_html=True)
    if st.button("Scan for Anomalies", key="s_anomaly"):
        with st.spinner("Scanning data for unusual patterns..."):
            raw = detect_anomalies(df, 'revenue', 'region', 'Sales')
            anomalies = parse_anomalies(raw)
        for a in anomalies:
            color = DANGER if a.get('severity','').lower() == 'high' else (WARN if a.get('severity','').lower() == 'medium' else SUCCESS)
            st.markdown(f"""<div class='anomaly-card'>
                <div class='anomaly-title'>⚠ {a.get('title','')} — {a.get('severity','')}</div>
                <div class='anomaly-body'>{a.get('detail','')}</div>
            </div>""", unsafe_allow_html=True)

    ai_section("s_ai", f"""Total Revenue: ${df['revenue'].sum():,.0f}
Total Profit: ${df['profit'].sum():,.0f}
Profit Margin: {(df['profit'].sum()/df['revenue'].sum()*100):.1f}%
Avg Discount: {df['discount_pct'].mean()*100:.1f}%
Return Rate: {df['returned'].mean()*100:.1f}%
Top Region: {df.groupby('region')['revenue'].sum().idxmax()}
Top Product: {df.groupby('product')['revenue'].sum().idxmax()}
Best Channel: {df.groupby('channel')['revenue'].sum().idxmax()}""", "Sales")


# ════════════════════════════════════════════════════════════════
# MARKETING
# ════════════════════════════════════════════════════════════════
elif active == "Marketing":
    st.markdown("<div class='ph'><p class='pt'>Marketing Analytics</p><p class='ps'>Campaign performance, ROI, and conversion analysis</p></div>", unsafe_allow_html=True)

    # NL Filter
    st.markdown("<div class='cc'>", unsafe_allow_html=True)
    st.markdown("<div class='ct'>Natural Language Filter</div>", unsafe_allow_html=True)
    nl_col1, nl_col2 = st.columns([4,1])
    with nl_col1:
        nl_query_m = st.text_input("Filter data in plain English", placeholder='e.g. "show only Social Media campaigns" or "ROI above 8"', label_visibility="collapsed", key="m_nl_input")
    with nl_col2:
        nl_apply_m = st.button("Apply Filter", key="mkt_nl")
    st.markdown("</div>", unsafe_allow_html=True)

    cf = st.multiselect("Campaign Type", mkt_df['campaign_type'].unique(), default=list(mkt_df['campaign_type'].unique()))
    df = mkt_df[mkt_df['campaign_type'].isin(cf)]

    if nl_apply_m and nl_query_m:
        filter_dict = parse_nl_filter(nl_query_m, df, "Marketing")
        df, applied = apply_nl_filter(df, filter_dict)
        if applied:
            st.success(f"Filter applied: {filter_dict}")
        else:
            st.warning("Could not parse filter. Showing unfiltered data.")

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Average ROI",         f"{df['roi'].mean():.2f}x")
    with c2: st.metric("Average CTR",         f"{df['ctr'].mean()*100:.2f}%")
    with c3: st.metric("Avg Conversion Rate", f"{df['conversion_rate'].mean()*100:.2f}%")
    with c4: st.metric("Total Spend",         f"${df['spend'].sum()/1e6:.2f}M")

    # Comparison Mode
    with st.expander("📊 Comparison Mode — Compare Two Campaign Types"):
        camp_types = list(df['campaign_type'].unique())
        if len(camp_types) >= 2:
            cc1, cc2 = st.columns(2)
            with cc1: ct1 = st.selectbox("Campaign A", camp_types, key="m_ct1")
            with cc2: ct2 = st.selectbox("Campaign B", camp_types, index=1, key="m_ct2")
            if st.button("Compare Campaigns", key="m_compare"):
                d1 = df[df['campaign_type'] == ct1]
                d2 = df[df['campaign_type'] == ct2]
                mc1, mc2 = st.columns(2)
                with mc1:
                    st.metric(f"{ct1} ROI", f"{d1['roi'].mean():.2f}x")
                    st.metric(f"{ct1} Conv. Rate", f"{d1['conversion_rate'].mean()*100:.2f}%")
                with mc2:
                    st.metric(f"{ct2} ROI", f"{d2['roi'].mean():.2f}x")
                    st.metric(f"{ct2} Conv. Rate", f"{d2['conversion_rate'].mean()*100:.2f}%")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
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

    st.markdown("<div class='cc'><div class='ct'>Marketing Spend vs Revenue Generated</div>", unsafe_allow_html=True)
    fig = px.scatter(df, x='spend', y='revenue_generated', color='campaign_type', size='conversions',
                     color_discrete_sequence=CSEQ, opacity=0.72)
    st.plotly_chart(fig_clean(fig, h=360), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Anomaly Detection
    st.markdown("<hr class='dv'>", unsafe_allow_html=True)
    st.markdown("<div class='sl'>Anomaly Detection</div>", unsafe_allow_html=True)
    if st.button("Scan for Anomalies", key="m_anomaly"):
        with st.spinner("Scanning..."):
            raw = detect_anomalies(df, 'roi', 'campaign_type', 'Marketing')
            anomalies = parse_anomalies(raw)
        for a in anomalies:
            st.markdown(f"""<div class='anomaly-card'>
                <div class='anomaly-title'>⚠ {a.get('title','')} — {a.get('severity','')}</div>
                <div class='anomaly-body'>{a.get('detail','')}</div>
            </div>""", unsafe_allow_html=True)

    ai_section("m_ai", f"""Total Campaigns: {len(df):,}
Avg ROI: {df['roi'].mean():.2f}x
Best Campaign: {df.groupby('campaign_type')['roi'].mean().idxmax()}
Worst Campaign: {df.groupby('campaign_type')['roi'].mean().idxmin()}
Avg CTR: {df['ctr'].mean()*100:.2f}%
Avg Conversion Rate: {df['conversion_rate'].mean()*100:.2f}%
Total Spend: ${df['spend'].sum():,.0f}
Total Revenue: ${df['revenue_generated'].sum():,.0f}
Best Segment: {df.groupby('customer_segment')['conversion_rate'].mean().idxmax()}""", "Marketing")


# ════════════════════════════════════════════════════════════════
# FINANCE
# ════════════════════════════════════════════════════════════════
elif active == "Finance":
    st.markdown("<div class='ph'><p class='pt'>Finance Analytics</p><p class='ps'>Budget performance, variance tracking, and expense analysis</p></div>", unsafe_allow_html=True)

    yr = st.selectbox("Fiscal Year", ['All'] + sorted(fin_df['year'].unique().tolist()))
    df = fin_df if yr == 'All' else fin_df[fin_df['year'] == int(yr)]

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Total Budget",       f"${df['budget'].sum()/1e6:.2f}M")
    with c2: st.metric("Total Actual Spend", f"${df['actual_spend'].sum()/1e6:.2f}M")
    with c3: st.metric("Over-Budget Rate",   f"{df['over_budget'].mean()*100:.1f}%")
    with c4: st.metric("Avg Variance",       f"${df['variance'].mean():,.0f}")

    # Comparison Mode
    with st.expander("📊 Comparison Mode — Compare Departments"):
        depts = list(df['department'].unique())
        if len(depts) >= 2:
            fc1, fc2 = st.columns(2)
            with fc1: fd1 = st.selectbox("Department A", depts, key="f_d1")
            with fc2: fd2 = st.selectbox("Department B", depts, index=1, key="f_d2")
            if st.button("Compare Departments", key="f_compare"):
                d1 = df[df['department'] == fd1]
                d2 = df[df['department'] == fd2]
                fc1m, fc2m = st.columns(2)
                with fc1m:
                    st.metric(f"{fd1} Budget", f"${d1['budget'].sum():,.0f}")
                    st.metric(f"{fd1} Over-Budget", f"{d1['over_budget'].mean()*100:.1f}%")
                with fc2m:
                    st.metric(f"{fd2} Budget", f"${d2['budget'].sum():,.0f}")
                    st.metric(f"{fd2} Over-Budget", f"{d2['over_budget'].mean()*100:.1f}%")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("<div class='cc'><div class='ct'>Budget vs Actual by Department</div>", unsafe_allow_html=True)
        d = df.groupby('department')[['budget','actual_spend']].sum().reset_index()
        fig = px.bar(d, x='department', y=['budget','actual_spend'], barmode='group',
                     color_discrete_map={'budget':ACC,'actual_spend':ACC2})
        st.plotly_chart(fig_clean(fig), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='cc'><div class='ct'>Over-Budget Rate by Department (%)</div>", unsafe_allow_html=True)
        o = df.groupby('department')['over_budget'].mean().reset_index()
        o['pct'] = (o['over_budget'] * 100).round(1)
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

    # Anomaly Detection
    st.markdown("<hr class='dv'>", unsafe_allow_html=True)
    st.markdown("<div class='sl'>Anomaly Detection</div>", unsafe_allow_html=True)
    if st.button("Scan for Anomalies", key="f_anomaly"):
        with st.spinner("Scanning..."):
            raw = detect_anomalies(df, 'actual_spend', 'department', 'Finance')
            anomalies = parse_anomalies(raw)
        for a in anomalies:
            st.markdown(f"""<div class='anomaly-card'>
                <div class='anomaly-title'>⚠ {a.get('title','')} — {a.get('severity','')}</div>
                <div class='anomaly-body'>{a.get('detail','')}</div>
            </div>""", unsafe_allow_html=True)

    ai_section("f_ai", f"""Total Budget: ${df['budget'].sum():,.0f}
Total Actual Spend: ${df['actual_spend'].sum():,.0f}
Overall Variance: ${df['variance'].sum():,.0f}
Over-Budget Rate: {df['over_budget'].mean()*100:.1f}%
Most Overspent Dept: {df.groupby('department')['actual_spend'].sum().idxmax()}
Most Under-Budget Dept: {df.groupby('department')['variance'].sum().idxmax()}
Highest Expense Category: {df.groupby('expense_category')['actual_spend'].sum().idxmax()}""", "Finance")


# ════════════════════════════════════════════════════════════════
# HEALTHCARE
# ════════════════════════════════════════════════════════════════
elif active == "Healthcare":
    st.markdown("<div class='ph'><p class='pt'>Healthcare Analytics</p><p class='ps'>Patient outcomes, treatment costs, and departmental performance</p></div>", unsafe_allow_html=True)

    # NL Filter
    st.markdown("<div class='cc'>", unsafe_allow_html=True)
    st.markdown("<div class='ct'>Natural Language Filter</div>", unsafe_allow_html=True)
    nl_col1, nl_col2 = st.columns([4,1])
    with nl_col1:
        nl_query_h = st.text_input("Filter data in plain English", placeholder='e.g. "show only Cardiology" or "treatment cost above 10000"', label_visibility="collapsed", key="h_nl_input")
    with nl_col2:
        nl_apply_h = st.button("Apply Filter", key="hc_nl")
    st.markdown("</div>", unsafe_allow_html=True)

    dpf = st.multiselect("Department", hc_df['department'].unique(), default=list(hc_df['department'].unique()))
    df  = hc_df[hc_df['department'].isin(dpf)]

    if nl_apply_h and nl_query_h:
        filter_dict = parse_nl_filter(nl_query_h, df, "Healthcare")
        df, applied = apply_nl_filter(df, filter_dict)
        if applied:
            st.success(f"Filter applied: {filter_dict}")
        else:
            st.warning("Could not parse filter.")

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Total Patients",     f"{len(df):,}")
    with c2: st.metric("Avg Treatment Cost", f"${df['treatment_cost'].mean():,.0f}")
    with c3: st.metric("Readmission Rate",   f"{df['readmitted'].mean()*100:.1f}%")
    with c4: st.metric("Avg Stay",           f"{df['length_of_stay'].mean():.1f} days")

    # Comparison Mode
    with st.expander("📊 Comparison Mode — Compare Insurance Types"):
        ins_types = list(df['insurance_type'].unique())
        if len(ins_types) >= 2:
            hc1, hc2 = st.columns(2)
            with hc1: hi1 = st.selectbox("Insurance A", ins_types, key="h_i1")
            with hc2: hi2 = st.selectbox("Insurance B", ins_types, index=1, key="h_i2")
            if st.button("Compare", key="h_compare"):
                hd1 = df[df['insurance_type'] == hi1]
                hd2 = df[df['insurance_type'] == hi2]
                hm1, hm2 = st.columns(2)
                with hm1:
                    st.metric(f"{hi1} Avg Cost", f"${hd1['treatment_cost'].mean():,.0f}")
                    st.metric(f"{hi1} Readmit", f"{hd1['readmitted'].mean()*100:.1f}%")
                with hm2:
                    st.metric(f"{hi2} Avg Cost", f"${hd2['treatment_cost'].mean():,.0f}")
                    st.metric(f"{hi2} Readmit", f"{hd2['readmitted'].mean()*100:.1f}%")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("<div class='cc'><div class='ct'>Admissions by Department</div>", unsafe_allow_html=True)
        a = df['department'].value_counts().reset_index()
        a.columns = ['dept','count']
        fig = px.bar(a, x='dept', y='count', color='count', color_continuous_scale=BLUE_SCALE)
        st.plotly_chart(fig_clean(fig), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='cc'><div class='ct'>Most Common Diagnoses</div>", unsafe_allow_html=True)
        d = df['diagnosis'].value_counts().reset_index()
        d.columns = ['diagnosis','count']
        fig = px.bar(d, x='count', y='diagnosis', orientation='h', color='count', color_continuous_scale=RED_SCALE)
        st.plotly_chart(fig_clean(fig), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    c3,c4 = st.columns(2)
    with c3:
        st.markdown("<div class='cc'><div class='ct'>Avg Treatment Cost by Age Group</div>", unsafe_allow_html=True)
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

    st.markdown("<div class='cc'><div class='ct'>Length of Stay vs Treatment Cost</div>", unsafe_allow_html=True)
    fig = px.scatter(df.sample(min(800,len(df))), x='length_of_stay', y='treatment_cost', color='department',
                     size='num_procedures', color_discrete_sequence=CSEQ, opacity=0.65)
    st.plotly_chart(fig_clean(fig, h=360), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Anomaly Detection
    st.markdown("<hr class='dv'>", unsafe_allow_html=True)
    st.markdown("<div class='sl'>Anomaly Detection</div>", unsafe_allow_html=True)
    if st.button("Scan for Anomalies", key="h_anomaly"):
        with st.spinner("Scanning..."):
            raw = detect_anomalies(df, 'treatment_cost', 'department', 'Healthcare')
            anomalies = parse_anomalies(raw)
        for a in anomalies:
            st.markdown(f"""<div class='anomaly-card'>
                <div class='anomaly-title'>⚠ {a.get('title','')} — {a.get('severity','')}</div>
                <div class='anomaly-body'>{a.get('detail','')}</div>
            </div>""", unsafe_allow_html=True)

    ai_section("h_ai", f"""Total Patients: {len(df):,}
Avg Treatment Cost: ${df['treatment_cost'].mean():,.0f}
Most Expensive Dept: {df.groupby('department')['treatment_cost'].mean().idxmax()}
Readmission Rate: {df['readmitted'].mean()*100:.1f}%
Most Common Diagnosis: {df['diagnosis'].value_counts().idxmax()}
Avg Length of Stay: {df['length_of_stay'].mean():.1f} days
Avg Satisfaction Score: {df['satisfaction_score'].mean():.1f}/10
Uninsured Rate: {(df['insurance_type']=='Uninsured').mean()*100:.1f}%""", "Healthcare")


# ════════════════════════════════════════════════════════════════
# FEATURE 1: ASK DRISHTI — Conversational Q&A
# ════════════════════════════════════════════════════════════════
elif active == "Ask Drishti":
    st.markdown("<div class='ph'><p class='pt'>Ask Drishti</p><p class='ps'>Ask any question about your data in plain English — powered by Google Gemini</p></div>", unsafe_allow_html=True)

    # Domain selector
    domain_choice = st.selectbox("Which domain do you want to ask about?",
        ["All Domains", "Sales", "Marketing", "Finance", "Healthcare"])

    # Suggested questions
    st.markdown("<div class='sl'>Suggested Questions</div>", unsafe_allow_html=True)
    suggestions = {
        "Sales": ["Which region had the highest revenue?", "What is the best performing product?", "Which channel has the lowest return rate?"],
        "Marketing": ["Which campaign type has the best ROI?", "Which customer segment converts best?", "What is our cost per conversion?"],
        "Finance": ["Which department is most over budget?", "What is our overall budget utilization?", "Which expense category is highest?"],
        "Healthcare": ["Which department has the highest readmission rate?", "What diagnosis costs the most to treat?", "How does insurance type affect costs?"],
        "All Domains": ["Which domain is performing best overall?", "Where are we losing the most money?", "What should be our top priority this quarter?"]
    }

    s_cols = st.columns(3)
    selected_suggestion = None
    for i, sug in enumerate(suggestions.get(domain_choice, [])):
        with s_cols[i % 3]:
            if st.button(sug, key=f"sug_{i}"):
                selected_suggestion = sug

    st.markdown("<div class='qa-box'>", unsafe_allow_html=True)
    question = st.text_input(
        "Your Question",
        value=selected_suggestion or "",
        placeholder="e.g. Which region had the worst Q3 performance?",
        key="qa_input"
    )

    if st.button("Ask Drishti", key="qa_submit") and question:
        # Build domain summary
        if domain_choice == "Sales" or domain_choice == "All Domains":
            s_sum = f"Sales: Revenue=${sales_df['revenue'].sum():,.0f}, Top Region={sales_df.groupby('region')['revenue'].sum().idxmax()}, Top Product={sales_df.groupby('product')['revenue'].sum().idxmax()}, Avg Margin={sales_df['profit'].sum()/sales_df['revenue'].sum()*100:.1f}%, Return Rate={sales_df['returned'].mean()*100:.1f}%"
        else:
            s_sum = ""

        if domain_choice == "Marketing" or domain_choice == "All Domains":
            m_sum = f"Marketing: Avg ROI={mkt_df['roi'].mean():.2f}x, Best Campaign={mkt_df.groupby('campaign_type')['roi'].mean().idxmax()}, Total Spend=${mkt_df['spend'].sum():,.0f}, Avg CTR={mkt_df['ctr'].mean()*100:.2f}%"
        else:
            m_sum = ""

        if domain_choice == "Finance" or domain_choice == "All Domains":
            f_sum = f"Finance: Total Budget=${fin_df['budget'].sum():,.0f}, Over-Budget Rate={fin_df['over_budget'].mean()*100:.1f}%, Most Overspent={fin_df.groupby('department')['actual_spend'].sum().idxmax()}"
        else:
            f_sum = ""

        if domain_choice == "Healthcare" or domain_choice == "All Domains":
            h_sum = f"Healthcare: Patients={len(hc_df):,}, Avg Cost=${hc_df['treatment_cost'].mean():,.0f}, Readmission={hc_df['readmitted'].mean()*100:.1f}%, Satisfaction={hc_df['satisfaction_score'].mean():.1f}/10"
        else:
            h_sum = ""

        full_summary = "\n".join(filter(None, [s_sum, m_sum, f_sum, h_sum]))

        with st.spinner("Drishti is thinking..."):
            answer = answer_question(question, full_summary)

        st.markdown(f'<div class="qa-answer">💡 {answer}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if st.button("Clear History", key="clear_chat"):
        st.session_state.chat_history = []


# ════════════════════════════════════════════════════════════════
# FEATURE 2: EXECUTIVE SUMMARY
# ════════════════════════════════════════════════════════════════
elif active == "Executive Summary":
    st.markdown("<div class='ph'><p class='pt'>Executive Summary</p><p class='ps'>AI-generated boardroom-ready summary across all four domains</p></div>", unsafe_allow_html=True)

    st.markdown("""
    <div style='background:#EBF8FF;border:1px solid #BEE3F8;border-radius:10px;padding:16px 20px;margin-bottom:20px;'>
        <div style='font-size:0.78rem;font-weight:700;color:#1B6CA8;margin-bottom:4px;'>What this does</div>
        <div style='font-size:0.82rem;color:#4A5568;'>Generates a comprehensive executive summary covering all 4 domains — Sales, Marketing, Finance, and Healthcare — with AI-identified wins, concerns, and strategic recommendations.</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Generate Executive Summary", key="exec_summary"):
        with st.spinner("Preparing boardroom-ready summary across all domains..."):
            s_sum = f"Revenue=${sales_df['revenue'].sum():,.0f}, Profit=${sales_df['profit'].sum():,.0f}, Margin={sales_df['profit'].sum()/sales_df['revenue'].sum()*100:.1f}%, Top Region={sales_df.groupby('region')['revenue'].sum().idxmax()}, Return Rate={sales_df['returned'].mean()*100:.1f}%"
            m_sum = f"Avg ROI={mkt_df['roi'].mean():.2f}x, Best Campaign={mkt_df.groupby('campaign_type')['roi'].mean().idxmax()}, Total Spend=${mkt_df['spend'].sum():,.0f}, Total Revenue Generated=${mkt_df['revenue_generated'].sum():,.0f}"
            f_sum = f"Budget=${fin_df['budget'].sum():,.0f}, Actual=${fin_df['actual_spend'].sum():,.0f}, Over-Budget Rate={fin_df['over_budget'].mean()*100:.1f}%, Variance=${fin_df['variance'].sum():,.0f}"
            h_sum = f"Patients={len(hc_df):,}, Avg Cost=${hc_df['treatment_cost'].mean():,.0f}, Readmission={hc_df['readmitted'].mean()*100:.1f}%, Satisfaction={hc_df['satisfaction_score'].mean():.1f}/10, Uninsured={( hc_df['insurance_type']=='Uninsured').mean()*100:.1f}%"
            result = generate_executive_summary(s_sum, m_sum, f_sum, h_sum)
        st.markdown(f'<div class="ai" style="font-size:0.9rem;">{result}</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# FEATURE 7: CROSS-DOMAIN INSIGHTS
# ════════════════════════════════════════════════════════════════
elif active == "Cross-Domain Insights":
    st.markdown("<div class='ph'><p class='pt'>Cross-Domain Insights</p><p class='ps'>AI-powered correlations connecting Sales, Marketing, Finance & Healthcare — unique to Drishti</p></div>", unsafe_allow_html=True)

    st.markdown("""
    <div style='background:#F0FFF4;border:1px solid #C6F6D5;border-radius:10px;padding:16px 20px;margin-bottom:20px;'>
        <div style='font-size:0.78rem;font-weight:700;color:#27AE60;margin-bottom:4px;'>Drishti's Unique Feature</div>
        <div style='font-size:0.82rem;color:#4A5568;'>No other free analytics tool finds connections across Sales, Finance, Marketing, AND Healthcare simultaneously. This is what makes Drishti different.</div>
    </div>
    """, unsafe_allow_html=True)

    # Quick cross-domain metrics
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Sales Revenue", f"${sales_df['revenue'].sum()/1e6:.1f}M")
    with c2: st.metric("Marketing ROI", f"{mkt_df['roi'].mean():.1f}x")
    with c3: st.metric("Finance Over-Budget", f"{fin_df['over_budget'].mean()*100:.0f}%")
    with c4: st.metric("HC Satisfaction", f"{hc_df['satisfaction_score'].mean():.1f}/10")

    # Revenue vs Marketing Spend correlation chart
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='cc'><div class='ct'>Sales Revenue vs Marketing Spend — Monthly Correlation</div>", unsafe_allow_html=True)
    s_m = sales_df.groupby(sales_df['date'].dt.to_period('M').astype(str))['revenue'].sum().reset_index()
    s_m.columns = ['month', 'revenue']
    mk_m = mkt_df.groupby(mkt_df['date'].dt.to_period('M').astype(str))['spend'].sum().reset_index()
    mk_m.columns = ['month', 'spend']
    merged = s_m.merge(mk_m, on='month', how='inner')

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=merged['month'], y=merged['revenue'], name='Sales Revenue', line=dict(color=ACC, width=2)), secondary_y=False)
    fig.add_trace(go.Scatter(x=merged['month'], y=merged['spend'], name='Mkt Spend', line=dict(color=WARN, width=2, dash='dot')), secondary_y=True)
    fig.update_layout(height=300, margin=dict(t=8,b=8,l=4,r=4), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter",size=11,color=MID))
    fig.update_xaxes(gridcolor=BDR)
    fig.update_yaxes(gridcolor=BDR, secondary_y=False)
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Find Cross-Domain Correlations", key="cross_insights"):
        with st.spinner("Analyzing patterns across all 4 domains..."):
            raw = cross_domain_insights(sales_df, mkt_df, fin_df, hc_df)
            insights = parse_cross_insights(raw)

        if insights:
            for ins in insights:
                st.markdown(f"""<div class='cross-card'>
                    <div class='cross-title'>🔗 {ins.get('title','')}</div>
                    <div class='cross-body'><strong>Finding:</strong> {ins.get('finding','')}<br><strong>Action:</strong> {ins.get('action','')}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai">{raw}</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# NEW DATASET — with Benchmark Mode
# ════════════════════════════════════════════════════════════════
elif active == "New Dataset":
    st.markdown("<div class='ph'><p class='pt'>New Dataset</p><p class='ps'>Upload any CSV or Excel file — get instant charts, AI insights, and industry benchmarking</p></div>", unsafe_allow_html=True)

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

            # ── FEATURE 8: BENCHMARK MODE ──
            if num:
                st.markdown("<hr class='dv'>", unsafe_allow_html=True)
                st.markdown("<div class='sl'>Benchmark Against Industry Data</div>", unsafe_allow_html=True)
                bm_col1, bm_col2, bm_col3 = st.columns(3)
                with bm_col1:
                    bm_domain = st.selectbox("Compare Against", ["Sales", "Marketing", "Finance", "Healthcare"])
                with bm_col2:
                    bm_col_upload = st.selectbox("Your Key Metric", num)
                with bm_col3:
                    bm_col_ref = {
                        "Sales": "revenue", "Marketing": "roi",
                        "Finance": "actual_spend", "Healthcare": "treatment_cost"
                    }
                    ref_df = {"Sales": sales_df, "Marketing": mkt_df, "Finance": fin_df, "Healthcare": hc_df}[bm_domain]
                    st.text(f"Reference: {bm_col_ref[bm_domain]}")

                if st.button("Run Benchmark Analysis", key="benchmark"):
                    with st.spinner("Benchmarking against industry data..."):
                        result = benchmark_analysis(df, bm_domain, ref_df, bm_col_upload if bm_col_upload in df.columns else num[0])
                    st.markdown(f'<div class="ai">{result}</div>', unsafe_allow_html=True)

            # AI Insights
            st.markdown("<hr class='dv'>", unsafe_allow_html=True)
            st.markdown("<div class='sl'>AI-Generated Analysis</div>", unsafe_allow_html=True)
            if st.button("Generate Insights", key="u_ai"):
                prompt = f"""Analyze this dataset named '{uf.name}'.
Columns: {', '.join(df.columns)}
Row count: {len(df):,}
Sample:\n{df.head(5).to_string()}
Stats:\n{df.describe().to_string()}

Write exactly:
Insight 1: [finding]
Insight 2: [finding]
Insight 3: [finding]
Risk 1: [risk or data quality issue]
Risk 2: [risk or data quality issue]
Recommendation 1: [action]
Recommendation 2: [action]"""
                with st.spinner("Analyzing your data..."):
                    result = gemini(prompt)
                st.markdown(f'<div class="ai">{result}</div>', unsafe_allow_html=True)

            # Anomaly Detection on uploaded data
            if num:
                st.markdown("<hr class='dv'>", unsafe_allow_html=True)
                st.markdown("<div class='sl'>Anomaly Detection</div>", unsafe_allow_html=True)
                if st.button("Scan Uploaded Data for Anomalies", key="u_anomaly"):
                    with st.spinner("Scanning..."):
                        raw = detect_anomalies(df, num[0], cat[0] if cat else None, uf.name)
                        anomalies = parse_anomalies(raw)
                    for a in anomalies:
                        st.markdown(f"""<div class='anomaly-card'>
                            <div class='anomaly-title'>⚠ {a.get('title','')} — {a.get('severity','')}</div>
                            <div class='anomaly-body'>{a.get('detail','')}</div>
                        </div>""", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Could not read file: {e}")
    else:
        st.markdown(f"""
        <div style='background:{CARD};border:2px dashed {BDR};border-radius:12px;
                    padding:56px;text-align:center;color:{LITE};margin-top:8px;'>
          <div style='font-size:0.9rem;font-weight:600;color:{MID};margin-bottom:8px;'>
            Drop your file here or click to browse
          </div>
          <div style='font-size:0.8rem;'>Supports CSV, XLSX, XLS — any domain</div>
          <div style='font-size:0.75rem;margin-top:8px;color:{LITE};'>Includes AI insights + industry benchmarking</div>
        </div>""", unsafe_allow_html=True)