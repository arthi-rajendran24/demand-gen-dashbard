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

# Directly load the data from the table
data = [
    {
        "update_as": "Jan 2025",
        "Domain": "idexcorp.com",
        "endpoints": 250,
        "revenue": 7018.92,
        "edition": "UEM",
        "license_date": "30/01/2025",
        "product": "Endpoint Central",
        "country": "Netherlands",
        "industry": "Industrial goods and machinery",
        "type": "Zero Cost",
        "cpl": 0.00
    },
    {
        "update_as": "Jan 2025",
        "Domain": "redingtongroup.com",
        "endpoints": 200,
        "revenue": 2442.30,
        "edition": "Enterprise",
        "license_date": "30/01/2025",
        "product": "PMP Cloud",
        "country": "United Arab Emirates",
        "industry": "IT",
        "type": "Zero Cost",
        "cpl": 0.00
    },
    {
        "update_as": "Feb 2025",
        "Domain": "co.ellis.tx.us",
        "endpoints": 580,
        "revenue": 2982.00,
        "edition": "Enterprise",
        "license_date": "15/02/2025",
        "product": "Patch Manager Plus",
        "country": "US",
        "industry": "Federal",
        "type": "Purchased",
        "cpl": 0.40
    },
    {
        "update_as": "Feb 2025",
        "Domain": "aventiv.com",
        "endpoints": 950,
        "revenue": 8698.00,
        "edition": "Enterprise",
        "license_date": "14/02/2025",
        "product": "Patch Manager Plus",
        "country": "US",
        "industry": "Federal",
        "type": "Purchased",
        "cpl": 0.40
    },
    {
        "update_as": "Feb 2025",
        "Domain": "baystateinterpreters.com",
        "endpoints": 110,
        "revenue": 840.00,
        "edition": "Enterprise",
        "license_date": "2/4/2025",
        "product": "Patch Manager Plus",
        "country": "US",
        "industry": "Translation services",
        "type": "Purchased",
        "cpl": 0.40
    },
    {
        "update_as": "Feb 2025",
        "Domain": "thecityofriles.com",
        "endpoints": 50,
        "revenue": 1463.00,
        "edition": "Professional",
        "license_date": "13/02/2025",
        "product": "Mobile Device Manager",
        "country": "US",
        "industry": "Federal",
        "type": "Purchased",
        "cpl": 0.40
    },
    {
        "update_as": "Feb 2025",
        "Domain": "blackedge.com",
        "endpoints": 200,
        "revenue": 8075.00,
        "edition": "Enterprise",
        "license_date": "14/02/2025",
        "product": "OS Deployer",
        "country": "US",
        "industry": "Finance",
        "type": "Purchased",
        "cpl": 0.40
    },
    {
        "update_as": "Feb 2025",
        "Domain": "bobbrowauto.com",
        "endpoints": 250,
        "revenue": 1495.00,
        "edition": "Enterprise",
        "license_date": "2/11/2025",
        "product": "OS Deployer",
        "country": "US",
        "industry": "Automotive",
        "type": "Purchased",
        "cpl": 0.40
    },
    {
        "update_as": "Feb 2025",
        "Domain": "skylinenationalbank.com",
        "endpoints": 500,
        "revenue": 31488.00,
        "edition": "UEM",
        "license_date": "2/8/2025",
        "product": "Endpoint Central",
        "country": "US",
        "industry": "Banking",
        "type": "Purchased",
        "cpl": 0.40
    },
    {
        "update_as": "Feb 2025",
        "Domain": "orabandamining.com.au",
        "endpoints": 256,
        "revenue": 10007.97,
        "edition": "Security",
        "license_date": "27/2/2025",
        "product": "Endpoint Central Cloud",
        "country": "Australia",
        "industry": "Mining industry",
        "type": "Zero Cost",
        "cpl": 0.40
    },
    {
        "update_as": "Feb 2025",
        "Domain": "imagenetconsulting.com",
        "endpoints": 575,
        "revenue": 5941.00,
        "edition": "Enterprise",
        "license_date": "21/2/2025",
        "product": "VMP",
        "country": "US",
        "industry": "IT",
        "type": "Purchased",
        "cpl": 0.40
    },
    {
        "update_as": "Feb 2025",
        "Domain": "indysoft.com",
        "endpoints": 70,
        "revenue": 3173.00,
        "edition": "Security",
        "license_date": "26/2/2025",
        "product": "Endpoint Central Cloud",
        "country": "US",
        "industry": "Software solutions",
        "type": "Purchased",
        "cpl": 0.40
    },
    {
        "update_as": "Feb 2025",
        "Domain": "dessercom.org",
        "endpoints": 250,
        "revenue": 2016.00,
        "edition": "Enterprise",
        "license_date": "13/02/2025",
        "product": "PMP Cloud",
        "country": "Canada",
        "industry": "Emergency medical services",
        "type": "Zero Cost",
        "cpl": 0.00
    },
    {
        "update_as": "Feb 2025",
        "Domain": "toughbuilt.com",
        "endpoints": 250,
        "revenue": 4421.00,
        "edition": "Enterprise",
        "license_date": "28/2/2025",
        "product": "Endpoint Central MSP Cloud",
        "country": "US",
        "industry": "Construction tools and accessories",
        "type": "Zero Cost",
        "cpl": 0.00
    },
    {
        "update_as": "Mar 2025",
        "Domain": "bensonsforbed.co.uk",
        "endpoints": 60,
        "revenue": 101.12,
        "edition": "Professional (Monthly payment)",
        "license_date": "3/3/2025",
        "product": "PMP Cloud",
        "country": "UK",
        "industry": "Retail",
        "type": "Purchased",
        "cpl": 0.60
    },
    {
        "update_as": "Mar 2025",
        "Domain": "buckeyebroadband.com",
        "endpoints": 2800,
        "revenue": 62810.20,
        "edition": "UEM",
        "license_date": "4/3/2025",
        "product": "Endpoint Central Cloud",
        "country": "US",
        "industry": "Telecommunications",
        "type": "Purchased",
        "cpl": 0.40
    },
    {
        "update_as": "Mar 2025",
        "Domain": "apsystem.it",
        "endpoints": 52,
        "revenue": 535.70,
        "edition": "Enterprise",
        "license_date": "14/3/2025",
        "product": "VMP",
        "country": "Netherlands",
        "industry": "Renewable energy sector",
        "type": "Zero Cost",
        "cpl": 0.00
    },
    {
        "update_as": "Mar 2025",
        "Domain": "apsystem.it",
        "endpoints": 52,
        "revenue": 2338.25,
        "edition": "Enterprise",
        "license_date": "14/3/2025",
        "product": "Endpoint Central",
        "country": "Netherlands",
        "industry": "Renewable energy sector",
        "type": "Zero Cost",
        "cpl": 0.00
    },
    {
        "update_as": "Mar 2025",
        "Domain": "aaml.com.sa",
        "endpoints": 525,
        "revenue": 3055.50,
        "edition": "Enterprise",
        "license_date": "28/3/2025",
        "product": "Patch Manager Plus",
        "country": "Saudi Arabia",
        "industry": "Diagnostic imaging services",
        "type": "Zero Cost",
        "cpl": 0.00
    },
    {
        "update_as": "Mar 2025",
        "Domain": "acmcle.com.hk",
        "endpoints": 100,
        "revenue": 255.94,
        "edition": "Professional",
        "license_date": "10/3/2025",
        "product": "Patch Manager Plus",
        "country": "Hong Kong",
        "industry": "Educational",
        "type": "Zero Cost",
        "cpl": 0.00
    },
    {
        "update_as": "Mar 2025",
        "Domain": "aurigaspa.com",
        "endpoints": 680,
        "revenue": 42104.70,
        "edition": "Security",
        "license_date": "31/3/2025",
        "product": "Endpoint Central",
        "country": "Italy",
        "industry": "Information Technology and Services",
        "type": "Zero Cost",
        "cpl": 0.00
    },
    {
        "update_as": "Mar 2025",
        "Domain": "nagase-nam.com",
        "endpoints": 150,
        "revenue": 4112.00,
        "edition": "Enterprise",
        "license_date": "26/3/2025",
        "product": "Endpoint Central Cloud",
        "country": "US",
        "industry": "Chemical Manufacturing",
        "type": "Purchased",
        "cpl": 0.40
    },
  {
    "update_as": "Apr 2025",
    "Domain": "1st-edge.com",
    "endpoints": 175,
    "revenue": 3010.00,
    "edition": "Enterprise",
    "license_date": "30/4/2025",
    "product": "VMP",
    "country": "US",
    "industry": "Defense and Space Manufacturing",
    "type": "Purchased",
    "cpl": 0.40
  },
  {
    "update_as": "Apr 2025",
    "Domain": "agrikemilau.com",
    "endpoints": 50,
    "revenue": 838.50,
    "edition": "Enterprise",
    "license_date": "23/4/2025",
    "product": "Endpoint Central",
    "country": "Indonesia",
    "industry": "Agriculture",
    "type": "Zero Cost",
    "cpl": 0.00
  },
  {
    "update_as": "Apr 2025",
    "Domain": "apsystems.tech",
    "endpoints": 100,
    "revenue": 2844.00,
    "edition": "Security",
    "license_date": "15/4/2025",
    "product": "Endpoint Central Cloud",
    "country": "Poland",
    "industry": "Solar Energy / Renewable Energy",
    "type": "Zero Cost",
    "cpl": 0.00
  },
  {
    "update_as": "Apr 2025",
    "Domain": "cna.org.br",
    "endpoints": 515,
    "revenue": 4024.00,
    "edition": "Professional",
    "license_date": "2/4/2025",
    "product": "Endpoint Central",
    "country": "Brazil",
    "industry": "Nonprofit Research and Analysis",
    "type": "Zero Cost",
    "cpl": 0.00
  },
  {
    "update_as": "Apr 2025",
    "Domain": "fairmountpark.com",
    "endpoints": 180,
    "revenue": 9492.00,
    "edition": "Security",
    "license_date": "30/4/2025",
    "product": "Endpoint Central Cloud",
    "country": "US, Canada",
    "industry": "Gambling Facilities and Casinos",
    "type": "Purchased",
    "cpl": 0.40
  },
  {
    "update_as": "Apr 2025",
    "Domain": "geniodiligence.it",
    "endpoints": 85,
    "revenue": 3630.00,
    "edition": "Security",
    "license_date": "30/4/2025",
    "product": "Endpoint Central",
    "country": "Italy",
    "industry": "Banking / Fintech",
    "type": "Zero Cost",
    "cpl": 0.00
  },
  {
    "update_as": "Apr 2025",
    "Domain": "harrisseeds.com",
    "endpoints": 135,
    "revenue": 5549.00,
    "edition": "Enterprise",
    "license_date": "24/4/2025",
    "product": "Endpoint Central Cloud",
    "country": "US",
    "industry": "Farming / Horticulture",
    "type": "Purchased",
    "cpl": 0.40
  },
  {
    "update_as": "Apr 2025",
    "Domain": "lamache.org",
    "endpoints": 925,
    "revenue": 28035.00,
    "edition": "UEM",
    "license_date": "9/4/2025",
    "product": "Endpoint Central",
    "country": "France",
    "industry": "Education / Vocational Training",
    "type": "Zero Cost",
    "cpl": 0.00
  },
  {
    "update_as": "Apr 2025",
    "Domain": "medicareonline.it",
    "endpoints": 400,
    "revenue": 13180.00,
    "edition": "Professional",
    "license_date": "30/4/2025",
    "product": "Mobile Device Manager Plus Cloud",
    "country": "Italy",
    "industry": "Healthcare Data Analytics",
    "type": "Zero Cost",
    "cpl": 0.00
  },
  {
    "update_as": "Apr 2025",
    "Domain": "prosearch.com",
    "endpoints": 1755,
    "revenue": 43862.00,
    "edition": "Security",
    "license_date": "30/4/2025",
    "product": "Endpoint Central",
    "country": "US",
    "industry": "Legal Technology / E-Discovery",
    "type": "Purchased",
    "cpl": 0.00
  },
  {
    "update_as": "Apr 2025",
    "Domain": "sau53.org",
    "endpoints": 55,
    "revenue": 3819.00,
    "edition": "Enterprise",
    "license_date": "26/4/2025",
    "product": "Patch Manager Plus",
    "country": "US",
    "industry": "Education",
    "type": "Purchased",
    "cpl": 0.00
  },
  {
    "update_as": "Apr 2025",
    "Domain": "shieldcompany.com.br",
    "endpoints": 320,
    "revenue": 6372.00,
    "edition": "Security",
    "license_date": "2/4/2025",
    "product": "Endpoint Central",
    "country": "Brazil",
    "industry": "Healthcare Logistics / Cold Chain Solutions",
    "type": "Zero Cost",
    "cpl": 0.00
  },
  {
    "update_as": "Apr 2025",
    "Domain": "whitelabgx.com",
    "endpoints": 70,
    "revenue": 3322.40,
    "edition": "Security",
    "license_date": "10/4/2025",
    "product": "Endpoint Central Cloud",
    "country": "France",
    "industry": "Biotechnology Research",
    "type": "Zero Cost",
    "cpl": 0.00
  },
  {
    "update_as": "Apr 2025",
    "Domain": "grupocox.com",
    "endpoints": 5000,
    "revenue": 44805.00,
    "edition": "Security",
    "license_date": "26/4/2025",
    "product": "Endpoint Central Cloud",
    "country": "Spain",
    "industry": "Water and Energy Utilities",
    "type": "Zero Cost",
    "cpl": 0.00
  },
  {
    "update_as": "Apr 2025",
    "Domain": "hindujahousingfinance.com",
    "endpoints": 2515,
    "revenue": 32095.40,
    "edition": "Security",
    "license_date": "30/4/2025",
    "product": "Endpoint Central Cloud",
    "country": "India",
    "industry": "Financial Services / Housing Finance",
    "type": "Zero Cost",
    "cpl": 0.00
  },
 {
        "update_as": "May 2025",
        "Domain": "hirschsecure.com",
        "endpoints": 206,
        "revenue": 4865.00,
        "edition": "Enterprise",
        "license_date": "7/5/2025",
        "product": "Endpoint Central",
        "country": "US",
        "industry": "Security Technology",
        "type": "Purchased",
        "cpl": 0.40
    },
    {
        "update_as": "May 2025",
        "Domain": "vulcabras.com",
        "endpoints": 1900,
        "revenue": 22000.00,
        "edition": "Security",
        "license_date": "31/5/2025",
        "product": "Endpoint Central",
        "country": "Brazil",
        "industry": "Footwear Manufacturing",
        "type": "Zero Cost",
        "cpl": 0.00
    },
    {
        "update_as": "May 2025",
        "Domain": "xops.io",
        "endpoints": 120,
        "revenue": 1180.00,
        "edition": "Enterprise",
        "license_date": "10/5/2025",
        "product": "PMP Cloud",
        "country": "US",
        "industry": "Software Development / IT Operations",
        "type": "Purchased",
        "cpl": 0.40
    },
    {
        "update_as": "May 2025",
        "Domain": "wasa-technologies.com",
        "endpoints": 100,
        "revenue": 1174.25,
        "edition": "Professional",
        "license_date": "15/5/2025",
        "product": "Endpoint Central",
        "country": "Germany",
        "industry": "Concrete Production Technology",
        "type": "Zero cost",
        "cpl": 0.00
    },
    {
        "update_as": "May 2025",
        "Domain": "landform.ca",
        "endpoints": 38,
        "revenue": 920.00,
        "edition": "Professional",
        "license_date": "9/5/2025",
        "product": "MDM OnDemand",
        "country": "Canada",
        "industry": "Landscape Construction",
        "type": "Zero Cost",
        "cpl": 0.00
    },
    {
        "update_as": "May 2025",
        "Domain": "kokusai-electric.com",
        "endpoints": 310,
        "revenue": 27240.00,
        "edition": "UEM",
        "license_date": "15/5/2025",
        "product": "Endpoint Central",
        "country": "US",
        "industry": "Semiconductor Manufacturing Equipment",
        "type": "Purchased",
        "cpl": 0.40
    },
    {
        "update_as": "May 2025",
        "Domain": "it-advisor.ch",
        "endpoints": 50,
        "revenue": 1677.00,
        "edition": "Enterprise",
        "license_date": "31/5/2025",
        "product": "Patch Manager Plus",
        "country": "Switzerland",
        "industry": "IT Consulting",
        "type": "Zero Cost",
        "cpl": 0.00
    },
    {
        "update_as": "May 2025",
        "Domain": "bonollo.it",
        "endpoints": 125,
        "revenue": 438.69,
        "edition": "Enterprise",
        "license_date": "24/5/2025",
        "product": "Vulnerability Manager Plus",
        "country": "Italy",
        "industry": "Spirits & Distillation",
        "type": "Zero Cost",
        "cpl": 0.00
    },
    {
        "update_as": "May 2025",
        "Domain": "bonollo.it",
        "endpoints": 125,
        "revenue": 1687.68,
        "edition": "Enterprise",
        "license_date": "24/5/2025",
        "product": "Endpoint Central",
        "country": "Italy",
        "industry": "Spirits & Distillation",
        "type": "Zero Cost",
        "cpl": 0.00
    },
    {
        "update_as": "May 2025",
        "Domain": "bonollo.it",
        "endpoints": 125,
        "revenue": 752.40,
        "edition": "Enterprise",
        "license_date": "24/5/2025",
        "product": "OS Deployer",
        "country": "Italy",
        "industry": "Spirits & Distillation",
        "type": "Zero Cost",
        "cpl": 0.00
    },
    {
        "update_as": "May 2025",
        "Domain": "merchantscx.co.za",
        "endpoints": 3800,
        "revenue": 21686.25,
        "edition": "Enterprise",
        "license_date": "29/5/2025",
        "product": "Endpoint Central",
        "country": "South Africa",
        "industry": "Customer Experience Management",
        "type": "Zero Cost",
        "cpl": 0.00
    },
    {
        "update_as": "May 2025",
        "Domain": "asp.gov.md",
        "endpoints": 2500,
        "revenue": 14323.40,
        "edition": "Professional",
        "license_date": "17/5/2025",
        "product": "Device Control Plus",
        "country": "Romania",
        "industry": "Government Services",
        "type": "Zero Cost",
        "cpl": 0.00
    },
    {
        "update_as": "May 2025",
        "Domain": "ny-creates.org",
        "endpoints": 1100,
        "revenue": 64950.00,
        "edition": "Security",
        "license_date": "13/5/2025",
        "product": "Endpoint Central Cloud",
        "country": "US",
        "industry": "Semiconductor Research & Development",
        "type": "Purchased",
        "cpl": 0.40
    },
    {
        "update_as": "May 2025",
        "Domain": "nederlander.com",
        "endpoints": 250,
        "revenue": 20220.00,
        "edition": "UEM",
        "license_date": "13/5/2025",
        "product": "Endpoint Central Cloud",
        "country": "US",
        "industry": "Live Entertainment",
        "type": "Purchased",
        "cpl": 0.40
    },
    {
        "update_as": "May 2025",
        "Domain": "abxnetwork.pro",
        "endpoints": 1000,
        "revenue": 16158.00,
        "edition": "Security",
        "license_date": "10/5/2025",
        "product": "Endpoint Central",
        "country": "Cyprus",
        "industry": "Blockchain & Cryptocurrency",
        "type": "Zero Cost",
        "cpl": 0.00
    },
    {
        "update_as": "May 2025",
        "Domain": "pedongroup.com",
        "endpoints": 120,
        "revenue": 2038.57,
        "edition": "Enterprise",
        "license_date": "30/5/2025",
        "product": "Endpoint Central Cloud",
        "country": "Italy",
        "industry": "Construction & Real Estate",
        "type": "Zero Cost",
        "cpl": 0.00
    },
    {
        "update_as": "May 2025",
        "Domain": "schur.com",
        "endpoints": 1000,
        "revenue": 20814.30,
        "edition": "Security",
        "license_date": "16/5/2025",
        "product": "Endpoint Central Cloud",
        "country": "Denmark",
        "industry": "Packaging Solutions",
        "type": "Zero Cost",
        "cpl": 0.00
    },
    {
        "update_as": "May 2025",
        "Domain": "adlerpelzer.com",
        "endpoints": 5500,
        "revenue": 16264.45,
        "edition": "Enterprise",
        "license_date": "21/5/2025",
        "product": "Patch Manager Plus",
        "country": "Germany",
        "industry": "Automotive manufacturing",
        "type": "Zero Cost",
        "cpl": 0.00
    },

]


