# dashboard.py  –  Revenue Analytics Dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import os

# ─────────────────────────────────────────────────────────────
# 1. PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Revenue Analytics Dashboard",
                   page_icon="📊",
                   layout="wide")

# ─────────────────────────────────────────────────────────────
# 2. DATA HELPERS
# ─────────────────────────────────────────────────────────────
CSV_FILE = "data_Conversions.csv"          # must sit next to this script


def load_data(path: str) -> pd.DataFrame:
    fp = os.path.join(os.path.dirname(__file__), path)
    if not os.path.exists(fp):
        st.error(f"❌  '{path}' not found. Place it beside dashboard.py.")
        st.stop()

    df = pd.read_csv(fp)

    # normalise headers
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df = df.rename(columns={"region": "country"})   # keep legacy name

    expected = {
        "month", "year", "domain", "endpoints", "revenue", "edition",
        "license_date", "product", "country", "industry", "type", "cpl"
    }
    if not expected.issubset(df.columns):
        st.error("❌  Expected columns missing in the CSV.")
        st.stop()
    return df


def to_number(x):
    if pd.isna(x):
        return np.nan
    return pd.to_numeric(
        str(x).replace("$", "").replace(",", "").strip(), errors="coerce"
    )


def month_abbr(m: str) -> str:
    for fmt in ("%B", "%b"):
        try:
            return datetime.strptime(m, fmt).strftime("%b")
        except ValueError:
            continue
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
    df["cpl"]     = df["cpl"].apply(to_number)
    df["endpoints"] = pd.to_numeric(df["endpoints"], errors="coerce")

    # month handling
    df["month"] = df["month"].astype(str).apply(month_abbr)
    month_map = {m: i for i, m in enumerate(
        ["Jan","Feb","Mar","Apr","May","Jun",
         "Jul","Aug","Sep","Oct","Nov","Dec"], 1)}
    df = df[df["month"].notna()]
    df["month_num"] = df["month"].map(month_map)

    # derived cols
    df["deployment"] = df["product"].astype(str).str.lower().apply(
        lambda s: "Cloud" if "cloud" in s else "On-Premises")
    df["edition_simple"] = (
        df["edition"].astype(str)
          .str.split().str[0]        # <-- Series-aware split
          .fillna("Unknown")
    )
    df["type"] = df["type"].apply(normalise_type)
    return df


def compute_metrics(df: pd.DataFrame) -> dict:
    """Return YoY %, YTD %, latest-month revenue, etc."""
    yr_latest = df["year"].max()
    mo_latest = df[df["year"] == yr_latest]["month_num"].max()

    cur_m  = df[(df["year"] == yr_latest) & (df["month_num"] == mo_latest)]
    prev_m = df[(df["year"] == yr_latest - 1) &
                (df["month_num"] == mo_latest)]

    pct = lambda cur, prev: (cur - prev) / prev * 100 if prev else np.nan

    yoy_rev = pct(cur_m["revenue"].sum(),  prev_m["revenue"].sum())
    yoy_ep  = pct(cur_m["endpoints"].sum(), prev_m["endpoints"].sum())

    cur_ytd  = df[(df["year"] == yr_latest) &
                  (df["month_num"] <= mo_latest)]
    prev_ytd = df[(df["year"] == yr_latest - 1) &
                  (df["month_num"] <= mo_latest)]

    ytd_rev = pct(cur_ytd["revenue"].sum(),  prev_ytd["revenue"].sum())
    ytd_ep  = pct(cur_ytd["endpoints"].sum(), prev_ytd["endpoints"].sum())

    month_str = datetime.strptime(str(mo_latest), "%m").strftime("%b")

    return dict(
        latest_year=int(yr_latest),
        latest_month=month_str,
        latest_month_rev=cur_m["revenue"].sum(),
        yoy_rev=yoy_rev,
        yoy_ep=yoy_ep,
        ytd_rev=ytd_rev,
        ytd_ep=ytd_ep
    )


# ─────────────────────────────────────────────────────────────
# 3. LOAD & PREP DATA
# ─────────────────────────────────────────────────────────────
df = process_data(load_data(CSV_FILE))
if df.empty:
    st.warning("No usable rows after cleaning. Check your CSV.")
    st.stop()

M = compute_metrics(df)

