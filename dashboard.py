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
    .blue-bg {
        background-color: #e6f3ff;
    }
    .green-bg {
        background-color: #e6fff0;
    }
    .yellow-bg {
        background-color: #fffde6;
    }
    .purple-bg {
        background-color: #f2e6ff;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("Revenue Analytics Dashboard")

# Create tabs
tab1, tab2 = st.tabs(["Dashboard", "Data Entry"])

# Sample data structure for a new entry
empty_row = {
    "update_as": "",
    "endpoints": 0,
    "revenue": 0.0,
    "edition": "",
    "license_date": datetime.now().strftime("%d/%m/%Y"),
    "product": "",
    "country": "",
    "industry": "",
    "type": "",
    "cpl": 0.0
}

# Default sample data
default_data = [
    {"update_as": "Jan 2025", "endpoints": 250, "revenue": 7018.92, "edition": "UEM", "license_date": "30/01/2025",
     "product": "Endpoint Central", "country": "Netherlands", "industry": "Industrial goods and machinery",
     "type": "Zero Cost", "cpl": 0.00},
    {"update_as": "Jan 2025", "endpoints": 200, "revenue": 2442.30, "edition": "Enterprise",
     "license_date": "30/01/2025", "product": "PMP Cloud", "country": "United Arab Emirates", "industry": "IT",
     "type": "Zero Cost", "cpl": 0.00},
    {"update_as": "Jan 2025", "endpoints": 580, "revenue": 2982.00, "edition": "Enterprise",
     "license_date": "15/02/2025", "product": "Patch Manager Plus", "country": "US", "industry": "Federal",
     "type": "Purchased", "cpl": 0.40},
    {"update_as": "Feb 2025", "endpoints": 500, "revenue": 31488.00, "edition": "UEM", "license_date": "8/2/2025",
     "product": "Endpoint Central", "country": "US", "industry": "Banking", "type": "Purchased", "cpl": 0.40},
    {"update_as": "Feb 2025", "endpoints": 256, "revenue": 10007.97, "edition": "Security", "license_date": "27/2/2025",
     "product": "Endpoint Central Cloud", "country": "Australia", "industry": "Mining industry", "type": "Zero Cost",
     "cpl": 0.40},
    {"update_as": "Mar 2025", "endpoints": 525, "revenue": 3055.50, "edition": "Enterprise",
     "license_date": "28/3/2025", "product": "Patch Manager Plus Cloud", "country": "Saudi Arabia",
     "industry": "Diagnostic imaging services", "type": "Zero Cost", "cpl": 0.00}
]

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = default_data


# Function to process data
def process_data(df):
    # Basic data cleaning
    if 'revenue' in df.columns:
        df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')

    if 'endpoints' in df.columns:
        df['endpoints'] = pd.to_numeric(df['endpoints'], errors='coerce')

    if 'license_date' in df.columns:
        # Keep license_date as string for now, convert when needed
        pass

    # Extract month from update_as field
    if 'update_as' in df.columns:
        df['month'] = df['update_as'].str.split(' ').str[0]
    else:
        # If update_as not available, use license_date
        try:
            df['month'] = pd.to_datetime(df['license_date'], format='%d/%m/%Y', errors='coerce').dt.strftime('%b')
        except:
            df['month'] = "Unknown"

    # Calculate deployment type based on product name
    if 'product' in df.columns:
        df['deployment'] = df['product'].str.lower().apply(lambda x: 'Cloud' if 'cloud' in str(x) else 'On-Premises')

    # Clean edition
    if 'edition' in df.columns:
        df['edition_simple'] = df['edition'].str.split(' ').str[0]

    return df


# Data Entry Tab
with tab2:
    st.header("Data Entry")

    # Button to add a new row
    if st.button("Add New Entry"):
        st.session_state.data.append(empty_row.copy())

    # Display editable dataframe
    edited_df = st.data_editor(
        pd.DataFrame(st.session_state.data),
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "update_as": st.column_config.TextColumn("Update As", help="Format: Mon YYYY (e.g., Jan 2025)"),
            "endpoints": st.column_config.NumberColumn("Endpoints", help="Number of endpoints"),
            "revenue": st.column_config.NumberColumn("Revenue", help="Revenue in USD", format="$%.2f"),
            "edition": st.column_config.SelectboxColumn(
                "Edition",
                help="Product edition",
                options=["UEM", "Enterprise", "Security", "Professional"]
            ),
            "license_date": st.column_config.TextColumn("License Date", help="Date in format DD/MM/YYYY"),
            "product": st.column_config.TextColumn("Product", help="Product name"),
            "country": st.column_config.TextColumn("Country", help="Country name"),
            "industry": st.column_config.TextColumn("Industry", help="Industry type"),
            "type": st.column_config.SelectboxColumn(
                "Type",
                help="Lead type",
                options=["Purchased", "Zero Cost"]
            ),
            "cpl": st.column_config.NumberColumn("CPL", help="Cost per lead", format="$%.2f")
        },
        hide_index=True
    )

    # Update the session state data
    if edited_df is not None:
        st.session_state.data = edited_df.to_dict('records')

    # Option to download data as CSV
    csv = edited_df.to_csv(index=False)
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name="sales_data.csv",
        mime="text/csv"
    )

    # Option to reset to default data
    if st.button("Reset to Default Data"):
        st.session_state.data = default_data.copy()
        st.rerun()

# Dashboard Tab
with tab1:
    # Convert data to DataFrame and process
    df = pd.DataFrame(st.session_state.data)
    processed_df = process_data(df)

    # Calculate summary statistics
    total_revenue = processed_df['revenue'].sum()
    total_endpoints = processed_df['endpoints'].sum()

    # Count lead types
    paid_leads = processed_df[processed_df['type'] == 'Purchased'].shape[0]
    zero_cost_leads = processed_df[processed_df['type'] == 'Zero Cost'].shape[0]

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

            # Use pd.concat instead of append (which is deprecated)
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

        fig.update_traces(
            textinfo='percent+label',
            textposition='outside'
        )

        fig.update_layout(
            margin=dict(t=10, l=10, r=10, b=10),
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Endpoint Size Distribution
    size_ranges = [(0, 100), (101, 200), (201, 300), (301, 400), (401, 500),
                   (501, 600), (601, 700), (701, 800), (801, 900), (901, float('inf'))]

    range_labels = ['0-100', '101-200', '201-300', '301-400', '401-500',
                    '501-600', '601-700', '701-800', '801-900', '901+']

    endpoint_size_distribution = []
    for i, (lower, upper) in enumerate(size_ranges):
        count = processed_df[(processed_df['endpoints'] >= lower) & (processed_df['endpoints'] <= upper)].shape[0]
        if count > 0:
            endpoint_size_distribution.append({
                'range': range_labels[i],
                'count': count
            })

    endpoint_size_df = pd.DataFrame(endpoint_size_distribution)

    if not endpoint_size_df.empty:
        # Map the range to an order for proper sorting
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

            fig.update_layout(
                plot_bgcolor='white',
                hovermode='closest',
                margin=dict(t=10, l=10, r=10, b=10),
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>© 2025 Revenue Analytics Dashboard</p>",
            unsafe_allow_html=True)
