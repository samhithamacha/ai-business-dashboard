import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

np.random.seed(42)
os.makedirs('data', exist_ok=True)

# ── SALES (5,000 rows) ──────────────────────────────────────────
n = 5000
dates = [datetime(2022,1,1) + timedelta(days=np.random.randint(0,730)) for _ in range(n)]
sales_df = pd.DataFrame({
    'date':            dates,
    'region':          np.random.choice(['North','South','East','West','Central'], n),
    'product':         np.random.choice(['Laptop','Phone','Tablet','Monitor','Keyboard','Headphones','Webcam'], n),
    'channel':         np.random.choice(['Online','Retail','Wholesale','Direct'], n),
    'units_sold':      np.random.randint(1, 100, n),
    'unit_price':      np.random.uniform(20, 1500, n).round(2),
    'discount_pct':    np.random.uniform(0, 0.30, n).round(2),
    'customer_age':    np.random.randint(18, 70, n),
    'customer_gender': np.random.choice(['Male','Female','Other'], n),
    'returned':        np.random.choice([0,1], n, p=[0.92,0.08])
})
sales_df['revenue'] = (sales_df['units_sold'] * sales_df['unit_price'] * (1 - sales_df['discount_pct'])).round(2)
sales_df['cost']    = (sales_df['revenue'] * np.random.uniform(0.4, 0.7, n)).round(2)
sales_df['profit']  = (sales_df['revenue'] - sales_df['cost']).round(2)
sales_df.to_csv('data/sales_data.csv', index=False)
print(" Sales dataset created")

# ── MARKETING (2,000 rows) ──────────────────────────────────────
n = 2000
marketing_df = pd.DataFrame({
    'date':              [datetime(2022,1,1) + timedelta(days=np.random.randint(0,730)) for _ in range(n)],
    'campaign_type':     np.random.choice(['Email','Social Media','Google Ads','TV','Influencer','SEO'], n),
    'customer_segment':  np.random.choice(['Young Adults','Professionals','Seniors','Students','Parents'], n),
    'impressions':       np.random.randint(500, 50000, n),
    'clicks':            np.random.randint(10, 5000, n),
    'conversions':       np.random.randint(1, 500, n),
    'spend':             np.random.uniform(100, 10000, n).round(2),
    'revenue_generated': np.random.uniform(200, 50000, n).round(2),
    'region':            np.random.choice(['North','South','East','West','Central'], n)
})
marketing_df['ctr']             = (marketing_df['clicks'] / marketing_df['impressions']).round(4)
marketing_df['conversion_rate'] = (marketing_df['conversions'] / marketing_df['clicks']).round(4)
marketing_df['roi']             = ((marketing_df['revenue_generated'] - marketing_df['spend']) / marketing_df['spend']).round(4)
marketing_df.to_csv('data/marketing_data.csv', index=False)
print(" Marketing dataset created")

# ── FINANCE (1,000 rows) ────────────────────────────────────────
n = 1000
finance_df = pd.DataFrame({
    'date':             [datetime(2022,1,1) + timedelta(days=np.random.randint(0,730)) for _ in range(n)],
    'department':       np.random.choice(['Engineering','Sales','Marketing','HR','Operations','IT','Finance'], n),
    'expense_category': np.random.choice(['Salaries','Software','Travel','Equipment','Marketing','Utilities','Rent'], n),
    'budget':           np.random.uniform(10000, 500000, n).round(2),
    'actual_spend':     np.random.uniform(8000, 520000, n).round(2),
    'headcount':        np.random.randint(2, 50, n),
    'quarter':          np.random.choice(['Q1','Q2','Q3','Q4'], n),
    'year':             np.random.choice([2022,2023], n)
})
finance_df['variance']     = (finance_df['budget'] - finance_df['actual_spend']).round(2)
finance_df['variance_pct'] = (finance_df['variance'] / finance_df['budget'] * 100).round(2)
finance_df['over_budget']  = (finance_df['actual_spend'] > finance_df['budget']).astype(int)
finance_df.to_csv('data/finance_data.csv', index=False)
print(" Finance dataset created")

# ── HEALTHCARE (3,000 rows) ─────────────────────────────────────
n = 3000
healthcare_df = pd.DataFrame({
    'admission_date':    [datetime(2022,1,1) + timedelta(days=np.random.randint(0,730)) for _ in range(n)],
    'department':        np.random.choice(['Emergency','Cardiology','Orthopedics','Neurology','Oncology','Pediatrics','ICU'], n),
    'diagnosis':         np.random.choice(['Hypertension','Diabetes','Fracture','Stroke','Pneumonia','Appendicitis','Cancer','COVID-19'], n),
    'patient_age':       np.random.randint(1, 95, n),
    'patient_gender':    np.random.choice(['Male','Female'], n),
    'length_of_stay':    np.random.randint(1, 30, n),
    'treatment_cost':    np.random.uniform(500, 80000, n).round(2),
    'insurance_type':    np.random.choice(['Private','Medicare','Medicaid','Uninsured'], n),
    'readmitted':        np.random.choice([0,1], n, p=[0.85,0.15]),
    'outcome':           np.random.choice(['Discharged','Transferred','Deceased','Admitted'], n, p=[0.70,0.15,0.05,0.10]),
    'num_procedures':    np.random.randint(1, 10, n),
    'satisfaction_score':np.random.randint(1, 11, n)
})
healthcare_df['age_group'] = pd.cut(healthcare_df['patient_age'],
                                     bins=[0,17,35,60,95],
                                     labels=['Child','Young Adult','Adult','Senior'])
healthcare_df.to_csv('data/healthcare_data.csv', index=False)
print(" Healthcare dataset created")

print("\n All 4 datasets saved to /data folder!")
