# revenue_dashboard.py  ─────────────────────────────────────────────────────────
# Streamlit dashboard for demand-gen / revenue analytics
# Robust to missing columns & alternate header spellings.
# ───────────────────────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ───────────────────────────────────────────────────────────────────────────────
# Page config + CSS
# ───────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Revenue Dashboard", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
        .metric-card {background:#f8f9fa;border-radius:5px;padding:20px;
                      box-shadow:0 1px 3px rgba(0,0,0,0.12),
                                 0 1px 2px rgba(0,0,0,0.24);text-align:center;}
        .metric-title {font-size:18px;font-weight:500;color:#333;}
        .metric-value {font-size:24px;font-weight:700;margin-top:10px;}
        .chart-container {background:#fff;border-radius:5px;padding:15px;
                          box-shadow:0 1px 3px rgba(0,0,0,0.12),
                                     0 1px 2px rgba(0,0,0,0.24);margin-bottom:20px;}
        .blue-bg   {background:#e6f3ff;}  .green-bg  {background:#e6fff0;}
        .yellow-bg {background:#fffde6;}  .purple-bg {background:#f2e6ff;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ───────────────────────────────────────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────────────────────────────────────
def has_col(df: pd.DataFrame, col: str) -> bool:
    """Return True if `col` exists and isn’t completely NaN / empty."""
    return col in df.columns and df[col].notna().any()


# ───────────────────────────────────────────────────────────────────────────────
# 1│ LOAD DATA
# ───────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data(default_csv: str = "data_Conversions.csv") -> pd.DataFrame:
    """Read local CSV, or override with user-uploaded file."""
    up = st.sidebar.file_uploader("⬆️  Upload a CSV (optional)", type="csv")
    df = pd.read_csv(up) if up else pd.read_csv(default_csv)

    # Normalise headers → lower_snake_case
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )

    # Map common alternate column names → canonical
    alt_cols = {
        "countryname": "country",
        "nation": "country",
        "region": "country",
        "license_date": "license_date",  # keep; just shows how to add others
    }
    df.rename(columns=alt_cols, inplace=True)

    return df


df_raw = load_data()

# ───────────────────────────────────────────────────────────────────────────────
# 2│ PROCESS DATA
# ───────────────────────────────────────────────────────────────────────────────
def process_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Numeric conversions
    for col in ("revenue", "endpoints"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Month label from update_as
    if has_col(df, "update_as"):
        df["update_as"] = df["update_as"].astype(str)
        df["month"] = df["update_as"].str.split().str[0]

    # Deployment: Cloud vs On-Prem
    if has_col(df, "product"):
        df["product"] = df["product"].astype(str)
        df["deployment"] = df["product"].str.lower().apply(
            lambda x: "Cloud" if "cloud" in x else "On-Premises"
        )

    # Simplified edition
    if has_col(df, "edition"):
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
total_revenue   = df["revenue"].sum()         if has_col(df, "revenue")   else 0
total_endpoints = df["endpoints"].sum()       if has_col(df, "endpoints") else 0

paid_leads = zero_cost_leads = 0
if has_col(df, "domain") and has_col(df, "type"):
    uniq = df[["domain", "type"]].drop_duplicates()
    paid_leads      = uniq[uniq["type"] == "Purchased"].shape[0]
    zero_cost_leads = uniq[uniq["type"] == "Zero Cost"].shape[0]

# Revenue by lead type
if has_col(df, "type") and has_col(df, "revenue"):
    rev_by_type = df.groupby("type")["revenue"].sum().reset_index()
else:
    rev_by_type = pd.DataFrame(columns=["type", "revenue"])

avg_paid = (
    rev_by_type.loc[rev_by_type["type"] == "Purchased", "revenue"].iloc[0] / paid_leads
    if paid_leads and not rev_by_type.empty
    else 0
)
avg_zero = (
    rev_by_type.loc[rev_by_type["type"] == "Zero Cost", "revenue"].iloc[0] / zero_cost_leads
    if zero_cost_leads and not rev_by_type.empty
    else 0
)

# KPI cards
k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(
        f"""<div class="metric-card blue-bg">
                <div class="metric-title">Total Revenue</div>
                <div class="metric-value">${total_revenue:,.2f}</div>
            </div>""",
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        f"""<div class="metric-card green-bg">
                <div class="metric-title">Total Endpoints</div>
                <div class="metric-value">{int(total_endpoints):,}</div>
            </div>""",
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        f"""<div class="metric-card yellow-bg">
                <div class="metric-title">Lead Types</div>
                <div class="metric-value">{paid_leads} Paid / {zero_cost_leads} Zero-Cost</div>
            </div>""",
        unsafe_allow_html=True,
    )

k4, k5 = st.columns(2)
with k4:
    st.markdown(
        f"""<div class="metric-card purple-bg">
                <div class="metric-title">Avg. Revenue Per Paid Lead</div>
                <div class="metric-value">${avg_paid:,.2f}</div>
            </div>""",
        unsafe_allow_html=True,
    )
with k5:
    st.markdown(
        f"""<div class="metric-card blue-bg">
                <div class="metric-title">Avg. Revenue Per Zero-Cost Lead</div>
                <div class="metric-value">${avg_zero:,.2f}</div>
            </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────────────────────
# 5│ CHARTS
# ───────────────────────────────────────────────────────────────────────────────
# Month ordering
month_order = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

# Monthly revenue
if has_col(df, "month") and has_col(df, "revenue"):
    m_rev = df.groupby("month")["revenue"].sum().reset_index()
    m_rev["order"] = m_rev["month"].map(month_order)
    m_rev = m_rev.sort_values("order")
else:
    m_rev = pd.DataFrame(columns=["month", "revenue"])

# Monthly customer acquisition
if has_col(df, "month") and has_col(df, "type"):
    m_acq = df.groupby(["month", "type"]).size().unstack(fill_value=0).reset_index()
    for col in ("Purchased", "Zero Cost"):
        if col not in m_acq.columns:
            m_acq[col] = 0
    m_acq["order"] = m_acq["month"].map(month_order)
    m_acq = m_acq.sort_values("order")
else:
    m_acq = pd.DataFrame(columns=["month", "Purchased", "Zero Cost"])

# Row 1: Monthly revenue & acquisition
c1, c2 = st.columns(2)
with c1:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Monthly Revenue")
    fig = px.bar(
        m_rev, x="month", y="revenue", text_auto=".2s",
        color_discrete_sequence=["#4F46E5"],
        labels={"month": "", "revenue": "Revenue ($)"}
    )
    fig.update_layout(plot_bgcolor="white", hovermode="closest",
                      margin=dict(t=10, l=10, r=10, b=10), height=350)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Monthly Customer Acquisition")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=m_acq["month"], y=m_acq.get("Purchased", []),
        name="Paid", marker_color="#4F46E5")
    )
    fig.add_trace(go.Bar(
        x=m_acq["month"], y=m_acq.get("Zero Cost", []),
        name="Zero-Cost", marker_color="#10B981")
    )
    fig.update_layout(
        barmode="stack", plot_bgcolor="white", hovermode="closest",
        margin=dict(t=10, l=10, r=10, b=10), height=350
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Row 2: Lead-type pie & country pie
c3, c4 = st.columns(2)

with c3:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Revenue by Lead Type")
    fig = px.pie(
        rev_by_type, values="revenue", names="type", hole=0.4,
        color_discrete_sequence=["#0088FE", "#00C49F"],
        labels={"type": "Lead Type", "revenue": "Revenue ($)"}
    )
    fig.update_traces(textinfo="percent+label", textposition="outside")
    fig.update_layout(
        annotations=[dict(text=f'${total_revenue:,.0f}', x=0.5, y=0.5,
                          font_size=15, showarrow=False)],
        margin=dict(t=10, l=10, r=10, b=10), height=350
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Revenue by country (guarded)
if has_col(df, "country") and has_col(df, "revenue"):
    rev_country = (
        df.groupby("country")["revenue"].sum().reset_index()
        .sort_values("revenue", ascending=False)
    )
    rev_country["pct"] = (rev_country["revenue"] / rev_country["revenue"].sum() * 100).round(1)

    with c4:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("Revenue by Country")
        fig = px.pie(
            rev_country, values="revenue", names="country", hole=0.4,
            color_discrete_sequence=[
                "#0088FE", "#00C49F", "#FFBB28", "#FF8042",
                "#A28BFC", "#FF6B6B", "#775DD0"
            ],
            labels={"country": "Country", "revenue": "Revenue ($)"}
        )
        fig.update_traces(textinfo="percent+label", textposition="outside")
        fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=350)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
else:
    with c4:
        st.info("📍 No ‘country’ column found in this file.")

# Row 3: Edition & Deployment pies
c5, c6 = st.columns(2)

if has_col(df, "edition_simple") and has_col(df, "revenue"):
    rev_edition = df.groupby("edition_simple")["revenue"].sum().reset_index()
    rev_edition["pct"] = (rev_edition["revenue"] / total_revenue * 100).round(1)
    with c5:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("Revenue by Edition")
        fig = px.pie(
            rev_edition, values="revenue", names="edition_simple", hole=0.4,
            color_discrete_sequence=["#0088FE", "#00C49F", "#FFBB28", "#FF8042"],
            labels={"edition_simple": "Edition", "revenue": "Revenue ($)"}
        )
        fig.update_traces(textinfo="percent+label", textposition="outside")
        fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=350)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
else:
    with c5:
        st.info("Edition breakdown unavailable.")

if has_col(df, "deployment") and has_col(df, "revenue"):
    rev_deploy = df.groupby("deployment")["revenue"].sum().reset_index()
    with c6:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("Revenue by Deployment")
        fig = px.pie(
            rev_deploy, values="revenue", names="deployment", hole=0.4,
            color_discrete_sequence=["#0088FE", "#00C49F"],
            labels={"deployment": "Deployment", "revenue": "Revenue ($)"}
        )
        fig.update_traces(textinfo="percent+label", textposition="outside")
        fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=350)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
else:
    with c6:
        st.info("Deployment breakdown unavailable.")

# Revenue by product
if has_col(df, "product") and has_col(df, "revenue"):
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Revenue by Product")
    rev_prod = (
        df.groupby("product")["revenue"].sum()
        .reset_index()
        .sort_values("revenue", ascending=False)
    )
    fig = px.bar(
        rev_prod, y="product", x="revenue", orientation="h",
        color_discrete_sequence=["#4F46E5"],
        labels={"product": "", "revenue": "Revenue ($)"}
    )
    fig.update_layout(
        plot_bgcolor="white", hovermode="closest",
        margin=dict(t=10, l=150, r=10, b=10), height=400,
        yaxis={"categoryorder": "total ascending"}
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Revenue by industry
if has_col(df, "industry") and has_col(df, "revenue"):
    rev_ind = df.groupby("industry")["revenue"].sum().reset_index()
    rev_ind = rev_ind.sort_values("revenue", ascending=False)
    top_ind = rev_ind.head(6)
    if len(rev_ind) > 6:
        other = pd.DataFrame(
            {"industry": ["Other"], "revenue": [rev_ind["revenue"].iloc[6:].sum()]}
        )
        top_ind = pd.concat([top_ind, other], ignore_index=True)

    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Revenue by Industry")
    fig = px.pie(
        top_ind, values="revenue", names="industry", hole=0.4,
        color_discrete_sequence=[
            "#FF3EA5", "#FF5E5B", "#FFDB4C", "#00E396",
            "#0073FF", "#7C4DFF", "#775DD0"
        ],
        labels={"industry": "Industry", "revenue": "Revenue ($)"}
    )
    fig.update_traces(textinfo="percent+label", textposition="outside")
    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Endpoint size distribution
if has_col(df, "endpoints"):
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
    dist = [
        {"range": labels[i],
         "count": df[(df["endpoints"] >= lo) & (df["endpoints"] <= hi)].shape[0]}
        for i, (lo, hi) in enumerate(ranges)
        if df[(df["endpoints"] >= lo) & (df["endpoints"] <= hi)].shape[0] > 0
    ]
    if dist:
        dist_df = pd.DataFrame(dist)
        dist_df["order"] = dist_df["range"].map({lab: i for i, lab in enumerate(labels)})
        dist_df = dist_df.sort_values("order")

        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("Endpoint Size Distribution")
        fig = px.bar(
            dist_df, x="range", y="count",
            color_discrete_sequence=["#FF8042"],
            labels={"range": "Size Range", "count": "Count"},
        )
        fig.update_layout(
            plot_bgcolor="white", hovermode="closest",
            margin=dict(t=10, l=10, r=10, b=10), height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Top domains by frequency
if has_col(df, "domain"):
    d_cnt = df["domain"].value_counts().reset_index()
    d_cnt.columns = ["domain", "count"]
    d_cnt = d_cnt[d_cnt["domain"].str.strip() != ""].head(10)
    if not d_cnt.empty:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("Top 10 Domains by Entries")
        fig = px.bar(
            d_cnt, y="domain", x="count", orientation="h",
            color_discrete_sequence=["#00C49F"],
            labels={"domain": "", "count": "Entries"},
        )
        fig.update_layout(
            plot_bgcolor="white", hovermode="closest",
            margin=dict(t=10, l=250, r=10, b=10), height=400,
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
