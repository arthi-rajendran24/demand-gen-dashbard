# revenue_dashboard.py  ─────────────────────────────────────────────────────────
# A fully self-contained Streamlit dashboard that loads data_Conversions.csv
# (or a file you upload) and visualises revenue, endpoints, lead types, etc.
# ───────────────────────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ───────────────────────────────────────────────────────────────────────────────
# Streamlit page configuration
# ───────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Revenue Dashboard", page_icon="📊", layout="wide")

# ───────────────────────────────────────────────────────────────────────────────
# Custom CSS
# ───────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        .metric-card {
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
            text-align: center;
        }
        .metric-title { font-size: 18px; font-weight: 500; color: #333; }
        .metric-value { font-size: 24px; font-weight: 700; margin-top: 10px; }
        .chart-container {
            background-color: white; border-radius: 5px; padding: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
            margin-bottom: 20px;
        }
        .blue-bg   { background-color: #e6f3ff; }
        .green-bg  { background-color: #e6fff0; }
        .yellow-bg { background-color: #fffde6; }
        .purple-bg { background-color: #f2e6ff; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ───────────────────────────────────────────────────────────────────────────────
# 1│ LOAD DATA (CSV or user upload)
# ───────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data(default_path: str = "data_Conversions.csv") -> pd.DataFrame:
    """
    • Reads default CSV if present.
    • If user uploads a CSV via sidebar, use that instead.
    • Normalises column names → lower_snake_case.
    """
    upload = st.sidebar.file_uploader("⬆️ Upload a CSV (optional override)", type="csv")
    if upload is not None:
        df = pd.read_csv(upload)
    else:
        df = pd.read_csv(default_path)

    # Standardise column names (e.g. "License Date" → "license_date")
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )
    return df


df_raw = load_data()

# ───────────────────────────────────────────────────────────────────────────────
# 2│ PROCESS DATA
# ───────────────────────────────────────────────────────────────────────────────
def process_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Numeric conversions
    if "revenue" in df.columns:
        df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
    if "endpoints" in df.columns:
        df["endpoints"] = pd.to_numeric(df["endpoints"], errors="coerce")

    # Month extraction from update_as (e.g. "Jan 2025" → "Jan")
    if "update_as" in df.columns:
        df["update_as"] = df["update_as"].astype(str)
        df["month"] = df["update_as"].str.split().str[0]

    # Cloud / On-Prem flag
    if "product" in df.columns:
        df["product"] = df["product"].astype(str)
        df["deployment"] = df["product"].str.lower().apply(
            lambda x: "Cloud" if "cloud" in x else "On-Premises"
        )

    # Simplified edition
    if "edition" in df.columns:
        df["edition"] = df["edition"].astype(str)
        df["edition_simple"] = df["edition"].str.split().str[0]

    return df


df = process_data(df_raw)

# ───────────────────────────────────────────────────────────────────────────────
# 3│ DASHBOARD TITLE
# ───────────────────────────────────────────────────────────────────────────────
st.title("Revenue Analytics Dashboard")

# ───────────────────────────────────────────────────────────────────────────────
# 4│ KPI METRICS
# ───────────────────────────────────────────────────────────────────────────────
total_revenue   = df["revenue"].sum()
total_endpoints = df["endpoints"].sum()

unique_domains  = df[["domain", "type"]].drop_duplicates()
paid_leads      = unique_domains[unique_domains["type"] == "Purchased"].shape[0]
zero_cost_leads = unique_domains[unique_domains["type"] == "Zero Cost"].shape[0]

revenue_by_lead_type = df.groupby("type")["revenue"].sum().reset_index()
avg_revenue_per_paid = (
    revenue_by_lead_type.loc[revenue_by_lead_type["type"] == "Purchased", "revenue"].iloc[0]
    / paid_leads
    if paid_leads
    else 0
)
avg_revenue_per_zero = (
    revenue_by_lead_type.loc[revenue_by_lead_type["type"] == "Zero Cost", "revenue"].iloc[0]
    / zero_cost_leads
    if zero_cost_leads
    else 0
)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f"""<div class="metric-card blue-bg">
               <div class="metric-title">Total Revenue</div>
               <div class="metric-value">${total_revenue:,.2f}</div>
           </div>""",
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f"""<div class="metric-card green-bg">
               <div class="metric-title">Total Endpoints</div>
               <div class="metric-value">{int(total_endpoints):,}</div>
           </div>""",
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f"""<div class="metric-card yellow-bg">
               <div class="metric-title">Lead Types</div>
               <div class="metric-value">{paid_leads} Paid / {zero_cost_leads} Zero-Cost</div>
           </div>""",
        unsafe_allow_html=True,
    )

col4, col5 = st.columns(2)
with col4:
    st.markdown(
        f"""<div class="metric-card purple-bg">
               <div class="metric-title">Avg. Revenue Per Paid Lead</div>
               <div class="metric-value">${avg_revenue_per_paid:,.2f}</div>
           </div>""",
        unsafe_allow_html=True,
    )
with col5:
    st.markdown(
        f"""<div class="metric-card blue-bg">
               <div class="metric-title">Avg. Revenue Per Zero-Cost Lead</div>
               <div class="metric-value">${avg_revenue_per_zero:,.2f}</div>
           </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────────────────────
# 5│ CHARTS
# ───────────────────────────────────────────────────────────────────────────────
# Month mapping for proper order
month_order = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

# Monthly Revenue
monthly_rev = df.groupby("month")["revenue"].sum().reset_index()
monthly_rev["month_num"] = monthly_rev["month"].map(month_order)
monthly_rev = monthly_rev.sort_values("month_num")

# Monthly Customer Acquisition
monthly_acq = df.groupby(["month", "type"]).size().unstack(fill_value=0).reset_index()
if "Purchased" not in monthly_acq.columns:
    monthly_acq["Purchased"] = 0
if "Zero Cost" not in monthly_acq.columns:
    monthly_acq["Zero Cost"] = 0
monthly_acq["month_num"] = monthly_acq["month"].map(month_order)
monthly_acq = monthly_acq.sort_values("month_num")

# ---- Row 1 charts ----
c1, c2 = st.columns(2)

with c1:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Monthly Revenue")
    fig = px.bar(
        monthly_rev,
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

with c2:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Monthly Customer Acquisition")
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=monthly_acq["month"],
            y=monthly_acq["Purchased"],
            name="Paid",
            marker_color="#4F46E5",
        )
    )
    fig.add_trace(
        go.Bar(
            x=monthly_acq["month"],
            y=monthly_acq["Zero Cost"],
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

# ---- Row 2 charts ----
c3, c4 = st.columns(2)

# Revenue by Lead Type pie
revenue_by_lead_type["percentage"] = (revenue_by_lead_type["revenue"] / total_revenue * 100).round(1)
with c3:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Revenue by Lead Type")
    fig = px.pie(
        revenue_by_lead_type,
        values="revenue",
        names="type",
        hole=0.4,
        color_discrete_sequence=["#0088FE", "#00C49F"],
        labels={"type": "Lead Type", "revenue": "Revenue ($)"},
    )
    fig.update_traces(textinfo="percent+label", textposition="outside")
    fig.update_layout(
        annotations=[dict(text=f'${total_revenue:,.0f}', x=0.5, y=0.5, font_size=15, showarrow=False)],
        margin=dict(t=10, l=10, r=10, b=10),
        height=350,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Revenue by Country pie
revenue_by_country = df.groupby("country")["revenue"].sum().reset_index()
revenue_by_country["percentage"] = (revenue_by_country["revenue"] / total_revenue * 100).round(1)
revenue_by_country = revenue_by_country.sort_values("revenue", ascending=False)
with c4:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Revenue by Country")
    fig = px.pie(
        revenue_by_country,
        values="revenue",
        names="country",
        hole=0.4,
        color_discrete_sequence=["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#A28BFC", "#FF6B6B"],
        labels={"country": "Country", "revenue": "Revenue ($)"},
    )
    fig.update_traces(textinfo="percent+label", textposition="outside")
    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=350)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---- Row 3 charts ----
c5, c6 = st.columns(2)

# Revenue by Edition pie
if "edition_simple" in df.columns:
    rev_by_edition = df.groupby("edition_simple")["revenue"].sum().reset_index()
    rev_by_edition["percentage"] = (rev_by_edition["revenue"] / total_revenue * 100).round(1)
    with c5:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("Revenue by Edition")
        fig = px.pie(
            rev_by_edition,
            values="revenue",
            names="edition_simple",
            hole=0.4,
            color_discrete_sequence=["#0088FE", "#00C49F", "#FFBB28", "#FF8042"],
            labels={"edition_simple": "Edition", "revenue": "Revenue ($)"},
        )
        fig.update_traces(textinfo="percent+label", textposition="outside")
        fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=350)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Revenue by Deployment pie
if "deployment" in df.columns:
    rev_by_deployment = df.groupby("deployment")["revenue"].sum().reset_index()
    rev_by_deployment["percentage"] = (rev_by_deployment["revenue"] / total_revenue * 100).round(1)
    with c6:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("Revenue by Deployment")
        fig = px.pie(
            rev_by_deployment,
            values="revenue",
            names="deployment",
            hole=0.4,
            color_discrete_sequence=["#0088FE", "#00C49F"],
            labels={"deployment": "Deployment", "revenue": "Revenue ($)"},
        )
        fig.update_traces(textinfo="percent+label", textposition="outside")
        fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=350)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Revenue by Product bar
st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
st.subheader("Revenue by Product")
rev_by_product = df.groupby("product")["revenue"].sum().reset_index().sort_values("revenue", ascending=False)
fig = px.bar(
    rev_by_product,
    y="product",
    x="revenue",
    orientation="h",
    color_discrete_sequence=["#4F46E5"],
    labels={"product": "", "revenue": "Revenue ($)"},
)
fig.update_layout(
    plot_bgcolor="white",
    hovermode="closest",
    margin=dict(t=10, l=150, r=10, b=10),
    height=400,
    yaxis={"categoryorder": "total ascending"},
)
st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# Revenue by Industry pie (top 6 + Other)
rev_by_industry = df.groupby("industry")["revenue"].sum().reset_index()
rev_by_industry["percentage"] = (rev_by_industry["revenue"] / total_revenue * 100).round(1)
rev_by_industry = rev_by_industry.sort_values("revenue", ascending=False)
top_industries = rev_by_industry.head(6)
if len(rev_by_industry) > 6:
    other = pd.DataFrame(
        {
            "industry": ["Other"],
            "revenue": [rev_by_industry["revenue"].iloc[6:].sum()],
            "percentage": [rev_by_industry["percentage"].iloc[6:].sum()],
        }
    )
    top_industries = pd.concat([top_industries, other], ignore_index=True)

st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
st.subheader("Revenue by Industry")
fig = px.pie(
    top_industries,
    values="revenue",
    names="industry",
    hole=0.4,
    color_discrete_sequence=["#FF3EA5", "#FF5E5B", "#FFDB4C", "#00E396", "#0073FF", "#7C4DFF", "#775DD0"],
    labels={"industry": "Industry", "revenue": "Revenue ($)"},
)
fig.update_traces(textinfo="percent+label", textposition="outside")
fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=400)
st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# Endpoint Size Distribution
ranges = [
    (0, 100), (101, 200), (201, 300), (301, 400), (401, 500),
    (501, 600), (601, 700), (701, 800), (801, 900),
    (901, 999), (1000, 1499), (1500, 1999), (2000, 2499), (2500, float("inf")),
]
labels = [
    "0-100", "101-200", "201-300", "301-400", "401-500",
    "501-600", "601-700", "701-800", "801-900",
    "901+", "1000+", "1500+", "2000+", "2500+",
]
dist = []
for i, (lo, hi) in enumerate(ranges):
    cnt = df[(df["endpoints"] >= lo) & (df["endpoints"] <= hi)].shape[0]
    if cnt:
        dist.append({"range": labels[i], "count": cnt})
dist_df = pd.DataFrame(dist)
if not dist_df.empty:
    dist_df["order"] = dist_df["range"].map({lab: i for i, lab in enumerate(labels)})
    dist_df = dist_df.sort_values("order")

    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Endpoint Size Distribution")
    fig = px.bar(
        dist_df,
        x="range",
        y="count",
        color_discrete_sequence=["#FF8042"],
        labels={"range": "Size Range", "count": "Count"},
    )
    fig.update_layout(
        plot_bgcolor="white",
        hovermode="closest",
        margin=dict(t=10, l=10, r=10, b=10),
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Top 10 Domains by record count
domain_count = df["domain"].value_counts().reset_index()
domain_count.columns = ["domain", "count"]
domain_count = domain_count[domain_count["domain"].str.strip() != ""].head(10)
if not domain_count.empty:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Top 10 Domains by Entries")
    fig = px.bar(
        domain_count,
        y="domain",
        x="count",
        orientation="h",
        color_discrete_sequence=["#00C49F"],
        labels={"domain": "", "count": "Number of Entries"},
    )
    fig.update_layout(
        plot_bgcolor="white",
        hovermode="closest",
        margin=dict(t=10, l=250, r=10, b=10),
        height=400,
        yaxis={"categoryorder": "total ascending"},
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────────────────────
# Footer
# ───────────────────────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:gray;'>© 2025 Revenue Analytics Dashboard</p>",
    unsafe_allow_html=True,
)
