from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Customer Churn Workbench", page_icon="🧭", layout="wide")
st.title("Customer Churn Workbench")
st.caption("Explore retention patterns and prioritize customers using transparent risk signals.")
df = pd.read_csv(Path(__file__).parent / "data" / "customers.csv")
df["risk_score"] = (df.tenure_months.lt(6).astype(int)*30 + df.support_tickets.ge(3).astype(int)*25 + df.payment_delay_days.ge(10).astype(int)*25 + df.contract_type.eq("Monthly").astype(int)*20).clip(0,100)
contracts = st.sidebar.multiselect("Contract types", sorted(df.contract_type.unique()), default=sorted(df.contract_type.unique()))
min_tenure = st.sidebar.slider("Minimum tenure (months)",0,int(df.tenure_months.max()),0)
f = df[df.contract_type.isin(contracts) & df.tenure_months.ge(min_tenure)]
if f.empty: st.warning("No customers match these filters."); st.stop()
a,b,c,d=st.columns(4)
a.metric("Customers",f.customer_id.nunique())
b.metric("Churn rate",f.churn.mean(),delta=f"{(f.churn.mean()-df.churn.mean())*100:+.1f} pp vs all customers")
c.metric("Avg. monthly charge",f.monthly_charges.mean().round(2))
d.metric("High-risk customers",int(f.risk_score.ge(60).sum()))
left,right=st.columns(2)
with left:
 st.subheader("Churn by contract"); st.bar_chart(f.groupby("contract_type").churn.mean())
with right:
 st.subheader("Churn by tenure band"); f2=f.assign(tenure_band=pd.cut(f.tenure_months,[0,6,12,24,60],labels=["0–6","7–12","13–24","25+"])); st.bar_chart(f2.groupby("tenure_band",observed=False).churn.mean())
st.subheader("Customers to review")
review=f.sort_values(["risk_score","monthly_charges"],ascending=False).head(25)
st.dataframe(review, use_container_width=True, hide_index=True)
st.download_button("Download filtered customers",f.to_csv(index=False),"customers.csv","text/csv")
st.info("Risk score is a heuristic for triage, not a prediction of an individual's behavior. Validate it against your own data before operational use.")
