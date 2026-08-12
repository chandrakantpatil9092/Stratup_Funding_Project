import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from click import option


# Load Data
df = pd.read_csv('startup_funding.csv')

# Drop Columns
df.drop(columns=['SNo', 'Remarks'], inplace=True)

# Rename Columns
df.rename(columns={
    'Date dd/mm/yyyy': 'Date',
    'StartupName': 'startup',
    'IndustryVertical': 'vertical',
    'SubVertical': 'subvertical',
    'CityLocation': 'city',
    'InvestorsName': 'investor',
    'InvestmentType': 'round',
    'AmountInUSD': 'amount'
}, inplace=True)

# Date Cleaning
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

df['year'] = df['Date'].dt.year
df['month'] = df['Date'].dt.month

# Amount Cleaning
df['amount'] = (
    df['amount']
    .astype(str)
    .str.replace(',', '')
    .str.replace('$', '')
)

df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

# Investor Cleaning
df['investor'] = (
    df['investor']
    .astype(str)
    .str.lower()
    .str.replace(r'\(.*?\)', '', regex=True)
    .str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
    .str.replace(r'\s+', ' ', regex=True)
    .str.strip()
)

# Startup Cleaning
df['startup'] = (
    df['startup']
    .astype(str)
    .str.lower()
    .str.replace(r'xe2x80x99', '', regex=True)
    .str.replace(r'[^a-z0-9\s]', '', regex=True)
    .str.replace(r'\s+', ' ', regex=True)
    .str.strip()
)

# Unique Lists
startup_list = sorted(df['startup'].dropna().unique().tolist())
investor_list = sorted(df['investor'].dropna().unique().tolist())

# Sidebar
st.sidebar.title('Indian Startup Funding Analysis')

options = st.sidebar.selectbox(
    'Select Option',
    ['Overall Analysis', 'Startup', 'Investor']
)

# ================= OVERALL ANALYSIS =================

if options == 'Overall Analysis':

    st.title('Overall Startup Funding Analysis')

    # Cards
    total = round(df['amount'].sum())

    max_funding = round(
        df.groupby('startup')['amount']
        .sum()
        .sort_values(ascending=False)
        .values[0]
    )

    avg_funding = round(
        df.groupby('startup')['amount']
        .sum()
        .mean()
    )

    total_startups = df['startup'].nunique()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric('Total Funding', f"${total:,}")
    col2.metric('Max Funding', f"${max_funding:,}")
    col3.metric('Average Funding', f"${avg_funding:,}")
    col4.metric('Total Startups', total_startups)

    # Month on Month Chart
    st.subheader('Month on Month Funding Count')

    temp = df.groupby(['year', 'month'])['startup'].count().reset_index()

    temp['x'] = temp['month'].astype(str) + "-" + temp['year'].astype(str)

    fig = px.line(
        temp,
        x='x',
        y='startup'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Sector Analysis
    st.subheader('Top Sectors')

    sector = (
        df.groupby('vertical')['amount']
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    fig = px.pie(
        values=sector.values,
        names=sector.index
    )

    st.plotly_chart(fig, use_container_width=True)

    # City Wise Funding
    st.subheader('City Wise Funding')

    city = (
        df.groupby('city')['amount']
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    fig = px.bar(
        x=city.index,
        y=city.values
    )

    st.plotly_chart(fig, use_container_width=True)

    # Top Startups
    st.subheader('Top Startups')

    top_startups = (
        df.groupby('startup')['amount']
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    st.dataframe(top_startups)

    # Top Investors
    st.subheader('Top Investors')

    top_investors = df['investor'].value_counts().head(10)

    st.dataframe(top_investors)

    # Heatmap
    st.subheader('Funding Heatmap')

    heatmap = df.pivot_table(
        index='city',
        columns='year',
        values='amount',
        aggfunc='sum'
    )

    st.dataframe(heatmap)

# ================= STARTUP ANALYSIS =================

elif options == 'Startup':

    selected_startup = st.sidebar.selectbox(
        'Select Startup',
        startup_list
    )

    st.title(selected_startup.upper())

    startup_df = df[df['startup'] == selected_startup]

    # Basic Details
    st.subheader('Basic Details')

    st.write('Industry:', startup_df['vertical'].iloc[0])
    st.write('SubIndustry:', startup_df['subvertical'].iloc[0])
    st.write('Location:', startup_df['city'].iloc[0])

    # Funding Rounds
    st.subheader('Funding Rounds')

    st.dataframe(
        startup_df[
            ['Date', 'round', 'investor', 'amount']
        ]
    )

    # Total Funding
    st.subheader('Total Funding')

    st.metric(
        'Funding Raised',
        f"${round(startup_df['amount'].sum()):,}"
    )

    # Similar Startups
    st.subheader('Similar Startups')

    similar = df[
        df['vertical'] == startup_df['vertical'].iloc[0]
    ]['startup'].unique()

    st.write(similar)

# ================= INVESTOR ANALYSIS =================

elif options == 'Investor':

    selected_investor = st.sidebar.selectbox(
        'Select Investor',
        investor_list
    )

    st.title(selected_investor.upper())

    investor_df = df[df['investor'] == selected_investor]

    # Recent Investments
    st.subheader('Recent Investments')

    recent = investor_df.sort_values(
        'Date',
        ascending=False
    )[
        ['Date', 'startup', 'vertical', 'city', 'amount']
    ]

    st.dataframe(recent)

    # Biggest Investments
    st.subheader('Biggest Investments')

    biggest = investor_df.sort_values(
        'amount',
        ascending=False
    )[
        ['startup', 'amount']
    ].head(10)

    st.dataframe(biggest)

    # Generally Invests In
    st.subheader('Generally Invests In')

    sector = investor_df['vertical'].value_counts().head()

    fig = px.pie(
        values=sector.values,
        names=sector.index
    )

    st.plotly_chart(fig, use_container_width=True)