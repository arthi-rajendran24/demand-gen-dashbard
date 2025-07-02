import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. Data Loading and Cleaning (from GitHub) ---

def load_and_clean_data(url):
    """Loads data from the specified URL and performs thorough cleaning."""
    print(f"Fetching data from {url}...")
    try:
        # Pandas can read directly from a URL
        df = pd.read_csv(url)
    except Exception as e:
        print(f"Error fetching or reading data from URL: {e}")
        return None

    # Drop the 'Total' row and any fully empty rows
    if 'Total' in df['Month'].values:
        df = df[df['Month'] != 'Total'].reset_index(drop=True)
    df.dropna(how='all', inplace=True)

    # --- Clean and standardize columns ---

    # Clean 'Revenue' column (remove $, commas)
    df['Revenue'] = df['Revenue'].astype(str).str.replace(r'[$,]', '', regex=True).astype(float)

    # Clean and convert 'Endpoints'
    df['Endpoints'] = pd.to_numeric(df['Endpoints'], errors='coerce').fillna(0).astype(int)

    # Convert 'License Date' to datetime, handling potential mixed formats
    df['License Date'] = pd.to_datetime(df['License Date'], errors='coerce', dayfirst=False)
    # For dates like 31/10/2024, a second pass with dayfirst=True can fix errors
    df['License Date'].fillna(pd.to_datetime(df['License Date'], errors='coerce', dayfirst=True), inplace=True)
    df['MonthYear'] = df['License Date'].dt.to_period('M').astype(str)

    # Standardize 'Type' column (handles 'Zero Cost', 'Zero-cost', 'Purchased', 'Purhased')
    df['Type'] = df['Type'].str.strip().str.replace('-', ' ').str.title()
    type_map = {'Purhased': 'Purchased', 'Zero Cost': 'Zero Cost'}
    df['Type'] = df['Type'].map(type_map).fillna(df['Type']) # Keep original if not in map
    df['Type'] = df['Type'].fillna('Other')

    # Standardize 'Edition' column
    df['Edition'] = df['Edition'].str.replace(r' \(.*\)', '', regex=True).str.strip()

    # Standardize 'Product' column (handle abbreviations and casing)
    product_map = {
        'EC': 'Endpoint Central', 'EC Cloud': 'Endpoint Central Cloud',
        'EC MSP Cloud': 'Endpoint Central MSP Cloud',
        'Endpoint central cloud': 'Endpoint Central Cloud',
        'PCP': 'Patch Manager Plus', 'PMP': 'Patch Manager Plus',
        'PMP Cloud': 'Patch Manager Plus Cloud',
        'VMP': 'Vulnerability Manager Plus',
        'MDM': 'Mobile Device Manager Plus',
        'MDMOnDemand': 'Mobile Device Manager Plus Cloud',
        'Patch manager Plus': 'Patch Manager Plus',
    }
    df['Product'] = df['Product'].str.strip().replace(product_map)

    # Handle multiple products in one cell by splitting and exploding
    df['Product'] = df['Product'].str.split(', ')
    df = df.explode('Product')
    df['Product'] = df['Product'].str.strip()

    # Clean 'Industry' column (remove newlines)
    df['Industry'] = df['Industry'].str.replace('\n', ' ', regex=False).str.strip()

    # Correct region names
    df['Region'] = df['Region'].replace({'South Arica': 'South Africa'})

    print("Data cleaning complete.")
    return df.sort_values('License Date').reset_index(drop=True)

# URL of the raw CSV file on GitHub
github_url = 'https://raw.githubusercontent.com/arthi-rajendran24/demand-gen-dashbard/refs/heads/main/data_Conversions.csv'

# Load and clean the data
df_clean = load_and_clean_data(github_url)