# ─────────────────────────────────────────────────────────────
# 4. GLOBAL CSS (pretty cards)
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
:root{
  --blue:#4F46E5;
  --emerald:#10B981;
  --amber:#F59E0B;
  --pink:#EC4899;
  --slate:#64748B;
}
.metric-card{
  position:relative;
  padding:26px 28px 22px;
  background:#fff;
  border-left:6px solid var(--accent, var(--slate));
  border-radius:12px;
  box-shadow:0 4px 12px rgba(0,0,0,.08);
  transition:transform .15s ease, box-shadow .15s ease;
}
.metric-card:hover{
  transform:translateY(-4px);
  box-shadow:0 8px 20px rgba(0,0,0,.12);
}
.metric-card::before{
  content:"";
  position:absolute;
  width:110px;
  height:110px;
  top:-35px; right:-35px;
  background:var(--accent, var(--slate));
  opacity:.12;
  border-radius:50%;
}
.metric-title{
  font-size:16px;
  font-weight:600;
  color:#475569;
  margin-bottom:4px;
}
.metric-sub{
  font-size:13px;
  color:#64748B;
  margin-bottom:8px;
}
.metric-value{
  font-size:28px;
  font-weight:800;
  color:#1F2937;
}
.chart-container{
  background:#fff;
  border-radius:8px;
  padding:15px;
  box-shadow:0 1px 3px rgba(0,0,0,.12),
             0 1px 2px rgba(0,0,0,.24);
  margin-bottom:20px;
}
</style>
""", unsafe_allow_html=True)

st.title("Revenue Analytics Dashboard")

# ─────────────────────────────────────────────────────────────
# 5. KPI CARDS (refreshed design)
# ─────────────────────────────────────────────────────────────
def kpi(title:str, value:str, sub:str|None=None,
        accent:str="var(--blue)") -> str:
    sub_html = (f'<div class="metric-sub">{sub}</div>' if sub else "")
    return (f'<div class="metric-card" style="--accent:{accent}">'
            f'<div class="metric-title">{title}</div>'
            f'{sub_html}'
            f'<div class="metric-value">{value}</div>'
            f'</div>')


# ---- data for cards ----
total_rev        = f"${df['revenue'].sum():,.2f}"
latest_month_lbl = f"{M['latest_month']} {M['latest_year']}"
latest_rev       = f"${M['latest_month_rev']:,.2f}"
total_eps        = f"{int(df['endpoints'].sum()):,}"
yoy_rev_pct      = f"{M['yoy_rev']:.1f}%"
ytd_rev_pct      = f"{M['ytd_rev']:.1f}%"
yoy_ep_pct       = f"{M['yoy_ep']:.1f}%"

# lead counts
unique_leads = df[["domain", "type"]].drop_duplicates()
paid_leads   = (unique_leads["type"] == "Purchased").sum()
zero_leads   = (unique_leads["type"] == "Zero Cost").sum()
lead_ratio   = f"{paid_leads} / {zero_leads}"

# ---------- ROW-1 ----------
c1,c2,c3,c4,c5 = st.columns(5)
c1.markdown(kpi("Total Revenue", total_rev,
                accent="var(--blue)"), unsafe_allow_html=True)
c2.markdown(kpi("Latest-Month Revenue", latest_rev, latest_month_lbl,
                accent="var(--pink)"), unsafe_allow_html=True)
c3.markdown(kpi("Total Endpoints", total_eps,
                accent="var(--emerald)"), unsafe_allow_html=True)
c4.markdown(kpi(f"{latest_month_lbl} YoY Revenue", yoy_rev_pct,
                accent="var(--amber)"), unsafe_allow_html=True)
c5.markdown(kpi("YTD Revenue vs PY", ytd_rev_pct,
                accent="var(--slate)"), unsafe_allow_html=True)

# ---------- ROW-2 ----------
d1,d2 = st.columns(2)
d1.markdown(kpi("Paid vs Zero-Cost Leads", lead_ratio,
                accent="var(--blue)"), unsafe_allow_html=True)
d2.markdown(kpi(f"{latest_month_lbl} YoY Endpoints", yoy_ep_pct,
                accent="var(--emerald)"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# 6. CHARTS  (identical to previous version)
# ─────────────────────────────────────────────────────────────
mo_order = {m:i for i,m in enumerate(
    ["Jan","Feb","Mar","Apr","May","Jun","Jul",
     "Aug","Sep","Oct","Nov","Dec"], 1)}

# 6-1  Monthly Revenue by Year
rev_line = (df.groupby(["year","month","month_num"])["revenue"]
              .sum().reset_index().sort_values(["year","month_num"]))
fig = px.line(rev_line, x="month_num", y="revenue", color="year",
              markers=True,
              labels={"month_num":"Month","revenue":"Revenue ($)"},
              color_discrete_sequence=px.colors.qualitative.Bold)
fig.update_xaxes(tickmode="array",
                 tickvals=list(mo_order.values()),
                 ticktext=list(mo_order.keys()))
st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
st.subheader("Monthly Revenue by Year")
st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# 6-2  Monthly Customer Acquisition
acq = (df.groupby(["year","month","month_num","type"]).size()
         .reset_index(name="count"))
last_two = sorted(df["year"].unique())[-2:]
acq = acq[acq["year"].isin(last_two)]
pivot = (acq.pivot_table(index=["year","month","month_num"],
                         columns="type", values="count",
                         fill_value=0).reset_index())
st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
st.subheader("Monthly Customer Acquisition (Paid vs Zero-Cost)")
for yr in last_two:
    sub = pivot[pivot["year"] == yr].sort_values("month_num")
    fg = go.Figure()
    fg.add_trace(go.Bar(x=sub["month"], y=sub.get("Purchased",0),
                        name="Paid", marker_color="#4F46E5"))
    fg.add_trace(go.Bar(x=sub["month"], y=sub.get("Zero Cost",0),
                        name="Zero-Cost", marker_color="#10B981"))
    fg.update_layout(barmode="stack",
                     title=str(yr),
                     plot_bgcolor="white",
                     showlegend=(yr == last_two[0]),
                     margin=dict(t=40,l=10,r=10,b=10), height=300)
    st.plotly_chart(fg, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ── quick pie helper
def pie(title, data, names, values, seq):
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader(title)
    f = px.pie(data, names=names, values=values,
               hole=.4, color_discrete_sequence=seq)
    f.update_traces(textinfo="percent+label", textposition="outside")
    f.update_layout(margin=dict(t=10,l=10,r=10,b=10), height=350)
    st.plotly_chart(f, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# 6-3  Lead-type pie
pie("Revenue by Lead Type",
    df.groupby("type")["revenue"].sum().reset_index(),
    "type","revenue",["#0088FE","#00C49F"])

# 6-4  Country pie
pie("Revenue by Country",
    df.groupby("country")["revenue"].sum()
      .reset_index().sort_values("revenue",ascending=False),
    "country","revenue",px.colors.qualitative.Pastel)

# 6-5  Edition pie
pie("Revenue by Edition",
    df.groupby("edition_simple")["revenue"].sum().reset_index(),
    "edition_simple","revenue",
    ["#0088FE","#00C49F","#FFBB28","#FF8042"])

# 6-6  Deployment pie
pie("Revenue by Deployment",
    df.groupby("deployment")["revenue"].sum().reset_index(),
    "deployment","revenue",
    ["#0088FE","#00C49F"])

# 6-7  Product bar
prod = (df.groupby("product")["revenue"].sum()
          .reset_index().sort_values("revenue",ascending=False))
st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
st.subheader("Revenue by Product")
fig = px.bar(prod, y="product", x="revenue", orientation="h",
             color_discrete_sequence=["#4F46E5"])
fig.update_layout(plot_bgcolor="white",
                  margin=dict(t=10,l=200,r=10,b=10),
                  height=450,
                  yaxis={"categoryorder":"total ascending"})
st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# 6-8  Industry pie
ind = (df.groupby("industry")["revenue"].sum()
         .reset_index().sort_values("revenue",ascending=False))
ind_top = ind.head(6)
if len(ind) > 6:
    ind_top = pd.concat([
        ind_top,
        pd.DataFrame({"industry":["Other"],
                      "revenue":[ind["revenue"].iloc[6:].sum()]})
    ], ignore_index=True)
pie("Revenue by Industry", ind_top, "industry", "revenue",
    px.colors.qualitative.Set3)

# 6-9  Endpoint size distribution
bins = [
    (0,100),(101,200),(201,300),(301,400),(401,500),
    (501,600),(601,700),(701,800),(801,900),
    (901,999),(1000,1499),(1500,1999),(2000,2499),
    (2500,2999),(3000,4999),(5000,9999),(10000, float("inf"))
]
labels = [
    "0-100","101-200","201-300","301-400","401-500",
    "501-600","601-700","701-800","801-900",
    "901+","1000+","1500+","2000+","2500+",
    "3000+","5000+","10000+"
]
dist = [
    {
        "range": lab,
        "count": df[(df["endpoints"]>=lo)&(df["endpoints"]<=hi)].shape[0]
    }
    for (lo,hi),lab in zip(bins,labels)
    if df[(df["endpoints"]>=lo)&(df["endpoints"]<=hi)].shape[0]
]
if dist:
    ddf = pd.DataFrame(dist)
    ddf["order"] = ddf["range"].apply(labels.index)
    ddf = ddf.sort_values("order")
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Endpoint Size Distribution")
    f = px.bar(ddf, x="range", y="count",
               color_discrete_sequence=["#FF8042"])
    f.update_layout(plot_bgcolor="white",
                    margin=dict(t=10,l=10,r=10,b=40),
                    height=400)
    st.plotly_chart(f, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# 6-10  Top 10 Domains
top_dom = df["domain"].value_counts().head(10).reset_index()
top_dom.columns = ["domain","count"]
if not top_dom.empty:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Top 10 Domains by Frequency")
    f = px.bar(top_dom, y="domain", x="count", orientation="h",
               color_discrete_sequence=["#00C49F"])
    f.update_layout(plot_bgcolor="white",
                    margin=dict(t=10,l=250,r=10,b=40),
                    height=450,
                    yaxis={"categoryorder":"total ascending"})
    st.plotly_chart(f, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# 7. FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:gray;'>© 2025 Revenue Analytics Dashboard</p>",
    unsafe_allow_html=True
)
