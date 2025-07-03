# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import os

# --------------------------------------------------
# Page settings
# --------------------------------------------------
st.set_page_config(
    page_title="Revenue Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# Helper functions
# --------------------------------------------------
CSV_FILE = "data_Conversions.csv"        # file must sit next to dashboard.py


def load_data(csv_file: str) -> pd.DataFrame:
    """Read the CSV and return a cleaned dataframe."""
    file_path = os.path.join(os.path.dirname(__file__), csv_file)
    if not os.path.exists(file_path):
        st.error(f"❌  '{csv_file}' not found. Make sure it’s in the same folder as dashboard.py.")
        st.stop()

    df = pd.read_csv(file_path)

    # Normalise column names (lower-case, no spaces)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # If the CSV uses slightly different headings, map them here
    rename_map = {
        "region": "country",
        "month": "update_as"
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    return df


def to_number(val):
    """Strip $, commas etc. and convert to float."""
    if pd.isna(val):
        return np.nan
    val = str(val).replace("$", "").replace(",", "").strip()
    try:
        return float(val)
    except ValueError:
        return np.nan


def extract_month(update_as: str) -> str:
    """Convert 'Apr 2025' or 'April 2025' -> 'Apr'."""
    for fmt in ("%b %Y", "%B %Y"):
        try:
            return datetime.strptime(update_as, fmt).strftime("%b")
        except ValueError:
            continue
    return None


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and enrich the raw dataframe to drive the charts."""
    df = df.copy()

    df["revenue"] = df["revenue"].apply(to_number)
    df["endpoints"] = pd.to_numeric(df["endpoints"], errors="coerce")
    if "cpl" in df.columns:
        df["cpl"] = df["cpl"].apply(to_number)

    df["month"] = df["update_as"].apply(lambda x: extract_month(str(x)))
    df = df[df["month"].notna()]  # drop rows where month couldn’t be parsed

    df["deployment"] = (
        df["product"].astype(str)
        .str.lower()
        .apply(lambda x: "Cloud" if "cloud" in x else "On-Premises")
    )
    df["edition_simple"] = df["edition"].astype(str).str.split(" ").str[0]

    return df


# --------------------------------------------------
# Load & prepare data
# --------------------------------------------------
raw_df = load_data(CSV_FILE)
processed_df = process_data(raw_df)

if processed_df.empty:
    st.warning("No usable rows after cleaning – please verify your CSV.")
    st.stop()

# --------------------------------------------------
# CSS (same styling as before)
# --------------------------------------------------
st.markdown(
    """
    <style>
        .metric-card {
            background:#f8f9fa;
            border-radius:5px;
            padding:20px;
            box-shadow:0 1px 3px rgba(0,0,0,.12),0 1px 2px rgba(0,0,0,.24);
            text-align:center;
        }
        .metric-title{font-size:18px;font-weight:500;color:#333;}
        .metric-value{font-size:24px;font-weight:700;margin-top:10px;}
        .chart-container{
            background:white;border-radius:5px;padding:15px;
            box-shadow:0 1px 3px rgba(0,0,0,.12),0 1px 2px rgba(0,0,0,.24);
            margin-bottom:20px;
        }
        .blue-bg{background:#e6f3ff;}
        .green-bg{background:#e6fff0;}
        .yellow-bg{background:#fffde6;}
        .purple-bg{background:#f2e6ff;}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Revenue Analytics Dashboard")

# --------------------------------------------------
# KPI calculations
# --------------------------------------------------
total_revenue = processed_df["revenue"].sum()
total_endpoints = processed_df["endpoints"].sum()

unique_domains = processed_df[["domain", "type"]].drop_duplicates()
paid_leads = unique_domains[unique_domains["type"] == "Purchased"].shape[0]
zero_cost_leads = unique_domains[unique_domains["type"] == "Zero Cost"].shape[0]

revenue_by_lead_type = processed_df.groupby("type")["revenue"].sum().reset_index()

avg_revenue_per_paid = (
    revenue_by_lead_type.loc[revenue_by_lead_type["type"] == "Purchased", "revenue"].sum() / paid_leads
    if paid_leads else 0
)
avg_revenue_per_zero_cost = (
    revenue_by_lead_type.loc[revenue_by_lead_type["type"] == "Zero Cost", "revenue"].sum() / zero_cost_leads
    if zero_cost_leads else 0
)

# --------------------------------------------------
# KPI cards
# --------------------------------------------------
k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(
        f"""
        <div class="metric-card blue-bg">
            <div class="metric-title">Total Revenue</div>
            <div class="metric-value">${total_revenue:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k2:
    st.markdown(
        f"""
        <div class="metric-card green-bg">
            <div class="metric-title">Total Endpoints</div>
            <div class="metric-value">{int(total_endpoints):,}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k3:
    st.markdown(
        f"""
        <div class="metric-card yellow-bg">
            <div class="metric-title">Lead Types</div>
            <div class="metric-value">{paid_leads} Paid / {zero_cost_leads} Zero-Cost</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

k4, k5 = st.columns(2)
with k4:
    st.markdown(
        f"""
        <div class="metric-card purple-bg">
            <div class="metric-title">Avg. Revenue per Paid Lead</div>
            <div class="metric-value">${avg_revenue_per_paid:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k5:
    st.markdown(
        f"""
        <div class="metric-card blue-bg">
            <div class="metric-title">Avg. Revenue per Zero-Cost Lead</div>
            <div class="metric-value">${avg_revenue_per_zero_cost:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# --------------------------------------------------
# Charts
# --------------------------------------------------
# Month ordering helper
month_order = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

# ---------- Monthly Revenue ----------
monthly_revenue = (
    processed_df.groupby("month")["revenue"].sum().reset_index()
    .assign(month_num=lambda d: d["month"].map(month_order))
    .sort_values("month_num")
)

c1, c2 = st.columns(2)
with c1:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Monthly Revenue")

    fig = px.bar(
        monthly_revenue,
        x="month",
        y="revenue",
        text_auto=".2s",
        color_discrete_sequence=["#4F46E5"],
        labels={"month": "", "revenue": "Revenue ($)"},
    )
    fig.update_layout(
        plot_bgcolor="white",
        hovermode="closest",
        margin=dict(t=10, l=10, r=10, b=10),
        height=350,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Monthly Customer Acquisition ----------
monthly_acquisition = (
    processed_df.groupby(["month", "type"]).size().unstack(fill_value=0).reset_index()
)
if {"Purchased", "Zero Cost"}.issubset(monthly_acquisition.columns):
    monthly_acquisition["month_num"] = monthly_acquisition["month"].map(month_order)
    monthly_acquisition = monthly_acquisition.sort_values("month_num")

    with c2:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("Monthly Customer Acquisition")

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=monthly_acquisition["month"],
                y=monthly_acquisition["Purchased"],
                name="Paid",
                marker_color="#4F46E5",
            )
        )
        fig.add_trace(
            go.Bar(
                x=monthly_acquisition["month"],
                y=monthly_acquisition["Zero Cost"],
                name="Zero-Cost",
                marker_color="#10B981",
            )
        )
        fig.update_layout(
            barmode="stack",
            plot_bgcolor="white",
            hovermode="closest",
            margin=dict(t=10, l=10, r=10, b=10),
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ---------- Revenue by Lead Type ----------
c1, c2 = st.columns(2)

revenue_by_lead_type["percentage"] = (
    revenue_by_lead_type["revenue"] / total_revenue * 100
)
