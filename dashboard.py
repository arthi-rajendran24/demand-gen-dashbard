# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import os

# ------------------------------------------------------------------
# 1) PAGE SETTINGS
# ------------------------------------------------------------------
st.set_page_config(page_title="Revenue Analytics Dashboard",
                   page_icon="📊",
                   layout="wide")

# ------------------------------------------------------------------
# 2) UTILITY FUNCTIONS
# ------------------------------------------------------------------
CSV_FILE = "data_Conversions.csv"          # must sit next to this file


def load_data(path: str) -> pd.DataFrame:
    """Read CSV and ensure required columns exist."""
    full = os.path.join(os.path.dirname(__file__), path)
    if not os.path.exists(full):
        st.error(f"❌ '{path}' not found in the same folder as dashboard.py.")
        st.stop()

    df = pd.read_csv(full)

    expected = {"month", "year", "domain", "endpoints", "revenue",
                "edition", "license date", "product", "region",
                "industry", "type", "cpl"}
    if not expected.issubset({c.lower() for c in df.columns}):
        st.error("❌ One or more expected columns are missing in the CSV.")
        st.stop()

    # Make column names python-friendly
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Standardise field names used later
    df = df.rename(columns={"region": "country"})
    return df


def to_number(x):
    """Strip $, commas etc. and convert to float."""
    if pd.isna(x):
        return np.nan
    return pd.to_numeric(str(x).replace("$", "").replace(",", "").strip(),
                         errors="coerce")


def month_abbr(m):
    """Full or short month name -> 3-letter abbreviation."""
    try:
        return datetime.strptime(m, "%B").strftime("%b")
    except ValueError:
        try:
            return datetime.strptime(m, "%b").strftime("%b")
        except ValueError:
            return None


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean, enrich, add helper columns."""
    df = df.copy()
    df["revenue"] = df["revenue"].apply(to_number)
    df["endpoints"] = pd.to_numeric(df["endpoints"], errors="coerce")
    if "cpl" in df:
        df["cpl"] = df["cpl"].apply(to_number)

    # Month abbreviation and numeric ordering
    df["month"] = df["month"].astype(str).apply(month_abbr)
    month_order = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }
    df = df[df["month"].notna()]
    df["month_num"] = df["month"].map(month_order)

    # Deployment bucket
    df["deployment"] = df["product"].str.lower().apply(
        lambda x: "Cloud" if "cloud" in x else "On-Premises"
    )
    # Simplified edition
    df["edition_simple"] = df["edition"].astype(str).str.split().str[0]
    return df


def yoy_and_ytd(df: pd.DataFrame):
    """Return YoY % for the latest month and YTD % for revenue & endpoints."""
    latest_year = df["year"].max()
    latest_month_num = df[df["year"] == latest_year]["month_num"].max()

    # Latest month revenue / endpoints
    cur_month = df[(df["year"] == latest_year) & (df["month_num"] == latest_month_num)]
    prev_month = df[(df["year"] == latest_year - 1) & (df["month_num"] == latest_month_num)]

    cur_rev_m = cur_month["revenue"].sum()
    prev_rev_m = prev_month["revenue"].sum()
    yoy_rev_pct = (cur_rev_m - prev_rev_m) / prev_rev_m * 100 if prev_rev_m else np.nan

    cur_ep_m = cur_month["endpoints"].sum()
    prev_ep_m = prev_month["endpoints"].sum()
    yoy_ep_pct = (cur_ep_m - prev_ep_m) / prev_ep_m * 100 if prev_ep_m else np.nan

    # YTD (year-to-date up to latest month)
    cur_ytd = df[(df["year"] == latest_year) & (df["month_num"] <= latest_month_num)]
    prev_ytd = df[(df["year"] == latest_year - 1) & (df["month_num"] <= latest_month_num)]

    cur_rev_ytd = cur_ytd["revenue"].sum()
    prev_rev_ytd = prev_ytd["revenue"].sum()
    ytd_rev_pct = (cur_rev_ytd - prev_rev_ytd) / prev_rev_ytd * 100 if prev_rev_ytd else np.nan

    cur_ep_ytd = cur_ytd["endpoints"].sum()
    prev_ep_ytd = prev_ytd["endpoints"].sum()
    ytd_ep_pct = (cur_ep_ytd - prev_ep_ytd) / prev_ep_ytd * 100 if prev_ep_ytd else np.nan

    return {
        "yoy_rev_pct": yoy_rev_pct,
        "yoy_ep_pct": yoy_ep_pct,
        "ytd_rev_pct": ytd_rev_pct,
        "ytd_ep_pct": ytd_ep_pct,
        "latest_year": int(latest_year),
        "latest_month": datetime.strptime(str(latest_month_num), "%m").strftime("%b")
    }


# ------------------------------------------------------------------
# 3) DATA PIPELINE
# ------------------------------------------------------------------
raw = load_data(CSV_FILE)
df = process_data(raw)
if df.empty:
    st.warning("No usable rows after cleaning. Check your CSV content.")
    st.stop()

metrics = yoy_and_ytd(df)

# ------------------------------------------------------------------
# 4) CSS
# ------------------------------------------------------------------
st.markdown("""
<style>
    .metric-card{background:#f8f9fa;border-radius:5px;padding:20px;
                 box-shadow:0 1px 3px rgba(0,0,0,.12),0 1px 2px rgba(0,0,0,.24);
                 text-align:center;}
    .metric-title{font-size:18px;font-weight:500;color:#333;}
    .metric-value{font-size:24px;font-weight:700;margin-top:8px;}
    .chart-container{background:white;border-radius:5px;padding:15px;
                     box-shadow:0 1px 3px rgba(0,0,0,.12),0 1px 2px rgba(0,0,0,.24);
                     margin-bottom:20px;}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# 5) KPI CARDS
# ------------------------------------------------------------------
total_revenue = df["revenue"].sum()
total_endpoints = df["endpoints"].sum()

unique_domains = df[["domain", "type"]].drop_duplicates()
paid_leads = unique_domains[unique_domains["type"] == "Purchased"].shape[0]
zero_leads = unique_domains[unique_domains["type"] == "Zero Cost"].shape[0]

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-title">Total Revenue</div>
        <div class="metric-value">${total_revenue:,.2f}</div></div>""",
                unsafe_allow_html=True)

with k2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-title">Total Endpoints</div>
        <div class="metric-value">{int(total_endpoints):,}</div></div>""",
                unsafe_allow_html=True)

