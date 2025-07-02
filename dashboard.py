import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

# --- Page Configuration ---
st.set_page_config(
    page_title="Demand Generation Performance Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Caching Data Loading ---
@st.cache_data
def load_data(url):
    """
    Loads data from the given URL, performs preprocessing, and returns a DataFrame.
    The @st.cache_data decorator ensures this function only runs once, caching the result.
    """
    try:
        df = pd.read_csv(url)
        
        # --- Data Preprocessing ---
        # Convert 'Date' to datetime objects
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Anonymize domain names as requested
        # Create a mapping from original domain to an anonymized name
        unique_domains = df['Domain'].unique()
        domain_mapping = {domain: f"Source {i+1}" for i, domain in enumerate(unique_domains)}
        df['Anonymized Source'] = df['Domain'].map(domain_mapping)
        
        # Create new time-based features for filtering and aggregation
        df['Month'] = df['Date'].dt.to_period('M').astype(str)
        df['Week'] = df['Date'].dt.to_period('W').astype(str)
        
        # Ensure numeric columns are of the correct type, handling potential errors
        numeric_cols = ['Conversions', 'Revenue', 'Cost', 'ROI', 'Impressions', 'Clicks', 'CTR', 'CPC', 'CPA']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Drop rows with missing critical values (like revenue or cost)
        df.dropna(subset=['Revenue', 'Cost', 'Conversions'], inplace=True)
        
        return df, domain_mapping

    except Exception as e:
        st.error(f"Error loading or processing data: {e}")
        return pd.DataFrame(), {}

# --- Load Data ---
DATA_URL = "https://raw.githubusercontent.com/arthi-rajendran24/demand-gen-dashbard/refs/heads/main/data_Conversions.csv"
df, domain_mapping = load_data(DATA_URL)

# Check if data loading was successful
if df.empty:
    st.warning("Could not load data. Please check the URL or your connection.")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("Dashboard Filters")

# Date Range Filter
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Handle case where user selects a single day
start_date, end_date = date_range
if len(date_range) == 1:
    start_date = date_range[0]
    end_date = date_range[0]

# Source Filter (using anonymized names)
all_sources = sorted(df['Anonymized Source'].unique())
selected_sources = st.sidebar.multiselect(
    "Select Source(s)",
    options=all_sources,
    default=all_sources
)

# --- Filter DataFrame based on selection ---
filtered_df = df[
    (df['Date'].dt.date >= start_date) &
    (df['Date'].dt.date <= end_date) &
    (df['Anonymized Source'].isin(selected_sources))
]

# Check if filtered data is empty
if filtered_df.empty:
    st.warning("No data available for the selected filters. Please adjust your selection.")
    st.stop()

# --- Main Dashboard ---
st.title("🚀 Demand Generation Performance Dashboard")
st.markdown("An interactive visualization of key marketing and conversion metrics.")

# --- Key Performance Indicators (KPIs) ---
st.subheader("Overall Performance Snapshot")

# Calculate KPIs
total_revenue = filtered_df['Revenue'].sum()
total_cost = filtered_df['Cost'].sum()
total_conversions = filtered_df['Conversions'].sum()
total_clicks = filtered_df['Clicks'].sum()

# Handle division by zero for metrics
if total_cost > 0:
    overall_roi = (total_revenue - total_cost) / total_cost
    overall_cpa = total_cost / total_conversions if total_conversions > 0 else 0
else:
    overall_roi = float('inf') if total_revenue > 0 else 0
    overall_cpa = 0

# Display KPIs in columns
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Total Cost", f"${total_cost:,.2f}")
col3.metric("Overall ROI", f"{overall_roi:.2%}")
col4.metric("Total Conversions", f"{total_conversions:,.0f}")

st.markdown("---")

# --- Time Series Analysis ---
st.subheader("Performance Trends Over Time")

# Aggregate data by day for time series plotting
time_series_df = filtered_df.groupby('Date').agg({
    'Revenue': 'sum',
    'Cost': 'sum',
    'Conversions': 'sum'
}).reset_index()

fig_time_series = go.Figure()
fig_time_series.add_trace(go.Scatter(x=time_series_df['Date'], y=time_series_df['Revenue'], mode='lines', name='Revenue', yaxis='y1'))
fig_time_series.add_trace(go.Scatter(x=time_series_df['Date'], y=time_series_df['Conversions'], mode='lines', name='Conversions', yaxis='y2'))

fig_time_series.update_layout(
    title='Daily Revenue and Conversions',
    xaxis_title='Date',
    yaxis=dict(
        title='Revenue ($)',
        titlefont=dict(color='#1f77b4'),
        tickfont=dict(color='#1f77b4')
    ),
    yaxis2=dict(
        title='Conversions',
        titlefont=dict(color='#ff7f0e'),
        tickfont=dict(color='#ff7f0e'),
        overlaying='y',
        side='right'
    ),
    legend=dict(x=0, y=1.1, orientation='h'),
    hovermode='x unified'
)
st.plotly_chart(fig_time_series, use_container_width=True)

st.markdown("---")

# --- Source-Level Analysis ---
st.subheader("In-Depth Source Analysis")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Performance by Source")
    
    # Aggregate data by source
    source_performance = filtered_df.groupby('Anonymized Source').agg({
        'Revenue': 'sum',
        'Cost': 'sum',
        'Conversions': 'sum',
        'Clicks': 'sum',
        'Impressions': 'sum'
    }).reset_index()
    
    # Calculate source-level metrics
    source_performance['ROI'] = (source_performance['Revenue'] - source_performance['Cost']) / source_performance['Cost']
    source_performance['CPA'] = source_performance['Cost'] / source_performance['Conversions']
    source_performance.replace([float('inf'), -float('inf')], None, inplace=True) # Handle infinite ROI/CPA

    # User selection for bar chart metric
    metric_to_plot = st.selectbox(
        "Select metric to compare sources:",
        options=['Revenue', 'Conversions', 'ROI', 'CPA'],
        index=0
    )

    is_ascending = True if metric_to_plot == 'CPA' else False
    
    fig_source_bar = px.bar(
        source_performance.sort_values(by=metric_to_plot, ascending=is_ascending).head(15),
        x=metric_to_plot,
        y='Anonymized Source',
        orientation='h',
        title=f'Top Sources by {metric_to_plot}',
        labels={'Anonymized Source': 'Source'},
        text_auto=True
    )
    fig_source_bar.update_traces(texttemplate='%{x:,.2f}' if metric_to_plot in ['ROI', 'CPA'] else '%{x:,.0f}', textposition='outside')
    st.plotly_chart(fig_source_bar, use_container_width=True)


with col2:
    st.markdown("#### Contribution by Source")
    
    # User selection for pie chart metric
    pie_metric = st.selectbox(
        "Select metric for contribution pie chart:",
        options=['Revenue', 'Conversions', 'Cost'],
        index=0
    )
    
    fig_pie = px.pie(
        source_performance,
        values=pie_metric,
        names='Anonymized Source',
        title=f'Contribution of each Source to Total {pie_metric}',
        hole=0.4 # for a donut chart effect
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# --- Efficiency and Correlation Analysis ---
st.subheader("Efficiency & Correlation Insights")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Cost vs. Revenue by Source")
    fig_scatter = px.scatter(
        filtered_df,
        x='Cost',
        y='Revenue',
        color='Anonymized Source',
        size='Conversions',
        hover_data=['Date'],
        title='Cost vs. Revenue (Bubble size represents Conversions)',
        size_max=60,
        log_x=True, # Use log scale for better visualization if values are spread out
        log_y=True
    )
    fig_scatter.update_layout(xaxis_title="Cost (Log Scale)", yaxis_title="Revenue (Log Scale)")
    st.plotly_chart(fig_scatter, use_container_width=True)
    
with col2:
    st.markdown("#### Key Efficiency Metrics Over Time")
    efficiency_df = filtered_df.groupby('Date').agg({
        'CTR': 'mean',
        'CPC': 'mean',
        'CPA': 'mean'
    }).reset_index()
    
    efficiency_metric = st.selectbox(
        "Select an efficiency metric to view over time:",
        options=['CTR', 'CPC', 'CPA'],
        index=2 # Default to CPA
    )
    
    fig_efficiency = px.line(
        efficiency_df,
        x='Date',
        y=efficiency_metric,
        title=f'Daily Average {efficiency_metric} Trend',
        markers=True
    )
    fig_efficiency.update_traces(line=dict(color='#d62728')) # Use a distinct color
    st.plotly_chart(fig_efficiency, use_container_width=True)
    
st.markdown("---")

# --- Detailed Data View ---
st.subheader("Detailed Data Explorer")
st.markdown("Use the filters in the sidebar to drill down into the data.")

# Show a subset of columns for clarity
display_cols = [
    'Date', 'Anonymized Source', 'Conversions', 'Revenue', 'Cost', 
    'ROI', 'CPA', 'Clicks', 'CTR', 'CPC'
]
st.dataframe(
    filtered_df[display_cols].sort_values(by='Date', ascending=False).reset_index(drop=True),
    use_container_width=True,
    hide_index=True
)

st.sidebar.markdown("---")
st.sidebar.info(
    "This dashboard is created to visualize demand generation data. "
    "All source domains have been anonymized for privacy."
)