# Function to process data
def process_data(df):
    # Make a copy to avoid modifying the original
    df = df.copy()

    # Basic data cleaning
    if 'revenue' in df.columns:
        df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')

    if 'endpoints' in df.columns:
        df['endpoints'] = pd.to_numeric(df['endpoints'], errors='coerce')

    # Ensure update_as is string type
    if 'update_as' in df.columns:
        df['update_as'] = df['update_as'].astype(str)
        df['month'] = df['update_as'].str.split(' ').str[0]

    # Calculate deployment type based on product name
    if 'product' in df.columns:
        df['product'] = df['product'].astype(str)
        df['deployment'] = df['product'].str.lower().apply(lambda x: 'Cloud' if 'cloud' in str(x) else 'On-Premises')

    # Clean edition
    if 'edition' in df.columns:
        df['edition'] = df['edition'].astype(str)
        df['edition_simple'] = df['edition'].str.split(' ').str[0]

    return df


# Convert data to DataFrame and process
df = pd.DataFrame(data)
processed_df = process_data(df)

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

# Add Domain Distribution Analysis - New Visualization
domain_count = processed_df['Domain'].value_counts().reset_index()
domain_count.columns = ['Domain', 'Count']
domain_count = domain_count[domain_count['Domain'] != ''].head(10)  # Top 10 domains, excluding empty

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
st.markdown("<p style='text-align: center; color: gray;'>© 2025 Revenue Analytics Dashboard</p>",
            unsafe_allow_html=True)
