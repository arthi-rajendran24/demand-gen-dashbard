import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

# --- DATA LOADING AND CLEANING ---

@st.cache_data(ttl=600) # Cache the data for 10 minutes
def load_and_clean_data(url):
    """Load data from a GitHub URL and rename columns."""
    try:
        # Load the raw data from the CSV
        df = pd.read_csv(url)

        # --- IMPORTANT: Column Renaming ---
        # This dictionary maps the names from your CSV file to the names the script expects.
        # Note the handling of spaces and special characters in 'Revenue (in USD )'.
        # Note that 'Region' from your file is being mapped to 'country' for the charts.
        rename_map = {
            'Update as of': 'update_as',
            'Domain': 'domain',
            'Endpoints': 'endpoints',
            'Revenue (in USD )': 'revenue',
            'Edition': 'edition',
            'License Date': 'license_date',
            'Product': 'product',
            'Region': 'country',  # Mapping 'Region' to 'country'
            'Industry': 'industry',
            'Type': 'type',
            'CPL': 'cpl'
        }
        df = df.rename(columns=rename_map)

        # Ensure all required columns exist after renaming
        required_cols = list(rename_map.values())
        if not all(col in df.columns for col in required_cols):
            st.error(f"One or more required columns are missing after renaming. Expected: {required_cols}")
            return pd.DataFrame()

        return df

    except Exception as e:
        st.error(f"Error loading or cleaning data from GitHub: {e}")
        return pd.DataFrame()

# The RAW URL for your GitHub file
GITHUB_URL = "https://raw.githubusercontent.com/arthi-rajendran24/demand-gen-dashbard/refs/heads/main/data_Conversions.csv"

# Load and clean the data
df_raw = load_and_clean_data(GITHUB_URL)

# Stop the app if data loading fails
if df_raw.empty:
    st.warning("Could not load or process data. Please check the GitHub URL and column names in the CSV.")
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

# Using 'domain' (lowercase) as defined in our rename map
unique_domains = processed_df[['domain', 'type']].drop_duplicates()
paid_leads = unique_domains[unique_domains['type'] == 'Purchased'].shape[0]
zero_cost_leads = unique_domains[unique_domains['type'] == 'Zero Cost'].shape[0]

# Calculate revenue by lead type
revenue_by_lead_type = processed_df.groupby('type')['revenue'].sum().reset_index()

# Calculate average revenue per lead type
avg_revenue_per_paid = (revenue_by_lead_type.loc[revenue_by_lead_type['type'] == 'Purchased', 'revenue'].iloc[0] / paid_leads) if paid_leads > 0 and not revenue_by_lead_type[revenue_by_lead_type['type'] == 'Purchased'].empty else 0
avg_revenue_per_zero_cost = (revenue_by_lead_type.loc[revenue_by_lead_type['type'] == 'Zero Cost', 'revenue'].iloc[0] / zero_cost_leads) if zero_cost_leads > 0 and not revenue_by_lead_type[revenue_by_lead_type['type'] == 'Zero Cost'].empty else 0


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
        <div class="metric-value">{paid_leads} Paid / {zero_cost_leads} Zero Cost</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

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
monthly_acquisition['month_num'] = monthly_acquisition['month'].map(month_order)
monthly_acquisition = monthly_acquisition.sort_values('month_num')

with col2:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Monthly Customer Acquisition")

    fig = go.Figure()
    if 'Purchased' in monthly_acquisition.columns:
        fig.add_trace(go.Bar(
            x=monthly_acquisition['month'],
            y=monthly_acquisition['Purchased'],
            name='Paid',
            marker_color='#4F46E5'
        ))
    if 'Zero Cost' in monthly_acquisition.columns:
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
    fig.update_traces(textinfo='percent+label', textposition='outside')
    fig.update_layout(
        annotations=[dict(text=f'${total_revenue:,.0f}', x=0.5, y=0.5, font_size=15, showarrow=False)],
        margin=dict(t=10, l=10, r=10, b=10),
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Revenue by Country (using the 'Region' column from your sheet)
revenue_by_country = processed_df.groupby('country')['revenue'].sum().reset_index()
revenue_by_country = revenue_by_country.sort_values('revenue', ascending=False)

with col2:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Revenue by Region") # Changed title to reflect source data
    fig = px.pie(
        revenue_by_country,
        values='revenue',
        names='country',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Plotly,
        labels={'country': 'Region', 'revenue': 'Revenue ($)'}
    )
    fig.update_traces(textinfo='percent+label', textposition='outside')
    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=350)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ... (The rest of the charts will work correctly with the renamed columns) ...

col1, col2 = st.columns(2)

# Revenue by Edition
if 'edition_simple' in processed_df.columns:
    revenue_by_edition = processed_df.groupby('edition_simple')['revenue'].sum().reset_index()

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
        fig.update_traces(textinfo='percent+label',textposition='outside')
        fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=350)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Revenue by Deployment
if 'deployment' in processed_df.columns:
    revenue_by_deployment = processed_df.groupby('deployment')['revenue'].sum().reset_index()

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
        fig.update_traces(textinfo='percent+label', textposition='outside')
        fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=350)
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
    margin=dict(t=10, l=200, r=10, b=10),
    height=400,
    yaxis={'categoryorder': 'total ascending'}
)
st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# Using 'domain' (lowercase) for the final chart
domain_count = processed_df['domain'].value_counts().reset_index()
domain_count.columns = ['domain', 'Count']
domain_count = domain_count[domain_count['domain'].notna() & (domain_count['domain'] != '')].head(10)

if not domain_count.empty:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Top 10 Domains by Entry Count")

    fig = px.bar(
        domain_count,
        y='domain',
        x='Count',
        orientation='h',
        color_discrete_sequence=['#00C49F'],
        labels={'domain': 'Domain', 'Count': 'Number of Entries'}
    )
    fig.update_layout(
        plot_bgcolor='white',
        hovermode='closest',
        margin=dict(t=10, l=250, r=10, b=10),
        height=400,
        yaxis={'categoryorder': 'total ascending'}
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>© 2025 Revenue Analytics Dashboard</p>", unsafe_allow_html=True)
