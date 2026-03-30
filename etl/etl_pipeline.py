import pandas as pd
import numpy as np
from datetime import timedelta

# 1. LOAD DATA
def load_data():
    users = pd.read_csv('users.csv')
    plans = pd.read_csv('plans.csv')
    subs = pd.read_csv('subscriptions.csv')
    payments = pd.read_csv('payments.csv')
    usage = pd.read_csv('usage_daily.csv')
    return users, plans, subs, payments, usage

# 2. CLEAN & STANDARDIZE
def clean_data(users, subs, payments, usage):
    # De-duplicate
    users = users.drop_duplicates(subset=['user_id'])
    subs = subs.drop_duplicates()
    payments = payments.drop_duplicates()
    usage = usage.drop_duplicates()
    
    # Normalize Casing (Addresses meta.json issues)
    payments['payment_status'] = payments['payment_status'].str.upper()
    
    # Handle Outliers in Usage (Top 0.15% as per meta.json)
    q_limit = usage['minutes_used'].quantile(0.9985)
    usage['minutes_used'] = np.where(usage['minutes_used'] > q_limit, q_limit, usage['minutes_used'])
    
    # Fill Missing preferred_device
    users['preferred_device'] = users['preferred_device'].fillna('unknown')
    
    return users, subs, payments, usage

# 3. PRODUCE OUTPUT 1: dim_users_enriched.csv
def create_dim_users(users, subs, usage):
    # Calculate Last Active Date
    last_act = usage.groupby('user_id')['date'].max().rename('last_active_date')
    
    # Calculate Lifetime Paid Months (Proxy using successful payments)
    # Join with users to get tenure
    enriched = users.merge(last_act, on='user_id', how='left')
    enriched['signup_date'] = pd.to_datetime(enriched['signup_date'])
    enriched['last_active_date'] = pd.to_datetime(enriched['last_active_date'])
    enriched['tenure_days'] = (enriched['last_active_date'] - enriched['signup_date']).dt.days
    
    # Engagement Band Logic
    avg_usage = usage.groupby('user_id')['minutes_used'].mean()
    enriched = enriched.merge(avg_usage.rename('avg_daily_min'), on='user_id', how='left')
    enriched['engagement_band'] = pd.qcut(enriched['avg_daily_min'].fillna(0), 3, labels=["low", "med", "high"])
    
    return enriched.drop(columns=['avg_daily_min'])

# 4. PRODUCE OUTPUT 2: fact_user_weekly.csv
def create_fact_weekly(usage, payments, subs):
    usage['date'] = pd.to_datetime(usage['date'])
    usage['week_start'] = usage['date'].dt.to_period('W').apply(lambda r: r.start_time)
    
    # Weekly Usage Aggregates
    weekly_usage = usage.groupby(['user_id', 'week_start']).agg(
        active_days_week=('minutes_used', lambda x: (x > 0).sum()),
        total_minutes_week=('minutes_used', 'sum'),
        sessions_week=('sessions_count', 'sum')
    ).reset_index()
    
    # Weekly Payment Signals
    payments['payment_date'] = pd.to_datetime(payments['payment_date'])
    payments['week_start'] = payments['payment_date'].dt.to_period('W').apply(lambda r: r.start_time)
    weekly_pay = payments.groupby(['user_id', 'week_start']).agg(
        payment_attempts_week=('payment_id', 'count'),
        payment_failures_week=('payment_status', lambda x: (x == 'FAILED').sum())
    ).reset_index()
    
    return pd.merge(weekly_usage, weekly_pay, on=['user_id', 'week_start'], how='outer').fillna(0)

# 5. PRODUCE OUTPUT 3: model_churn_dataset.csv
def create_model_dataset(subs, fact_weekly):
    # Reference date for the "As-of" snapshot (end of the observation period)
    as_of_date = pd.to_datetime('2026-01-30')
    
    # Labeling: will_churn_14d
    # 1 if status is cancelled/expired within the next 14 days
    subs['end_date'] = pd.to_datetime(subs['end_date'])
    subs['will_churn_14d'] = np.where(
        (subs['status'].isin(['cancelled', 'expired'])) & 
        (subs['end_date'] <= as_of_date + timedelta(days=14)), 1, 0
    )
    
    # Feature engineering: Last Week vs Avg of Previous 3 Weeks
    # This logic would involve shifting the weekly fact table to get trends.
    # For now, we take the latest stats per user.
    latest_stats = fact_weekly.sort_values('week_start').groupby('user_id').tail(1)
    
    model_df = subs[['user_id', 'plan_price', 'will_churn_14d']].merge(latest_stats, on='user_id')
    return model_df

# RUN PIPELINE
u, p_l, s, p_a, us = load_data()
u, s, p_a, us = clean_data(u, s, p_a, us)

dim_users = create_dim_users(u, s, us)
fact_weekly = create_fact_weekly(us, p_a, s)
model_data = create_model_dataset(s, fact_weekly)

# SAVE OUTPUTS TO /data/ folder
dim_users.to_csv('data/dim_users_enriched.csv', index=False)
fact_weekly.to_csv('data/fact_user_weekly.csv', index=False)
model_data.to_csv('data/model_churn_dataset.csv', index=False)

print("ETL complete. 3 files generated in /data/")