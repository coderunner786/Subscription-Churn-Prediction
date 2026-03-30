Part A: Problem Framing Document
1. Business Objective
The primary objective is to build an end-to-end analytics and predictive system to mitigate rising subscriber attrition. By identifying high-risk users 14 days before their subscription expires, we aim to deploy targeted retention interventions that stabilize Monthly Recurring Revenue (MRR) and increase long-term Customer Lifetime Value (LTV).

2. North Star Metric
Net Revenue Retention (NRR): This metric tracks the percentage of recurring revenue retained from the existing customer base over time. It is the definitive measure of our product’s ability to keep and grow its current revenue stream.

3. Supporting KPIs
To monitor the health of the subscription lifecycle and the drivers of churn, the following KPIs will be tracked:

Weekly/Monthly Churn Rate: Percentage of total subscribers who exit the platform.

Cohort Retention Rate: The percentage of users from a specific signup month who remain active in subsequent months.

Renewal Success Rate: Ratio of successful payments to total renewal attempts in payments.csv.

Payment Failure Rate: Percentage of churn caused by technical or financial failures (Involuntary Churn).

Average Usage Intensity: Weekly average of minutes_used and feature_events per user.

Revenue Lost (Proxy): The total financial value of subscriptions associated with cancelled or expired users.

Campaign Response Rate: The percentage of "at-risk" users who renew after receiving a renewal_reminder or content_nudge.

4. Churn Definition
A user is explicitly classified as CHURNED if they meet either of the following criteria:

The subscription status in subscriptions.csv is "cancelled".

OR the subscription status is "expired" and no successful renewal payment is recorded in payments.csv within a 5-day grace period following the end_date.

5. Scope & Windows
Observation Window: 30 days of historical behavioral data (Usage, Payments, and Touchpoints) will be analyzed to identify predictors of churn.

Lead Time: 7 days. We will ignore data from the final 7 days before the churn event to ensure the model captures "early-warning" signs rather than the churn event itself.

Prediction Window: The model will predict the probability of churn for the next 14 days, providing a sufficient window for the marketing team to act.

6. Stakeholder Questions
The data solution will answer the following business-critical questions:

Engagement Thresholds: Is there a specific level of "usage decay" (e.g., a 30% drop in minutes) that serves as the most reliable predictor of churn?

Involuntary vs. Voluntary: What percentage of our churn is caused by failed payments (expired) versus active user cancellations (cancelled)?

The "Cliff" Point: At which billing cycle (Month 1, 3, or 6) do we see the most significant drop-off in user retention?

Feature Stickiness: Which specific features in usage_daily.csv are most correlated with long-term retention?

Retention ROI: Which campaign_type (e.g., renewal_reminder vs. content_nudge) provides the highest lift in renewal probability?

Channel Quality: Do users acquired through specific channels (e.g., paid_social vs. organic) exhibit different churn patterns?

Capstone Project: Subscription Churn Analysis & Recovery
1. Project Overview
This project identifies the root causes of a significant 35.4% churn spike observed in January 2026. Using a Python-based ETL pipeline and a Random Forest predictive model, we developed a targeted retention strategy to recover ₹20,930 in monthly revenue by identifying 660 High-Risk users.

2. Churn Definition & Prediction Horizon
Churn Definition: A user is classified as CHURNED if their subscription is "cancelled" OR "expired" without a successful renewal payment within a 5-day grace period.

Prediction Horizon: The model predicts churn probability for the next 14 days.

Lead Time: A 7-day lead time is incorporated to allow the marketing team sufficient time for intervention before the actual churn event.

3. Technical Setup & How to Run ETL
To reproduce the analysis and curated datasets, ensure you have Python installed and follow these steps:

Step 1: Install Dependencies

Bash
pip install pandas numpy scikit-learn matplotlib seaborn
Step 2: Run the ETL Pipeline
Navigate to the root directory and execute the script to process raw CSVs:

Bash
python etl/etl_pipeline.py
Step 3: Run the Analysis
Open analysis/analysis.ipynb in Jupyter Notebook and select Kernel > Restart & Run All to view the model performance and impact tables.

4. Curated Outputs Generated
The ETL pipeline generates the following files in the /data/ folder:

dim_users_enriched.csv: Cleaned user profiles with tenure and engagement bands (Low/Med/High).

fact_user_weekly.csv: Weekly aggregated usage and technical failure metrics.

model_churn_dataset.csv: Flattened dataset used for ML training and evaluation.

weekly_trends_tableau.csv: Time-series export for Tableau trend visualizations.

5. Dashboard Details
Tool Used: Tableau Desktop

File Path: /dashboard/Retention_Dashboard.twbx

Navigation: The workbook contains 4 Views:

Executive Summary: Visualizes the Jan 2026 churn spike and core KPIs.

Cohort Analysis: Tracks retention rates by signup week.

Driver Diagnostics: Maps the correlation between Payment Failures and Churn.

Model & Targeting: Lists the 660 High-Risk users for the recovery plan.

6. Impact Summary
Identified High-Risk Segment: 660 Users

Target Recovery (Base Case): 70 Users (10.6% of segment)

Monthly Revenue Saved: ₹20,930

Annualized Revenue Recovery: ₹1,87,716

7. Folder Structure
_Capstone_SubscriptionChurn/
├── README.md
├── /data/                # Curated CSVs
├── /etl/                 # etl_pipeline.py
├── /analysis/            # analysis.ipynb
├── /dashboard/           # .twbx and /dashboard_screenshots/
└── /final_story/         # final_memo.pdf