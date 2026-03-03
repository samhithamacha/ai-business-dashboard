import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
from dotenv import load_dotenv
import os

# ── CONFIG ──────────────────────────────────────────────────────
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

st.set_page_config(
    page_title="AI Business Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #2d3250);
        border-radius: 12px; padding: 20px; margin: 8px 0;
        border-left: 4px solid #4f8bf9;
    }
    .section-title {
        font-size: 1.4rem; font-weight: 700;
        color: #4f8bf9; margin: 20px 0 10px 0;
    }
    .ai-box {
        background: linear-gradient(135deg, #1a1f35, #0d1117);
        border: 1px solid #4f8bf9; border-radius: 12px;
        padding: 20px; margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ────────────────────────────────────────────────────
@st.cache_data
def load_data():
    sales      = pd.read_csv('data/sales_data.csv',      parse_dates=['date'])
    marketing  = pd.read_csv('data/marketing_data.csv',  parse_dates=['date'])
    finance    = pd.read_csv('data/finance_data.csv',    parse_dates=['date'])
    healthcare = pd.read_csv('data/healthcare_data.csv', parse_dates=['admission_date'])
    return sales, marketing, finance, healthcare

sales_df, marketing_df, finance_df, healthcare_df = load_data()

# ── GEMINI HELPER ────────────────────────────────────────────────
def get_ai_insight(summary: str, domain: str) -> str:
    prompt = f"""You are a senior business analyst reviewing {domain} performance data.

Data Summary:
{summary}

Provide exactly:
1. THREE key insights (label them 🔍 Insight 1, 2, 3)
2. TWO risks or red flags (label them ⚠️ Risk 1, 2)
3. TWO actionable recommendations (label them ✅ Action 1, 2)

Be concise, specific, and data-driven. Use plain language."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Could not generate insights: {str(e)}"

# ── SIDEBAR ──────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/combo-chart.png", width=60)
    st.title("AI Dashboard")
    st.markdown("---")
    page = st.radio("Navigate", [
        "🏠 Overview",
        "🛒 Sales",
        "📣 Marketing",
        "💰 Finance",
        "🏥 Healthcare"
    ])
    st.markdown("---")
    st.caption("Built with Streamlit + Gemini AI")

# ════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ════════════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.title("📊 AI-Powered Business Insights Dashboard")
    st.markdown("Multi-domain analytics across Sales, Marketing, Finance & Healthcare")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Total Revenue",    f"${sales_df['revenue'].sum()/1e6:.2f}M")
    with col2:
        st.metric("📈 Avg Marketing ROI", f"{marketing_df['roi'].mean():.2f}x")
    with col3:
        st.metric("🏦 Budget Variance",   f"${finance_df['variance'].mean():,.0f}")
    with col4:
        st.metric("🏥 Avg Treatment Cost",f"${healthcare_df['treatment_cost'].mean():,.0f}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">🛒 Monthly Revenue Trend</p>', unsafe_allow_html=True)
        monthly = sales_df.groupby(sales_df['date'].dt.to_period('M').astype(str))['revenue'].sum().reset_index()
        monthly.columns = ['month', 'revenue']
        fig = px.area(monthly, x='month', y='revenue', template='plotly_dark',
                      color_discrete_sequence=['#4f8bf9'])
        fig.update_layout(margin=dict(t=10,b=10), height=280)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">📣 Campaign ROI by Type</p>', unsafe_allow_html=True)
        roi = marketing_df.groupby('campaign_type')['roi'].mean().reset_index()
        fig = px.bar(roi, x='campaign_type', y='roi', template='plotly_dark',
                     color='roi', color_continuous_scale='Blues')
        fig.update_layout(margin=dict(t=10,b=10), height=280)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<p class="section-title">💰 Budget vs Actual by Dept</p>', unsafe_allow_html=True)
        dept = finance_df.groupby('department')[['budget','actual_spend']].sum().reset_index()
        fig = px.bar(dept, x='department', y=['budget','actual_spend'],
                     barmode='group', template='plotly_dark')
        fig.update_layout(margin=dict(t=10,b=10), height=280)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown('<p class="section-title">🏥 Admissions by Department</p>', unsafe_allow_html=True)
        adm = healthcare_df['department'].value_counts().reset_index()
        adm.columns = ['department','count']
        fig = px.pie(adm, names='department', values='count', template='plotly_dark', hole=0.4)
        fig.update_layout(margin=dict(t=10,b=10), height=280)
        st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# PAGE: SALES
# ════════════════════════════════════════════════════════════════
elif page == "🛒 Sales":
    st.title("🛒 Sales Analytics")

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        regions = st.multiselect("Filter by Region", sales_df['region'].unique(),
                                  default=list(sales_df['region'].unique()))
    with col2:
        channels = st.multiselect("Filter by Channel", sales_df['channel'].unique(),
                                   default=list(sales_df['channel'].unique()))

    df = sales_df[sales_df['region'].isin(regions) & sales_df['channel'].isin(channels)]

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue",  f"${df['revenue'].sum():,.0f}")
    col2.metric("Total Profit",   f"${df['profit'].sum():,.0f}")
    col3.metric("Avg Discount",   f"{df['discount_pct'].mean()*100:.1f}%")
    col4.metric("Return Rate",    f"{df['returned'].mean()*100:.1f}%")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">📈 Monthly Revenue</p>', unsafe_allow_html=True)
        m = df.groupby(df['date'].dt.to_period('M').astype(str))['revenue'].sum().reset_index()
        m.columns = ['month','revenue']
        fig = px.line(m, x='month', y='revenue', template='plotly_dark',
                      color_discrete_sequence=['#4f8bf9'])
        fig.update_traces(line_width=2.5)
        fig.update_layout(height=300, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">🏆 Revenue by Product</p>', unsafe_allow_html=True)
        p = df.groupby('product')['revenue'].sum().sort_values().reset_index()
        fig = px.bar(p, x='revenue', y='product', orientation='h', template='plotly_dark',
                     color='revenue', color_continuous_scale='Blues')
        fig.update_layout(height=300, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<p class="section-title">🗺️ Revenue by Region</p>', unsafe_allow_html=True)
        r = df.groupby('region')[['revenue','profit']].sum().reset_index()
        fig = px.bar(r, x='region', y=['revenue','profit'], barmode='group', template='plotly_dark')
        fig.update_layout(height=300, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown('<p class="section-title">📊 Sales Channel Split</p>', unsafe_allow_html=True)
        c = df.groupby('channel')['revenue'].sum().reset_index()
        fig = px.pie(c, names='channel', values='revenue', template='plotly_dark', hole=0.4)
        fig.update_layout(height=300, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    # AI Insights
    st.markdown("---")
    st.markdown('<p class="section-title">🤖 AI-Generated Sales Insights</p>', unsafe_allow_html=True)
    if st.button("✨ Generate AI Insights", key="sales_ai"):
        summary = f"""
Total Revenue: ${df['revenue'].sum():,.0f}
Total Profit: ${df['profit'].sum():,.0f}
Profit Margin: {(df['profit'].sum()/df['revenue'].sum()*100):.1f}%
Avg Discount: {df['discount_pct'].mean()*100:.1f}%
Return Rate: {df['returned'].mean()*100:.1f}%
Top Region: {df.groupby('region')['revenue'].sum().idxmax()}
Top Product: {df.groupby('product')['revenue'].sum().idxmax()}
Best Channel: {df.groupby('channel')['revenue'].sum().idxmax()}
Total Orders: {len(df):,}
"""
        with st.spinner("Gemini is analyzing your sales data..."):
            insight = get_ai_insight(summary, "Sales")
        st.markdown(f'<div class="ai-box">{insight}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# PAGE: MARKETING
# ════════════════════════════════════════════════════════════════
elif page == "📣 Marketing":
    st.title("📣 Marketing Analytics")

    campaign_filter = st.multiselect("Filter by Campaign Type",
                                      marketing_df['campaign_type'].unique(),
                                      default=list(marketing_df['campaign_type'].unique()))
    df = marketing_df[marketing_df['campaign_type'].isin(campaign_filter)]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg ROI",         f"{df['roi'].mean():.2f}x")
    col2.metric("Avg CTR",         f"{df['ctr'].mean()*100:.2f}%")
    col3.metric("Avg Conversion",  f"{df['conversion_rate'].mean()*100:.2f}%")
    col4.metric("Total Spend",     f"${df['spend'].sum():,.0f}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">💹 ROI by Campaign Type</p>', unsafe_allow_html=True)
        r = df.groupby('campaign_type')['roi'].mean().sort_values(ascending=False).reset_index()
        fig = px.bar(r, x='campaign_type', y='roi', template='plotly_dark',
                     color='roi', color_continuous_scale='RdYlGn')
        fig.update_layout(height=300, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">🎯 Conversion Rate by Segment</p>', unsafe_allow_html=True)
        s = df.groupby('customer_segment')['conversion_rate'].mean().reset_index()
        fig = px.bar(s, x='customer_segment', y='conversion_rate', template='plotly_dark',
                     color='conversion_rate', color_continuous_scale='Blues')
        fig.update_layout(height=300, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="section-title">💸 Spend vs Revenue Generated</p>', unsafe_allow_html=True)
    fig = px.scatter(df, x='spend', y='revenue_generated', color='campaign_type',
                     size='conversions', template='plotly_dark', opacity=0.7,
                     title="")
    fig.update_layout(height=380, margin=dict(t=10))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown('<p class="section-title">🤖 AI-Generated Marketing Insights</p>', unsafe_allow_html=True)
    if st.button("✨ Generate AI Insights", key="mkt_ai"):
        summary = f"""
Total Campaigns: {len(df):,}
Avg ROI: {df['roi'].mean():.2f}x
Best Campaign by ROI: {df.groupby('campaign_type')['roi'].mean().idxmax()}
Worst Campaign by ROI: {df.groupby('campaign_type')['roi'].mean().idxmin()}
Avg CTR: {df['ctr'].mean()*100:.2f}%
Avg Conversion Rate: {df['conversion_rate'].mean()*100:.2f}%
Total Marketing Spend: ${df['spend'].sum():,.0f}
Total Revenue from Campaigns: ${df['revenue_generated'].sum():,.0f}
Best Segment by Conversion: {df.groupby('customer_segment')['conversion_rate'].mean().idxmax()}
"""
        with st.spinner("Gemini is analyzing your marketing data..."):
            insight = get_ai_insight(summary, "Marketing")
        st.markdown(f'<div class="ai-box">{insight}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# PAGE: FINANCE
# ════════════════════════════════════════════════════════════════
elif page == "💰 Finance":
    st.title("💰 Finance Analytics")

    year_filter = st.selectbox("Select Year", ['All'] + sorted(finance_df['year'].unique().tolist()))
    df = finance_df if year_filter == 'All' else finance_df[finance_df['year'] == int(year_filter)]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Budget",      f"${df['budget'].sum()/1e6:.2f}M")
    col2.metric("Total Actual Spend",f"${df['actual_spend'].sum()/1e6:.2f}M")
    col3.metric("Over-Budget Rate",  f"{df['over_budget'].mean()*100:.1f}%")
    col4.metric("Avg Variance",      f"${df['variance'].mean():,.0f}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">🏦 Budget vs Actual by Department</p>', unsafe_allow_html=True)
        d = df.groupby('department')[['budget','actual_spend']].sum().reset_index()
        fig = px.bar(d, x='department', y=['budget','actual_spend'],
                     barmode='group', template='plotly_dark')
        fig.update_layout(height=320, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">⚠️ Over-Budget Rate by Department</p>', unsafe_allow_html=True)
        o = df.groupby('department')['over_budget'].mean().reset_index()
        o['pct'] = (o['over_budget'] * 100).round(1)
        fig = px.bar(o, x='department', y='pct', template='plotly_dark',
                     color='pct', color_continuous_scale='Reds')
        fig.update_layout(height=320, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<p class="section-title">💳 Expense Category Breakdown</p>', unsafe_allow_html=True)
        e = df.groupby('expense_category')['actual_spend'].sum().reset_index()
        fig = px.pie(e, names='expense_category', values='actual_spend',
                     template='plotly_dark', hole=0.35)
        fig.update_layout(height=320, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown('<p class="section-title">📊 Spend by Quarter</p>', unsafe_allow_html=True)
        q = df.groupby('quarter')[['budget','actual_spend']].sum().reset_index()
        fig = px.bar(q, x='quarter', y=['budget','actual_spend'],
                     barmode='group', template='plotly_dark')
        fig.update_layout(height=320, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown('<p class="section-title">🤖 AI-Generated Finance Insights</p>', unsafe_allow_html=True)
    if st.button("✨ Generate AI Insights", key="fin_ai"):
        summary = f"""
Total Budget: ${df['budget'].sum():,.0f}
Total Actual Spend: ${df['actual_spend'].sum():,.0f}
Overall Variance: ${df['variance'].sum():,.0f}
Over-Budget Rate: {df['over_budget'].mean()*100:.1f}%
Most Overspent Department: {df.groupby('department')['actual_spend'].sum().idxmax()}
Most Under-Budget Department: {df.groupby('department')['variance'].sum().idxmax()}
Highest Expense Category: {df.groupby('expense_category')['actual_spend'].sum().idxmax()}
"""
        with st.spinner("Gemini is analyzing your finance data..."):
            insight = get_ai_insight(summary, "Finance")
        st.markdown(f'<div class="ai-box">{insight}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# PAGE: HEALTHCARE
# ════════════════════════════════════════════════════════════════
elif page == "🏥 Healthcare":
    st.title("🏥 Healthcare Analytics")

    dept_filter = st.multiselect("Filter by Department",
                                  healthcare_df['department'].unique(),
                                  default=list(healthcare_df['department'].unique()))
    df = healthcare_df[healthcare_df['department'].isin(dept_filter)]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Patients",     f"{len(df):,}")
    col2.metric("Avg Treatment Cost", f"${df['treatment_cost'].mean():,.0f}")
    col3.metric("Readmission Rate",   f"{df['readmitted'].mean()*100:.1f}%")
    col4.metric("Avg Stay (days)",    f"{df['length_of_stay'].mean():.1f}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">🏥 Admissions by Department</p>', unsafe_allow_html=True)
        a = df['department'].value_counts().reset_index()
        a.columns = ['department','count']
        fig = px.bar(a, x='department', y='count', template='plotly_dark',
                     color='count', color_continuous_scale='Blues')
        fig.update_layout(height=300, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">🩺 Top Diagnoses</p>', unsafe_allow_html=True)
        d = df['diagnosis'].value_counts().reset_index()
        d.columns = ['diagnosis','count']
        fig = px.bar(d, x='count', y='diagnosis', orientation='h', template='plotly_dark',
                     color='count', color_continuous_scale='Reds')
        fig.update_layout(height=300, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<p class="section-title">💊 Avg Cost by Age Group</p>', unsafe_allow_html=True)
        ag = df.groupby('age_group', observed=True)['treatment_cost'].mean().reset_index()
        fig = px.bar(ag, x='age_group', y='treatment_cost', template='plotly_dark',
                     color='treatment_cost', color_continuous_scale='Oranges')
        fig.update_layout(height=300, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown('<p class="section-title">🛡️ Cost by Insurance Type</p>', unsafe_allow_html=True)
        ins = df.groupby('insurance_type')['treatment_cost'].mean().reset_index()
        fig = px.bar(ins, x='insurance_type', y='treatment_cost', template='plotly_dark',
                     color='treatment_cost', color_continuous_scale='Purples')
        fig.update_layout(height=300, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="section-title">📊 Length of Stay vs Treatment Cost</p>', unsafe_allow_html=True)
    fig = px.scatter(df.sample(min(800, len(df))),
                     x='length_of_stay', y='treatment_cost',
                     color='department', size='num_procedures',
                     template='plotly_dark', opacity=0.7)
    fig.update_layout(height=380, margin=dict(t=10))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown('<p class="section-title">🤖 AI-Generated Healthcare Insights</p>', unsafe_allow_html=True)
    if st.button("✨ Generate AI Insights", key="health_ai"):
        summary = f"""
Total Patients: {len(df):,}
Avg Treatment Cost: ${df['treatment_cost'].mean():,.0f}
Most Expensive Dept: {df.groupby('department')['treatment_cost'].mean().idxmax()}
Readmission Rate: {df['readmitted'].mean()*100:.1f}%
Most Common Diagnosis: {df['diagnosis'].value_counts().idxmax()}
Highest Readmission Diagnosis: {df.groupby('diagnosis')['readmitted'].mean().idxmax()}
Avg Length of Stay: {df['length_of_stay'].mean():.1f} days
Avg Satisfaction Score: {df['satisfaction_score'].mean():.1f}/10
Most Common Insurance: {df['insurance_type'].value_counts().idxmax()}
Uninsured Patient %: {(df['insurance_type']=='Uninsured').mean()*100:.1f}%
"""
        with st.spinner("Gemini is analyzing your healthcare data..."):
            insight = get_ai_insight(summary, "Healthcare")
        st.markdown(f'<div class="ai-box">{insight}</div>', unsafe_allow_html=True)
