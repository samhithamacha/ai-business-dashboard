import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from google import genai
from dotenv import load_dotenv
import os

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

.sl{{font-size:0.68rem;font-weight:700;color:{LITE};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;}}
.dv{{border:none;border-top:1px solid {BDR};margin:1.5rem 0 1.2rem;}}

.stButton>button{{
  background:{ACC}!important;color:#fff!important;border:none!important;
  border-radius:6px!important;padding:9px 24px!important;
  font-size:0.8rem!important;font-weight:600!important;
  font-family:'Inter',sans-serif!important;letter-spacing:0.03em!important;
}}
.stButton>button:hover{{background:{ACC2}!important;}}

.stMultiSelect label,.stSelectbox label,.stFileUploader label{{
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

# ── DATA ─────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    s = pd.read_csv('data/sales_data.csv',      parse_dates=['date'])
    m = pd.read_csv('data/marketing_data.csv',  parse_dates=['date'])
    f = pd.read_csv('data/finance_data.csv',    parse_dates=['date'])
    h = pd.read_csv('data/healthcare_data.csv', parse_dates=['admission_date'])
    return s, m, f, h

sales_df, mkt_df, fin_df, hc_df = load_data()

# ── GEMINI AI ─────────────────────────────────────────────────────
def ai(summary, domain):
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
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error: {e}"

# ── SIDEBAR ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='padding:28px 20px 16px;'>
      <div style='font-size:1.1rem;font-weight:800;color:#F0F4F8;letter-spacing:-0.02em;'>Drishti</div>
      <div style='font-size:0.65rem;color:#4A5568;text-transform:uppercase;letter-spacing:0.1em;margin-top:2px;'>Analytics Platform</div>
    </div>
    <div style='height:1px;background:rgba(255,255,255,0.07);margin:0 20px 8px;'></div>
    <div style='padding:8px 20px 4px;font-size:0.62rem;font-weight:700;color:#2D3748;text-transform:uppercase;letter-spacing:0.12em;'>Main</div>
    """, unsafe_allow_html=True)

    page = st.radio("Navigation", ["Overview","Sales","Marketing","Finance","Healthcare"],
                    label_visibility="collapsed")

    st.markdown(f"""
    <div style='height:1px;background:rgba(255,255,255,0.07);margin:8px 20px;'></div>
    <div style='padding:8px 20px 4px;font-size:0.62rem;font-weight:700;color:#2D3748;text-transform:uppercase;letter-spacing:0.12em;'>Data</div>
    """, unsafe_allow_html=True)

    page2 = st.radio("Data", ["New Dataset"], label_visibility="collapsed")

    st.markdown(f"""
    <div style='height:1px;background:rgba(255,255,255,0.07);margin:8px 20px;'></div>
    <div style='padding:8px 20px 24px;font-size:0.7rem;color:#4A5568;line-height:1.7;'>
      Jan 2022 – Dec 2023<br>11,000+ records · 4 domains
    </div>
    """, unsafe_allow_html=True)

# Use session state to track which section is active
if "active_section" not in st.session_state:
    st.session_state.active_section = "Overview"

# Determine active page
if page2 == "New Dataset":
    active = "New Dataset"
else:
    active = page

# ── AI SECTION HELPER ────────────────────────────────────────────
def ai_section(key, summary, domain):
    st.markdown("<hr class='dv'>", unsafe_allow_html=True)
    st.markdown("<div class='sl'>AI-Generated Analysis</div>", unsafe_allow_html=True)
    if st.button("Generate Insights", key=key):
        with st.spinner("Analyzing..."):
            result = ai(summary, domain)
        st.markdown(f'<div class="ai">{result}</div>', unsafe_allow_html=True)

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
        st.plotly_chart(fig_clean(fig), width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='cc'><div class='ct'>Campaign ROI by Type</div>", unsafe_allow_html=True)
        r = mkt_df.groupby('campaign_type')['roi'].mean().sort_values(ascending=True).reset_index()
        fig = px.bar(r, x='roi', y='campaign_type', orientation='h', color='roi', color_continuous_scale=BLUE_SCALE, labels={'roi':'Avg ROI','campaign_type':''})
        st.plotly_chart(fig_clean(fig), width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

    c3,c4 = st.columns(2)
    with c3:
        st.markdown("<div class='cc'><div class='ct'>Budget vs Actual by Department</div>", unsafe_allow_html=True)
        d = fin_df.groupby('department')[['budget','actual_spend']].sum().reset_index()
        fig = px.bar(d, x='department', y=['budget','actual_spend'], barmode='group',
                     color_discrete_map={'budget':ACC,'actual_spend':ACC2}, labels={'value':'($)','department':'','variable':''})
        st.plotly_chart(fig_clean(fig), width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)
    with c4:
        st.markdown("<div class='cc'><div class='ct'>Patient Admissions by Department</div>", unsafe_allow_html=True)
        a = hc_df['department'].value_counts().reset_index()
        a.columns = ['dept','count']
        fig = px.pie(a, names='dept', values='count', color_discrete_sequence=CSEQ, hole=0.52)
        fig.update_traces(textposition='outside', textfont_size=10)
        st.plotly_chart(fig_clean(fig, h=290), width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SALES
# ════════════════════════════════════════════════════════════════
elif active == "Sales":
    st.markdown("<div class='ph'><p class='pt'>Sales Analytics</p><p class='ps'>Revenue, profitability, and channel performance</p></div>", unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1: reg = st.multiselect("Region", sales_df['region'].unique(), default=list(sales_df['region'].unique()))
    with c2: ch  = st.multiselect("Channel", sales_df['channel'].unique(), default=list(sales_df['channel'].unique()))
    df = sales_df[sales_df['region'].isin(reg) & sales_df['channel'].isin(ch)]

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Total Revenue", f"${df['revenue'].sum()/1e6:.2f}M")
    with c2: st.metric("Total Profit",  f"${df['profit'].sum()/1e6:.2f}M")
    with c3: st.metric("Avg Discount",  f"{df['discount_pct'].mean()*100:.1f}%")
    with c4: st.metric("Return Rate",   f"{df['returned'].mean()*100:.1f}%")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("<div class='cc'><div class='ct'>Monthly Revenue</div>", unsafe_allow_html=True)
        m = df.groupby(df['date'].dt.to_period('M').astype(str))['revenue'].sum().reset_index()
        m.columns = ['month','revenue']
        fig = px.line(m, x='month', y='revenue', color_discrete_sequence=[ACC], labels={'revenue':'Revenue ($)','month':''})
        fig.update_traces(line_width=2.5)
        st.plotly_chart(fig_clean(fig), width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='cc'><div class='ct'>Revenue by Product</div>", unsafe_allow_html=True)
        p = df.groupby('product')['revenue'].sum().sort_values().reset_index()
        fig = px.bar(p, x='revenue', y='product', orientation='h', color='revenue', color_continuous_scale=BLUE_SCALE, labels={'revenue':'Revenue ($)','product':''})
        st.plotly_chart(fig_clean(fig), width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

    c3,c4 = st.columns(2)
    with c3:
        st.markdown("<div class='cc'><div class='ct'>Revenue & Profit by Region</div>", unsafe_allow_html=True)
        r = df.groupby('region')[['revenue','profit']].sum().reset_index()
        fig = px.bar(r, x='region', y=['revenue','profit'], barmode='group',
                     color_discrete_map={'revenue':ACC,'profit':ACC2}, labels={'value':'($)','region':'','variable':''})
        st.plotly_chart(fig_clean(fig), width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)
    with c4:
        st.markdown("<div class='cc'><div class='ct'>Revenue by Sales Channel</div>", unsafe_allow_html=True)
        cv = df.groupby('channel')['revenue'].sum().reset_index()
        fig = px.pie(cv, names='channel', values='revenue', color_discrete_sequence=CSEQ, hole=0.52)
        fig.update_traces(textposition='outside', textfont_size=10)
        st.plotly_chart(fig_clean(fig, h=290), width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

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

    cf = st.multiselect("Campaign Type", mkt_df['campaign_type'].unique(), default=list(mkt_df['campaign_type'].unique()))
    df = mkt_df[mkt_df['campaign_type'].isin(cf)]

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Average ROI",         f"{df['roi'].mean():.2f}x")
    with c2: st.metric("Average CTR",         f"{df['ctr'].mean()*100:.2f}%")
    with c3: st.metric("Avg Conversion Rate", f"{df['conversion_rate'].mean()*100:.2f}%")
    with c4: st.metric("Total Spend",         f"${df['spend'].sum()/1e6:.2f}M")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("<div class='cc'><div class='ct'>Avg ROI by Campaign Type</div>", unsafe_allow_html=True)
        r = df.groupby('campaign_type')['roi'].mean().sort_values(ascending=True).reset_index()
        fig = px.bar(r, x='roi', y='campaign_type', orientation='h', color='roi', color_continuous_scale=BLUE_SCALE, labels={'roi':'Avg ROI','campaign_type':''})
        st.plotly_chart(fig_clean(fig), width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='cc'><div class='ct'>Conversion Rate by Segment</div>", unsafe_allow_html=True)
        s = df.groupby('customer_segment')['conversion_rate'].mean().sort_values(ascending=True).reset_index()
        fig = px.bar(s, x='conversion_rate', y='customer_segment', orientation='h', color='conversion_rate', color_continuous_scale=BLUE_SCALE2, labels={'conversion_rate':'Rate','customer_segment':''})
        st.plotly_chart(fig_clean(fig), width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='cc'><div class='ct'>Marketing Spend vs Revenue Generated</div>", unsafe_allow_html=True)
    fig = px.scatter(df, x='spend', y='revenue_generated', color='campaign_type', size='conversions',
                     color_discrete_sequence=CSEQ, opacity=0.72,
                     labels={'spend':'Spend ($)','revenue_generated':'Revenue ($)','campaign_type':'Campaign'})
    st.plotly_chart(fig_clean(fig, h=360), width='stretch')
    st.markdown("</div>", unsafe_allow_html=True)

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

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Total Budget",       f"${df['budget'].sum()/1e6:.2f}M")
    with c2: st.metric("Total Actual Spend", f"${df['actual_spend'].sum()/1e6:.2f}M")
    with c3: st.metric("Over-Budget Rate",   f"{df['over_budget'].mean()*100:.1f}%")
    with c4: st.metric("Avg Variance",       f"${df['variance'].mean():,.0f}")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("<div class='cc'><div class='ct'>Budget vs Actual by Department</div>", unsafe_allow_html=True)
        d = df.groupby('department')[['budget','actual_spend']].sum().reset_index()
        fig = px.bar(d, x='department', y=['budget','actual_spend'], barmode='group',
                     color_discrete_map={'budget':ACC,'actual_spend':ACC2}, labels={'value':'($)','department':'','variable':''})
        st.plotly_chart(fig_clean(fig), width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='cc'><div class='ct'>Over-Budget Rate by Department (%)</div>", unsafe_allow_html=True)
        o = df.groupby('department')['over_budget'].mean().reset_index()
        o['pct'] = (o['over_budget'] * 100).round(1)
        fig = px.bar(o, x='department', y='pct', color='pct', color_continuous_scale=RED_SCALE, labels={'pct':'Over-Budget (%)','department':''})
        st.plotly_chart(fig_clean(fig), width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

    c3,c4 = st.columns(2)
    with c3:
        st.markdown("<div class='cc'><div class='ct'>Expense Category Breakdown</div>", unsafe_allow_html=True)
        e = df.groupby('expense_category')['actual_spend'].sum().reset_index()
        fig = px.pie(e, names='expense_category', values='actual_spend', color_discrete_sequence=CSEQ, hole=0.52)
        fig.update_traces(textposition='outside', textfont_size=10)
        st.plotly_chart(fig_clean(fig, h=290), width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)
    with c4:
        st.markdown("<div class='cc'><div class='ct'>Quarterly Budget vs Spend</div>", unsafe_allow_html=True)
        q = df.groupby('quarter')[['budget','actual_spend']].sum().reset_index()
        fig = px.bar(q, x='quarter', y=['budget','actual_spend'], barmode='group',
                     color_discrete_map={'budget':ACC,'actual_spend':ACC2}, labels={'value':'($)','quarter':'','variable':''})
        st.plotly_chart(fig_clean(fig), width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

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

    dpf = st.multiselect("Department", hc_df['department'].unique(), default=list(hc_df['department'].unique()))
    df  = hc_df[hc_df['department'].isin(dpf)]

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Total Patients",     f"{len(df):,}")
    with c2: st.metric("Avg Treatment Cost", f"${df['treatment_cost'].mean():,.0f}")
    with c3: st.metric("Readmission Rate",   f"{df['readmitted'].mean()*100:.1f}%")
    with c4: st.metric("Avg Stay",           f"{df['length_of_stay'].mean():.1f} days")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("<div class='cc'><div class='ct'>Admissions by Department</div>", unsafe_allow_html=True)
        a = df['department'].value_counts().reset_index()
        a.columns = ['dept','count']
        fig = px.bar(a, x='dept', y='count', color='count', color_continuous_scale=BLUE_SCALE, labels={'count':'Admissions','dept':''})
        st.plotly_chart(fig_clean(fig), width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='cc'><div class='ct'>Most Common Diagnoses</div>", unsafe_allow_html=True)
        d = df['diagnosis'].value_counts().reset_index()
        d.columns = ['diagnosis','count']
        fig = px.bar(d, x='count', y='diagnosis', orientation='h', color='count', color_continuous_scale=RED_SCALE, labels={'count':'Cases','diagnosis':''})
        st.plotly_chart(fig_clean(fig), width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

    c3,c4 = st.columns(2)
    with c3:
        st.markdown("<div class='cc'><div class='ct'>Avg Treatment Cost by Age Group</div>", unsafe_allow_html=True)
        ag = df.groupby('age_group', observed=True)['treatment_cost'].mean().reset_index()
        fig = px.bar(ag, x='age_group', y='treatment_cost', color='treatment_cost', color_continuous_scale=BLUE_SCALE, labels={'treatment_cost':'Avg Cost ($)','age_group':''})
        st.plotly_chart(fig_clean(fig), width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)
    with c4:
        st.markdown("<div class='cc'><div class='ct'>Avg Cost by Insurance Type</div>", unsafe_allow_html=True)
        ins = df.groupby('insurance_type')['treatment_cost'].mean().reset_index()
        fig = px.bar(ins, x='insurance_type', y='treatment_cost', color='treatment_cost', color_continuous_scale=BLUE_SCALE2, labels={'treatment_cost':'Avg Cost ($)','insurance_type':''})
        st.plotly_chart(fig_clean(fig), width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='cc'><div class='ct'>Length of Stay vs Treatment Cost</div>", unsafe_allow_html=True)
    fig = px.scatter(df.sample(min(800,len(df))), x='length_of_stay', y='treatment_cost', color='department',
                     size='num_procedures', color_discrete_sequence=CSEQ, opacity=0.65,
                     labels={'length_of_stay':'Length of Stay (days)','treatment_cost':'Treatment Cost ($)','department':'Dept'})
    st.plotly_chart(fig_clean(fig, h=360), width='stretch')
    st.markdown("</div>", unsafe_allow_html=True)

    ai_section("h_ai", f"""Total Patients: {len(df):,}
Avg Treatment Cost: ${df['treatment_cost'].mean():,.0f}
Most Expensive Dept: {df.groupby('department')['treatment_cost'].mean().idxmax()}
Readmission Rate: {df['readmitted'].mean()*100:.1f}%
Most Common Diagnosis: {df['diagnosis'].value_counts().idxmax()}
Highest Readmission Diagnosis: {df.groupby('diagnosis')['readmitted'].mean().idxmax()}
Avg Length of Stay: {df['length_of_stay'].mean():.1f} days
Avg Satisfaction Score: {df['satisfaction_score'].mean():.1f}/10
Uninsured Rate: {(df['insurance_type']=='Uninsured').mean()*100:.1f}%""", "Healthcare")

# ════════════════════════════════════════════════════════════════
# NEW DATASET
# ════════════════════════════════════════════════════════════════
elif active == "New Dataset":
    st.markdown("<div class='ph'><p class='pt'>New Dataset</p><p class='ps'>Upload any CSV or Excel file to generate charts and AI insights instantly</p></div>", unsafe_allow_html=True)

    uf = st.file_uploader("Upload CSV or Excel file", type=["csv","xlsx","xls"])

    if uf:
        try:
            df = pd.read_csv(uf) if uf.name.endswith('.csv') else pd.read_excel(uf)
            num = df.select_dtypes(include=[np.number]).columns.tolist()
            cat = df.select_dtypes(include=['object','category']).columns.tolist()

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            c1,c2,c3,c4 = st.columns(4)
            with c1: st.metric("Total Rows",      f"{len(df):,}")
            with c2: st.metric("Total Columns",   f"{len(df.columns)}")
            with c3: st.metric("Numeric Columns", f"{len(num)}")
            with c4: st.metric("Missing Values",  f"{df.isnull().sum().sum():,}")

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            st.markdown("<div class='cc'><div class='ct'>Data Preview</div>", unsafe_allow_html=True)
            st.dataframe(df.head(10), width='stretch', height=260)
            st.markdown("</div>", unsafe_allow_html=True)

            if num and cat:
                c1,c2 = st.columns(2)
                tc, tn = cat[0], num[0]
                grp = df.groupby(tc)[tn].sum().sort_values(ascending=True).reset_index()
                with c1:
                    st.markdown("<div class='cc'><div class='ct'>Top Category Distribution</div>", unsafe_allow_html=True)
                    fig = px.bar(grp, x=tn, y=tc, orientation='h', color=tn, color_continuous_scale=BLUE_SCALE, labels={tn:tn,tc:''})
                    st.plotly_chart(fig_clean(fig), width='stretch')
                    st.markdown("</div>", unsafe_allow_html=True)
                with c2:
                    st.markdown("<div class='cc'><div class='ct'>Category Share</div>", unsafe_allow_html=True)
                    fig = px.pie(grp, names=tc, values=tn, color_discrete_sequence=CSEQ, hole=0.52)
                    fig.update_traces(textposition='outside', textfont_size=10)
                    st.plotly_chart(fig_clean(fig, h=290), width='stretch')
                    st.markdown("</div>", unsafe_allow_html=True)

            if len(num) >= 2:
                st.markdown("<div class='cc'><div class='ct'>Numeric Correlation</div>", unsafe_allow_html=True)
                fig = px.scatter(df.sample(min(500,len(df))), x=num[0], y=num[1],
                                 color=cat[0] if cat else None, color_discrete_sequence=CSEQ, opacity=0.7)
                st.plotly_chart(fig_clean(fig, h=340), width='stretch')
                st.markdown("</div>", unsafe_allow_html=True)

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
                    try:
                        response = client.models.generate_content(
                            model="gemini-2.0-flash",
                            contents=prompt
                        )
                        result = response.text
                    except Exception as e:
                        result = f"Error: {e}"
                st.markdown(f'<div class="ai">{result}</div>', unsafe_allow_html=True)

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
        </div>""", unsafe_allow_html=True)