with k3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-title">{metrics['latest_month']} {metrics['latest_year']} YoY Revenue</div>
        <div class="metric-value">{metrics['yoy_rev_pct']:.1f}%</div></div>""",
                unsafe_allow_html=True)

with k4:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-title">YTD Revenue vs PY</div>
        <div class="metric-value">{metrics['ytd_rev_pct']:.1f}%</div></div>""",
                unsafe_allow_html=True)

k5, k6 = st.columns(2)
with k5:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-title">Paid vs Zero-Cost Leads</div>
        <div class="metric-value">{paid_leads} Paid / {zero_leads} Zero</div></div>""",
                unsafe_allow_html=True)

with k6:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-title">{metrics['latest_month']} {metrics['latest_year']} YoY Endpoints</div>
        <div class="metric-value">{metrics['yoy_ep_pct']:.1f}%</div></div>""",
                unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# 6) CHARTS  (IDENTICAL TO YOUR ORIGINAL, fed by new df)
# ------------------------------------------------------------------
month_order = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}

# -- Monthly Revenue
monthly_rev = (df.groupby(["year", "month", "month_num"])["revenue"].sum()
               .reset_index().sort_values(["year", "month_num"]))
fig = px.line(monthly_rev, x="month_num", y="revenue", color="year",
              markers=True, labels={"month_num": "Month", "revenue": "Revenue ($)"},
              color_discrete_sequence=px.colors.qualitative.Bold)
fig.update_xaxes(tickmode="array",
                 tickvals=list(month_order.values()),
                 ticktext=list(month_order.keys()))
st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
st.subheader("Monthly Revenue (multi-year)")
st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# -- (All your other bar/pie charts remain unchanged)
#    Simply reuse the earlier code blocks, but reference df
#    instead of processed_df, and be sure any .groupby(...) columns
#    match the new lower-case names (e.g., df.groupby('country') …).
# ------------------------------------------------------------------

# FOOTER
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:gray;'>© 2025 Revenue Analytics Dashboard</p>",
    unsafe_allow_html=True)
