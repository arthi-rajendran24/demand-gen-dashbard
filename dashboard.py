import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Set page config
st.set_page_config(
    page_title="Revenue Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        text-align: center;
    }
    .metric-title {
        font-size: 18px;
        font-weight: 500;
        color: #333;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        margin-top: 10px;
    }
    .chart-container {
        background-color: white;
        border-radius: 5px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        margin-bottom: 20px;
    }
    .blue-bg { background-color: #e6f3ff; }
    .green-bg { background-color: #e6fff0; }
    .yellow-bg { background-color: #fffde6; }
    .purple-bg { background-color: #f2e6ff; }
</style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---

@st.cache_data(ttl=600) # Cache the data for 10 minutes
def load_data(url):
    """Load data from a GitHub URL."""
    try:
        # Assuming the file is a CSV. If it's an Excel file, use pd.read_excel(url)
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Error loading data from GitHub: {e}")
        return pd.DataFrame() # Return empty DataFrame on error

# --- IMPORTANT ---
# 1. Upload your data file (e.g., data.csv) to your GitHub repository.
# 2. Go to the file on GitHub and click the "Raw" button.
# 3. Copy the URL from your browser's address bar.
# 4. Paste the RAW GitHub URL here.
GITHUB_URL = "https://github.com/arthi-rajendran24/demand-gen-dashbard/blob/main/data_Conversions.csv"

# Load the data
df_raw = load_data(GITHUB_URL)

# Stop the app if data loading fails
if df_raw.empty:
    st.warning("Could not load data. Please check the GitHub URL in the code.")
    st.info("Make sure the URL is the 'RAW' link to a CSV or Excel file on a public GitHub repository.")
    st.stop()

# --- END OF DATA LOADING ---

# Title
st.title("Revenue Analytics Dashboard")

# Function to process data
def process_data(df):
    df = df.copy() # Make a copy to avoid SettingWithCopyWarning
    df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')
    df['endpoints'] = pd.to_numeric(df['endpoints'], errors='coerce')
    df['update_as'] = df['update_as'].astype(str)
    df['month'] = df['update_as'].str.split(' ').str[0]
    df['product'] = df['product'].astype(str)
    df['deployment'] = df['product'].str.lower().apply(lambda x: 'Cloud' if 'cloud' in str(x) else 'On-Premises')
    df['edition'] = df['edition'].astype(str)
    df['edition_simple'] = df['edition'].str.split(' ').str[0]
    return df

# Process the loaded data
processed_df = process_data(df_raw)

# --- The rest of your script remains unchanged ---

# Calculate summary statistics
total_revenue = processed_df['revenue'].sum()
total_endpoints = processed_df['endpoints'].sum()

unique_domains = processed_df[['Domain', 'type']].drop_duplicates()
paid_leads = unique_domains[unique_domains['type'] == 'Purchased'].shape[0]
zero_cost_leads = unique_domains[unique_domains['type'] == 'Zero Cost'].shape[0]

# Calculate revenue by lead type
revenue_by_lead_type = processed_df.groupby('type')['revenue'].sum().reset_index()

# Calculate average revenue per lead type
avg_revenue_per_paid = revenue_by_lead_type[revenue_by_lead_type['type'] == 'Purchased']['revenue'].values[
                           0] / paid_leads if paid_leads > 0 else 0
avg_revenue_per_zero_cost = revenue_by_lead_type[revenue_by_lead_type['type'] == 'Zero Cost']['revenue'].values[
                                0] / zero_cost_leads if zero_cost_leads > 0 else 0

# Display KPI metrics in a row
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card blue-bg">
        <div class="metric-title">Total Revenue</div>
        <div class="metric-value">${total_revenue:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card green-bg">
        <div class="metric-title">Total Endpoints</div>
        <div class="metric-value">{int(total_endpoints):,}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card yellow-bg">
        <div class="metric-title">Lead Types</div>
        <div class="metric-value">{paid_leads} Paid Leads / {zero_cost_leads} Zero Cost Leads</div>
    </div>
    """, unsafe_allow_html=True)

col4, col5 = st.columns(2)

with col4:
    st.markdown(f"""
    <div class="metric-card purple-bg">
        <div class="metric-title">Avg. Revenue Per Paid Lead</div>
        <div class="metric-value">${avg_revenue_per_paid:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card blue-bg">
        <div class="metric-title">Avg. Revenue Per Zero Cost Lead</div>
        <div class="metric-value">${avg_revenue_per_zero_cost:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Monthly Revenue Chart
monthly_revenue = processed_df.groupby('month')['revenue'].sum().reset_index()

# Ensure months are in correct order
month_order = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
               'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}

monthly_revenue['month_num'] = monthly_revenue['month'].map(month_order)
monthly_revenue = monthly_revenue.sort_values('month_num')

col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Monthly Revenue")

    fig = px.bar(
        monthly_revenue,
        x='month',
        y='revenue',
        text_auto='.2s',
        color_discrete_sequence=['#4F46E5'],
        labels={'month': '', 'revenue': 'Revenue ($)'}
    )
    fig.update_layout(
        plot_bgcolor='white',
        hovermode='closest',
        margin=dict(t=10, l=10, r=10, b=10),
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Monthly Customer Acquisition
monthly_acquisition = processed_df.groupby(['month', 'type']).size().unstack(fill_value=0).reset_index()

if 'Purchased' in monthly_acquisition.columns and 'Zero Cost' in monthly_acquisition.columns:
    monthly_acquisition['month_num'] = monthly_acquisition['month'].map(month_order)
    monthly_acquisition = monthly_acquisition.sort_values('month_num')

    with col2:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("Monthly Customer Acquisition")

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=monthly_acquisition['month'],
            y=monthly_acquisition['Purchased'],
            name='Paid',
            marker_color='#4F46E5'
        ))
        fig.add_trace(go.Bar(
            x=monthly_acquisition['month'],
            y=monthly_acquisition['Zero Cost'],
            name='Zero-Cost',
            marker_color='#10B981'
        ))

        fig.update_layout(
            barmode='stack',
            plot_bgcolor='white',
            hovermode='closest',
            margin=dict(t=10, l=10, r=10, b=10),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# Revenue by Lead Type Pie Chart
revenue_by_lead_type['percentage'] = (revenue_by_lead_type['revenue'] / total_revenue * 100).round(1)

with col1:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Revenue by Lead Type")

    fig = px.pie(
        revenue_by_lead_type,
        values='revenue',
        names='type',
        hole=0.4,
        color_discrete_sequence=['#0088FE', '#00C49F'],
        labels={'type': 'Lead Type', 'revenue': 'Revenue ($)'}
    )

    fig.update_traces(
        textinfo='percent+label',
        textposition='outside'
    )

    fig.update_layout(
        annotations=[dict(text=f'${total_revenue:,.0f}', x=0.5, y=0.5, font_size=15, showarrow=False)],
        margin=dict(t=10, l=10, r=10, b=10),
        height=350
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Revenue by Country
revenue_by_country = processed_df.groupby('country')['revenue'].sum().reset_index()
revenue_by_country['percentage'] = (revenue_by_country['revenue'] / total_revenue * 100).round(1)
revenue_by_country = revenue_by_country.sort_values('revenue', ascending=False)

with col2:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Revenue by Country")

    fig = px.pie(
        revenue_by_country,
        values='revenue',
        names='country',
        hole=0.4,
        color_discrete_sequence=['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#A28BFC', '#FF6B6B'],
        labels={'country': 'Country', 'revenue': 'Revenue ($)'}
    )

    fig.update_traces(
        textinfo='percent+label',
        textposition='outside'
    )

    fig.update_layout(
        margin=dict(t=10, l=10, r=10, b=10),
        height=350
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# Revenue by Edition
if 'edition_simple' in processed_df.columns:
    revenue_by_edition = processed_df.groupby('edition_simple')['revenue'].sum().reset_index()
    revenue_by_edition['percentage'] = (revenue_by_edition['revenue'] / total_revenue * 100).round(1)

    with col1:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("Revenue by Edition")

        fig = px.pie(
            revenue_by_edition,
            values='revenue',
            names='edition_simple',
            hole=0.4,
            color_discrete_sequence=['#0088FE', '#00C49F', '#FFBB28', '#FF8042'],
            labels={'edition_simple': 'Edition', 'revenue': 'Revenue ($)'}
        )

        fig.update_traces(
            textinfo='percent+label',
            textposition='outside'
        )

        fig.update_layout(
            margin=dict(t=10, l=10, r=10, b=10),
            height=350
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Revenue by Deployment
if 'deployment' in processed_df.columns:
    revenue_by_deployment = processed_df.groupby('deployment')['revenue'].sum().reset_index()
    revenue_by_deployment['percentage'] = (revenue_by_deployment['revenue'] / total_revenue * 100).round(1)

    with col2:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("Revenue by Deployment")

        fig = px.pie(
            revenue_by_deployment,
            values='revenue',
            names='deployment',
            hole=0.4,
            color_discrete_sequence=['#0088FE', '#00C49F'],
            labels={'deployment': 'Deployment', 'revenue': 'Revenue ($)'}
        )

        fig.update_traces(
            textinfo='percent+label',
            textposition='outside'
        )

        fig.update_layout(
            margin=dict(t=10, l=10, r=10, b=10),
            height=350
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Revenue by Product Bar Chart
revenue_by_product = processed_df.groupby('product')['revenue'].sum().reset_index()
revenue_by_product = revenue_by_product.sort_values('revenue', ascending=False)

st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
st.subheader("Revenue by Product")

fig = px.bar(
    revenue_by_product,
    y='product',
    x='revenue',
    orientation='h',
    color_discrete_sequence=['#4F46E5'],
    labels={'product': '', 'revenue': 'Revenue ($)'}
)

fig.update_layout(
    plot_bgcolor='white',
    hovermode='closest',
    margin=dict(t=10, l=150, r=10, b=10),
    height=400,
    yaxis={'categoryorder': 'total ascending'}
)

st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# Revenue by Industry Pie Chart
revenue_by_industry = processed_df.groupby('industry')['revenue'].sum().reset_index()
revenue_by_industry['percentage'] = (revenue_by_industry['revenue'] / total_revenue * 100).round(1)
revenue_by_industry = revenue_by_industry.sort_values('revenue', ascending=False)

with col1:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Revenue by Industry")

    top_industries = revenue_by_industry.head(6)
    other_industries = revenue_by_industry.iloc[6:]

    if not other_industries.empty:
        other_revenue = other_industries['revenue'].sum()
        other_percentage = other_industries['percentage'].sum()
        other_row = pd.DataFrame({
            'industry': ['Other'],
            'revenue': [other_revenue],
            'percentage': [other_percentage]
        })
        top_industries = pd.concat([top_industries, other_row], ignore_index=True)

    fig = px.pie(
        top_industries,
        values='revenue',
        names='industry',
        hole=0.4,
        color_discrete_sequence=['#FF3EA5', '#FF5E5B', '#FFDB4C', '#00E396', '#0073FF', '#7C4DFF', '#775DD0'],
        labels={'industry': 'Industry', 'revenue': 'Revenue ($)'}
    )

    fig.update_traces(textinfo='percent+label', textposition='outside')
    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Endpoint Size Distribution
size_ranges = [
    (0, 100), (101, 200), (201, 300), (301, 400), (401, 500),
    (501, 600), (601, 700), (701, 800), (801, 900), 
    (901, 999), (1000, 1499), (1500, 1999), (2000, 2499), (2500, float('inf'))
]

range_labels = [
    '0-100', '101-200', '201-300', '301-400', '401-500',
    '501-600', '601-700', '701-800', '801-900',
    '901+', '1000+', '1500+', '2000+', '2500+'
]

endpoint_size_distribution = []
for i, (lower, upper) in enumerate(size_ranges):
    count = processed_df[(processed_df['endpoints'] >= lower) & (processed_df['endpoints'] <= upper)].shape[0]
    if count > 0:
        endpoint_size_distribution.append({'range': range_labels[i], 'count': count})

endpoint_size_df = pd.DataFrame(endpoint_size_distribution)

if not endpoint_size_df.empty:
    range_order = {label: i for i, label in enumerate(range_labels)}
    endpoint_size_df['range_order'] = endpoint_size_df['range'].map(range_order)
    endpoint_size_df = endpoint_size_df.sort_values('range_order')

    with col2:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("Endpoint Size Distribution")

        fig = px.bar(
            endpoint_size_df,
            x='range',
            y='count',
            color_discrete_sequence=['#FF8042'],
            labels={'range': 'Size Range', 'count': 'Count'}
        )
        fig.update_layout(plot_bgcolor='white', hovermode='closest', margin=dict(t=10, l=10, r=10, b=10), height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Domain Distribution Analysis
domain_count = processed_df['Domain'].value_counts().reset_index()
domain_count.columns = ['Domain', 'Count']
domain_count = domain_count[domain_count['Domain'] != ''].head(10)

if not domain_count.empty:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Top 10 Domains by Count")

    fig = px.bar(
        domain_count,
        y='Domain',
        x='Count',
        orientation='h',
        color_discrete_sequence=['#00C49F'],
        labels={'Domain': '', 'Count': 'Number of Entries'}
    )
    fig.update_layout(plot_bgcolor='white', hovermode='closest', margin=dict(t=10, l=250, r=10, b=10), height=400, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>© 2025 Revenue Analytics Dashboard</p>", unsafe_allow_html=True)
