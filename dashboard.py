# dashboard.py  ──────────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import os

# ────────────────────────────────────────────────────────────────────────────
# 1. PAGE CONFIG
# ────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Revenue Analytics Dashboard",
                   page_icon="📊",
                   layout="wide")

# ────────────────────────────────────────────────────────────────────────────
# 2. HELPERS
# ────────────────────────────────────────────────────────────────────────────
CSV_FILE = "data_Conversions.csv"               # must sit beside this script


def load_data(path: str) -> pd.DataFrame:
    full = os.path.join(os.path.dirname(__file__), path)
    if not os.path.exists(full):
        st.error(f"❌  '{path}' not found. Place it in the same folder as dashboard.py.")
        st.stop()

    df = pd.read_csv(full)

    # rename to pythonic lowercase_with_underscores
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # expected columns check
    expected = {"month", "year", "domain", "endpoints", "revenue", "edition",
                "license_date", "product", "region", "industry", "type", "cpl"}
    if not expected.issubset(df.columns):
        st.error("❌  One or more expected columns are missing in the CSV.")
        st.stop()

    df = df.rename(columns={"region": "country"})   # match old code
    return df


def to_number(x):
    if pd.isna(x):
        return np.nan
    return pd.to_numeric(str(x).replace("$", "").replace(",", "").strip(),
                         errors="coerce")


def month_abbr(m):
    try:
        return datetime.strptime(m, "%B").strftime("%b")
    except ValueError:
        try:
            return datetime.strptime(m, "%b").strftime("%b")
        except ValueError:
            return None


def normalise_type(x: str) -> str:
    x = str(x).strip().lower()
    if x in {"0", "zero", "zero cost", "zero-cost"}:
        return "Zero Cost"
    if x in {"1", "purchased", "paid"}:
        return "Purchased"
    return x.title()


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # numeric conversions
    df["revenue"] = df["revenue"].apply(to_number)
    df["endpoints"] = pd.to_numeric(df["endpoints"], errors="coerce")
    df["cpl"] = df["cpl"].apply(to_number)

    # month handling
    df["month"] = df["month"].astype(str).apply(month_abbr)
    month_order = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }
    df = df[df["month"].notna()]
    df["month_num"] = df["month"].map(month_order)

    # extra helper columns
    df["deployment"] = df["product"].str.lower().apply(
        lambda s: "Cloud" if "cloud" in s else "On-Premises")
    df["edition_simple"] = df["edition"].astype(str).str.split().str[0]
    df["type"] = df["type"].apply(normalise_type)

    return df


def yoy_ytd_metrics(df: pd.DataFrame) -> dict:
    latest_year = df["year"].max()
    latest_month_num = df[df["year"] == latest_year]["month_num"].max()

    # Current & previous year same month
    cur_month = df[(df["year"] == latest_year) & (df["month_num"] == latest_month_num)]
    prev_month = df[(df["year"] == latest_year - 1) & (df["month_num"] == latest_month_num)]

    # Calculations helper
    def pct(cur, prev):
        return (cur - prev) / prev * 100 if prev else np.nan

    yoy_rev = pct(cur_month["revenue"].sum(), prev_month["revenue"].sum())
    yoy_ep = pct(cur_month["endpoints"].sum(), prev_month["endpoints"].sum())

    # YTD (up to latest month)
    cur_ytd = df[(df["year"] == latest_year) & (df["month_num"] <= latest_month_num)]
    prev_ytd = df[(df["year"] == latest_year - 1) & (df["month_num"] <= latest_month_num)]
    ytd_rev = pct(cur_ytd["revenue"].sum(), prev_ytd["revenue"].sum())
    ytd_ep = pct(cur_ytd["endpoints"].sum(), prev_ytd["endpoints"].sum())

    latest_month = datetime.strptime(str(latest_month_num), "%m").strftime("%b")
    return dict(yoy_rev=yoy_rev, yoy_ep=yoy_ep,
                ytd_rev=ytd_rev, ytd_ep=ytd_ep,
                latest_month=latest_month, latest_year=int(latest_year))