if df_clean is not None and not df_clean.empty:
    # --- 2. Data Analysis & Aggregation ---
    print("Analyzing data...")

    # KPIs
    total_revenue = df_clean['Revenue'].sum()
    total_endpoints = df_clean['Endpoints'].sum()
    num_deals = len(df_clean['Domain'].unique()) # Use unique domains for a more accurate deal count
    avg_revenue_per_deal = total_revenue / num_deals

    # Grouped data for charts
    monthly_revenue = df_clean.groupby('MonthYear')['Revenue'].sum().reset_index()
    monthly_deals = df_clean.groupby('MonthYear')['Domain'].nunique().rename('Deal Count').reset_index()
    revenue_by_region = df_clean.groupby('Region')['Revenue'].sum().sort_values(ascending=False).reset_index()
    revenue_by_product = df_clean.groupby('Product')['Revenue'].sum().sort_values(ascending=False).reset_index()
    revenue_by_industry = df_clean.groupby('Industry')['Revenue'].sum().sort_values(ascending=False).head(15).reset_index() # Top 15
    revenue_by_type = df_clean.groupby('Type')['Revenue'].sum().reset_index()
    deals_by_type = df_clean.groupby('Type')['Domain'].nunique().rename('Deal Count').reset_index()


    # --- 3. Visualization with Plotly ---
    print("Creating visualizations...")
    template = "plotly_white"

    # Chart 1: Monthly Revenue and Deal Count
    fig_monthly = make_subplots(specs=[[{"secondary_y": True}]])
    fig_monthly.add_trace(
        go.Bar(x=monthly_revenue['MonthYear'], y=monthly_revenue['Revenue'], name='Monthly Revenue', marker_color='cornflowerblue'),
        secondary_y=False,
    )
    fig_monthly.add_trace(
        go.Scatter(x=monthly_deals['MonthYear'], y=monthly_deals['Deal Count'], name='Deal Count', mode='lines+markers', line=dict(color='darkorange')),
        secondary_y=True,
    )
    fig_monthly.update_layout(title_text='<b>Monthly Revenue and Deal Count</b>', template=template)
    fig_monthly.update_yaxes(title_text="Total Revenue ($)", secondary_y=False)
    fig_monthly.update_yaxes(title_text="Number of Deals", secondary_y=True)

    # Chart 2 & 3: Conversion Type Analysis (Revenue and Count)
    fig_type = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
    fig_type.add_trace(go.Pie(labels=revenue_by_type['Type'], values=revenue_by_type['Revenue'], name="Revenue"), 1, 1)
    fig_type.add_trace(go.Pie(labels=deals_by_type['Type'], values=deals_by_type['Deal Count'], name="Deals"), 1, 2)
    fig_type.update_traces(hole=.4, hoverinfo="label+percent+value")
    fig_type.update_layout(
        title_text='<b>Conversion Type Analysis: Purchased vs. Zero Cost</b>',
        annotations=[dict(text='By Revenue', x=0.16, y=0.5, font_size=16, showarrow=False),
                    dict(text='By Deal Count', x=0.84, y=0.5, font_size=16, showarrow=False)],
        template=template
    )

    # Chart 4: Top 10 Revenue by Region
    fig_region = px.bar(
        revenue_by_region.head(10), x='Region', y='Revenue',
        title='<b>Top 10 Regions by Revenue</b>', text_auto='.2s',
        color='Revenue', color_continuous_scale='Blues'
    )
    fig_region.update_traces(textposition='outside')
    fig_region.update_layout(template=template)

    # Chart 5: Revenue by Product
    fig_product = px.bar(
        revenue_by_product, y='Product', x='Revenue', orientation='h',
        title='<b>Revenue by Product</b>', text_auto='.2s',
        color='Revenue', color_continuous_scale='Greens'
    )
    fig_product.update_layout(yaxis={'categoryorder':'total ascending'}, template=template)

    # Chart 6: Revenue by Industry (Top 15)
    fig_industry = px.bar(
        revenue_by_industry, y='Industry', x='Revenue', orientation='h',
        title='<b>Top 15 Industries by Revenue</b>', text_auto='.2s',
        color='Revenue', color_continuous_scale='Purples'
    )
    fig_industry.update_layout(yaxis={'categoryorder':'total ascending'}, template=template)

    # Chart 7: Revenue Distribution (Deal Size)
    fig_dist_rev = px.histogram(
        df_clean, x="Revenue", nbins=30,
        title='<b>Distribution of Deal Size (by Revenue)</b>'
    )
    fig_dist_rev.update_layout(bargap=0.1, template=template)

    # Chart 8: Revenue by Region and Product
    fig_treemap = px.treemap(
        df_clean, path=[px.Constant("All Regions"), 'Region', 'Product'], values='Revenue',
        color='Revenue', hover_data=['Endpoints'],
        color_continuous_scale='RdBu',
        title='<b>Revenue Treemap: Region > Product</b>'
    )
    fig_treemap.update_layout(margin = dict(t=50, l=25, r=25, b=25), template=template)


    # --- 4. Assemble Dashboard HTML ---
    print("Generating HTML dashboard...")

    with open('Conversions_Dashboard.html', 'w') as f:
        f.write('<html><head>')
        f.write('<style>body{font-family: Arial, sans-serif; background-color: #f4f4f4;} h1, h2 {color: #333;} .grid-container {display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; padding: 20px;} .kpi {background-color: #fff; padding: 20px; text-align: center; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);} .kpi h2 {margin: 0; color: #555; font-size: 18px;} .kpi .value {font-size: 36px; font-weight: bold; color: #0056b3; margin-top: 5px;} .chart {grid-column: span 3; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);} .chart-half {grid-column: span 1; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);} @media (max-width: 900px) { .grid-container {grid-template-columns: 1fr;} .chart, .chart-half {grid-column: span 1;} }</style>')
        f.write('<title>Conversions Dashboard</title>')
        f.write('</head><body>')
        f.write('<h1 style="text-align:center;">Business Conversions Analysis Dashboard</h1>')

        # KPI Section
        f.write('<div class="grid-container">')
        f.write(f'<div class="kpi"><h2>Total Revenue</h2><div class="value">${total_revenue:,.2f}</div></div>')
        f.write(f'<div class="kpi"><h2>Total Endpoints Sold</h2><div class="value">{total_endpoints:,}</div></div>')
        f.write(f'<div class="kpi"><h2>Average Revenue per Deal</h2><div class="value">${avg_revenue_per_deal:,.2f}</div></div>')
        
        # Charts
        f.write(f'<div class="chart">{fig_monthly.to_html(full_html=False, include_plotlyjs="cdn")}</div>')
        f.write(f'<div class="chart">{fig_type.to_html(full_html=False, include_plotlyjs=False)}</div>')
        f.write(f'<div class="chart-half">{fig_region.to_html(full_html=False, include_plotlyjs=False)}</div>')
        f.write(f'<div class="chart-half">{fig_dist_rev.to_html(full_html=False, include_plotlyjs=False)}</div>')
        f.write(f'<div class="chart-half">{fig_product.to_html(full_html=False, include_plotlyjs=False)}</div>')
        f.write(f'<div class="chart">{fig_industry.to_html(full_html=False, include_plotlyjs=False)}</div>')
        f.write(f'<div class="chart">{fig_treemap.to_html(full_html=False, include_plotlyjs=False)}</div>')

        f.write('</div>') # Close grid-container
        f.write('</body></html>')

    print("Dashboard 'Conversions_Dashboard.html' created successfully.")
else:
    print("Could not generate dashboard because data loading or cleaning failed.")
