# dashboard_app.py
"""
Comprehensive Demand-Gen Conversions Dashboard
=============================================
Interactive Streamlit application that surfaces every major insight hiding in
*data_Conversions.csv*.  It lets you slice & dice by time, product, region,
edition, industry, and more—all without exposing raw domain names on their own.

Run:
    streamlit run dashboard_app.py
Dependencies:
    pip install streamlit plotly pandas
--------------------------------------------------------------------
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ────────────────────────────────────────────────────────────────────────────────
# 1. Data loading & cleaning
# ────────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_and_prepare(csv_path: str = "data_Conversions.csv") -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    # Drop the aggregate “Total” row if present
    df = df[df["Month"].str.lower() != "total"].copy()

    # Helpers ────────────────────────────────────────────────────────────────
    def money_to_float(s):
        if pd.isna(s):
            return None
        s = (
            str(s)
            .replace("$", "")
            .replace("₹", "")
            .replace(",", "")
            .replace(" ", "")
        )
        try:
            return float(s)
        except ValueError:
            return None

    df["Revenue ($)"] = df["Revenue"].apply(money_to_float)
    df["CPL ($)"] = df["CPL"].apply(money_to_float)

    # Dates
    df["License Date"] = pd.to_datetime(df["License Date"], dayfirst=True, errors="coerce")
    df["Month (date)"] = pd.to_datetime(df["Month"], format="%b %Y", errors="coerce")
    df["Month Label"] = df["Month (date)"].dt.strftime("%b %Y")  # nice axis labels

    return df


df = load_and_prepare()

# ────────────────────────────────────────────────────────────────────────────────
# 2. Sidebar filters  **FIXED**
# ────────────────────────────────────────────────────────────────────────────────
st.sidebar.header("🔍  Filter Data")

# Convert Timestamp → date so Streamlit’s date_input gets a pure date default
min_date = df["License Date"].dropna().min().date()
max_date = df["License Date"].dropna().max().date()

date_range = st.sidebar.date_input(
    "License Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

edition_sel  = st.sidebar.multiselect("Edition",   sorted(df["Edition"].dropna().unique()))
product_sel  = st.sidebar.multiselect("Product",   sorted(df["Product"].dropna().unique()))
region_sel   = st.sidebar.multiselect("Region",    sorted(df["Region"].dropna().unique()))
industry_sel = st.sidebar.multiselect("Industry",  sorted(df["Industry"].dropna().unique()))
type_sel     = st.sidebar.multiselect("Deal Type", sorted(df["Type"].dropna().unique()))

# --- Normalise the two date types so they match ---
start_ts, end_ts = map(pd.to_datetime, date_range)        # <-- pd.Timestamp objects
license_dates     = df["License Date"]                    # already Timestamp
date_mask         = license_dates.between(start_ts, end_ts)

mask = (
    date_mask
    & (df["Edition"].isin(edition_sel)  if edition_sel  else True)
    & (df["Product"].isin(product_sel)  if product_sel  else True)
    & (df["Region"].isin(region_sel)    if region_sel   else True)
    & (df["Industry"].isin(industry_sel)if industry_sel else True)
    & (df["Type"].isin(type_sel)        if type_sel     else True)
)

f = df.loc[mask].copy()

# ────────────────────────────────────────────────────────────────────────────────
# 3. Global KPIs
# ────────────────────────────────────────────────────────────────────────────────
st.title("📊 Demand-Gen Conversions Dashboard")

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Endpoints", int(f["Endpoints"].sum()))
kpi2.metric("Total Revenue ($)", f["Revenue ($)"].sum())
kpi3.metric("Avg. CPL ($)", round(f["CPL ($)"].mean(), 2))

# ────────────────────────────────────────────────────────────────────────────────
# 4. Deep-dive tabs
# ────────────────────────────────────────────────────────────────────────────────
tab_time, tab_geo, tab_prod, tab_ind = st.tabs(
    ["⏱️ Time Series", "🌍 Geography", "🛠️ Products", "🏭 Industries"]
)

# 4-A  Time-series view ─────────────────────────────────────────────────────────
with tab_time:
    st.subheader("Monthly Revenue & Endpoints")

    time_agg = (
        f.groupby("Month Label", sort=False)
        .agg({"Revenue ($)": "sum", "Endpoints": "sum"})
        .reset_index()
    )

    fig_rev = px.bar(time_agg, x="Month Label", y="Revenue ($)", title="Revenue by Month")
    fig_ep = px.line(
        time_agg,
        x="Month Label",
        y="Endpoints",
        markers=True,
        title="Endpoints by Month",
    )

    st.plotly_chart(fig_rev, use_container_width=True)
    st.plotly_chart(fig_ep, use_container_width=True)

# 4-B  Geographic view ──────────────────────────────────────────────────────────
with tab_geo:
    st.subheader("Revenue by Region")

    geo_agg = (
        f.groupby("Region")
        .agg({"Revenue ($)": "sum", "Endpoints": "sum"})
        .sort_values("Revenue ($)", ascending=False)
        .reset_index()
    )
    fig_region = px.bar(
        geo_agg, x="Region", y="Revenue ($)", hover_data=["Endpoints"], height=500
    )
    st.plotly_chart(fig_region, use_container_width=True)

# 4-C  Product view ─────────────────────────────────────────────────────────────
with tab_prod:
    st.subheader("Product Performance")

    prod_agg = (
        f.groupby("Product")
        .agg({"Revenue ($)": "sum", "Endpoints": "sum"})
        .sort_values("Revenue ($)", ascending=False)
        .reset_index()
    )
    fig_prod = px.treemap(
        prod_agg,
        path=["Product"],
        values="Revenue ($)",
        hover_data=["Endpoints"],
    )
    st.plotly_chart(fig_prod, use_container_width=True)
    st.caption("💡 Tip — hover a rectangle to see endpoints handled per product.")

# 4-D  Industry view ────────────────────────────────────────────────────────────
with tab_ind:
    st.subheader("Industry Landscape")

    ind_agg = (
        f.groupby("Industry")
        .agg({"Revenue ($)": "sum", "Endpoints": "sum"})
        .sort_values("Revenue ($)", ascending=False)
        .reset_index()
    )
    fig_ind = px.scatter(
        ind_agg,
        x="Endpoints",
        y="Revenue ($)",
        size="Revenue ($)",
        color="Industry",
        hover_name="Industry",
        log_x=True,
        title="Endpoints vs Revenue by Industry",
    )
    st.plotly_chart(fig_ind, use_container_width=True)

# 4-E  Account view (no lonely domain names!) ───────────────────────────────────
with tab_acc:
    st.subheader("Top-Grossing Accounts (by Revenue)")

    top_acc = (
        f.groupby("Domain")
        .agg(
            {
                "Revenue ($)": "sum",
                "Endpoints": "sum",
                "Industry": "first",
                "Region": "first",
                "Edition": "first",
            }
        )
        .sort_values("Revenue ($)", ascending=False)
        .head(20)
        .reset_index()
    )

    st.dataframe(
        top_acc.rename(
            columns={
                "Domain": "Account",
                "Revenue ($)": "Revenue ($)",
                "Endpoints": "Endpoints",
            }
        )
    )