# ────────────────────────────────────────────────────────────────────────────
# 3. LOAD & PREP DATA
# ────────────────────────────────────────────────────────────────────────────
raw_df = load_data(CSV_FILE)
df = process_data(raw_df)
if df.empty:
    st.warning("No usable rows after cleaning – please check your CSV.")
    st.stop()

metrics = yoy_ytd_metrics(df)

# ────────────────────────────────────────────────────────────────────────────
# 4. CSS
# ────────────────────────────────────────────────────────────────────────────
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
</style>""", unsafe_allow_html=True)

st.title("Revenue Analytics Dashboard")

# ────────────────────────────────────────────────────────────────────────────
# 5. KPI CARDS
# ────────────────────────────────────────────────────────────────────────────
total_rev = df["revenue"].sum()
total_ep = df["endpoints"].sum()

unique_domains = df[["domain", "type"]].drop_duplicates()
paid_leads = unique_domains[unique_domains["type"] == "Purchased"].shape[0]
zero_leads = unique_domains[unique_domains["type"] == "Zero Cost"].shape[0]

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-title">Total Revenue</div>
        <div class="metric-value">${total_rev:,.2f}</div></div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-title">Total Endpoints</div>
        <div class="metric-value">{int(total_ep):,}</div></div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-title">{metrics['latest_month']} {metrics['latest_year']} YoY Revenue</div>
        <div class="metric-value">{metrics['yoy_rev']:.1f}%</div></div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-title">YTD Revenue vs PY</div>
        <div class="metric-value">{metrics['ytd_rev']:.1f}%</div></div>""", unsafe_allow_html=True)

k5, k6 = st.columns(2)
with k5:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-title">Paid vs Zero-Cost Leads</div>
        <div class="metric-value">{paid_leads} / {zero_leads}</div></div>""", unsafe_allow_html=True)
with k6:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-title">{metrics['latest_month']} {metrics['latest_year']} YoY Endpoints</div>
        <div class="metric-value">{metrics['yoy_ep']:.1f}%</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────────────────
# 6. CHARTS
# ────────────────────────────────────────────────────────────────────────────
month_order = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}

# --- 6.1 Monthly Revenue (multi-year) ------------
monthly_rev = (df.groupby(["year", "month", "month_num"])["revenue"].sum()
                 .reset_index().sort_values(["year", "month_num"]))
fig = px.line(monthly_rev, x="month_num", y="revenue", color="year",
              markers=True, labels={"month_num": "Month", "revenue": "Revenue ($)"},
              color_discrete_sequence=px.colors.qualitative.Bold)
fig.update_xaxes(tickmode="array",
                 tickvals=list(month_order.values()),
                 ticktext=list(month_order.keys()))
st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
st.subheader("Monthly Revenue by Year")
st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- 6.2 Monthly Customer Acquisition ------------
monthly_acq = (df.groupby(["year", "month", "month_num", "type"]).size()
                 .reset_index(name="count"))
latest_years = sorted(df["year"].unique())[-2:]   # show last 2 yrs for clarity
monthly_acq = monthly_acq[monthly_acq["year"].isin(latest_years)]
acq_pivot = (monthly_acq.pivot_table(index=["year", "month_num", "month"],
                                     columns="type", values="count", fill_value=0)
                           .reset_index())
st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
st.subheader("Monthly Customer Acquisition (Paid vs Zero-Cost)")
for yr in latest_years:
    sub = acq_pivot[acq_pivot["year"] == yr].sort_values("month_num")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=sub["month"], y=sub.get("Purchased", 0),
                         name="Paid", marker_color="#4F46E5"))
    fig.add_trace(go.Bar(x=sub["month"], y=sub.get("Zero Cost", 0),
                         name="Zero-Cost", marker_color="#10B981"))
    fig.update_layout(barmode="stack", title=f"{yr}",
                      plot_bgcolor="white", showlegend=(yr == latest_years[0]),
                      margin=dict(t=40, l=10, r=10, b=10), height=300)
    st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# Helper for repeated chart containers
def pie_card(title, data, names_col, values_col, seq):
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader(title)
    fig = px.pie(data, values=values_col, names=names_col,
                 hole=0.4, color_discrete_sequence=seq)
    fig.update_traces(textinfo="percent+label", textposition="outside")
    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=350)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 6.3 Revenue by Lead Type ---------------------
rev_lead = df.groupby("type")["revenue"].sum().reset_index()
pie_card("Revenue by Lead Type", rev_lead, "type", "revenue",
         ["#0088FE", "#00C49F"])

# --- 6.4 Revenue by Country -----------------------
rev_country = (df.groupby("country")["revenue"].sum()
                 .reset_index().sort_values("revenue", ascending=False))
pie_card("Revenue by Country", rev_country, "country", "revenue",
         px.colors.qualitative.Pastel)

# --- 6.5 Revenue by Edition -----------------------
rev_ed = df.groupby("edition_simple")["revenue"].sum().reset_index()
pie_card("Revenue by Edition", rev_ed, "edition_simple", "revenue",
         ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"])

# --- 6.6 Revenue by Deployment --------------------
rev_dep = df.groupby("deployment")["revenue"].sum().reset_index()
pie_card("Revenue by Deployment", rev_dep, "deployment", "revenue",
         ["#0088FE", "#00C49F"])

# --- 6.7 Revenue by Product -----------------------
rev_prod = (df.groupby("product")["revenue"].sum()
              .reset_index().sort_values("revenue", ascending=False))
st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
st.subheader("Revenue by Product")
fig = px.bar(rev_prod, y="product", x="revenue", orientation="h",
             color_discrete_sequence=["#4F46E5"],
             labels={"product": "", "revenue": "Revenue ($)"})
fig.update_layout(plot_bgcolor="white", hovermode="closest",
                  margin=dict(t=10, l=200, r=10, b=10),
                  height=450, yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- 6.8 Revenue by Industry ----------------------
rev_ind = (df.groupby("industry")["revenue"].sum()
             .reset_index().sort_values("revenue", ascending=False))
# roll up small slices
top6 = rev_ind.head(6)
if len(rev_ind) > 6:
    other = pd.DataFrame({"industry": ["Other"],
                          "revenue": [rev_ind["revenue"].iloc[6:].sum()]})
    top6 = pd.concat([top6, other], ignore_index=True)
pie_card("Revenue by Industry", top6, "industry", "revenue",
         px.colors.qualitative.Set3)

# --- 6.9 Endpoint Size Distribution --------------
bins = [(0, 100), (101, 200), (201, 300), (301, 400), (401, 500),
        (501, 600), (601, 700), (701, 800), (801, 900),
        (901, 999), (1000, 1499), (1500, 1999),
        (2000, 2499), (2500, float("inf"))]
labels = ["0-100", "101-200", "201-300", "301-400", "401-500",
          "501-600", "601-700", "701-800", "801-900",
          "901+", "1000+", "1500+", "2000+", "2500+"]
dist = []
for (lo, hi), lab in zip(bins, labels):
    cnt = df[(df["endpoints"] >= lo) & (df["endpoints"] <= hi)].shape[0]
    if cnt:
        dist.append({"range": lab, "count": cnt})
dist_df = pd.DataFrame(dist).sort_values("range")
if not dist_df.empty:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Endpoint Size Distribution")
    fig = px.bar(dist_df, x="range", y="count",
                 color_discrete_sequence=["#FF8042"],
                 labels={"range": "Size Range", "count": "Count"})
    fig.update_layout(plot_bgcolor="white", hovermode="closest",
                      margin=dict(t=10, l=10, r=10, b=40),
                      height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 6.10 Top 10 Domains -------------------------
top_domains = (df["domain"].value_counts()
                 .head(10).reset_index()
                 .rename(columns={"index": "domain", "domain": "count"}))
if not top_domains.empty:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Top 10 Domains by Frequency")
    fig = px.bar(top_domains, y="domain", x="count", orientation="h",
                 color_discrete_sequence=["#00C49F"],
                 labels={"domain": "", "count": "Entries"})
    fig.update_layout(plot_bgcolor="white", hovermode="closest",
                      margin=dict(t=10, l=250, r=10, b=40),
                      height=450, yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────────────────
# 7. FOOTER
# ────────────────────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:gray;'>© 2025 Revenue Analytics Dashboard</p>",
    unsafe_allow_html=True)
