"""
streamlit_app.py - Interactive Dashboard for Energy Stock Tracker
This creates a web dashboard to visualize the stock data
Run with: streamlit run dashboard/streamlit_app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Energy Stock Tracker",
    page_icon="📈",
    layout="wide"
)

# Connect to Supabase
@st.cache_resource
def init_supabase():
    """Connect to Supabase database, using Streamlit secrets as priority."""
    
    # 1. Try to get secrets from Streamlit Cloud (or local secrets.toml)
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except:
        # 2. Fallback to os.getenv (for local testing via .env file)
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
    if not url or not key:
        st.error("Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_KEY.")
        return None
        
    return create_client(url, key)

supabase = init_supabase()


# Get all stock data
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    """Load all stock data from database"""
    response = supabase.table('stock_data').select('*').execute()
    df = pd.DataFrame(response.data)
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
    
    return df


# Get companies list
@st.cache_data(ttl=3600)
def load_companies():
    """Load companies from database"""
    response = supabase.table('companies').select('*').execute()
    return pd.DataFrame(response.data)


# Main app
def main():
    """Main dashboard function"""
    
    # Title
    st.title("📈 Energy Stock Tracker Dashboard")
    st.markdown("Track daily stock prices of energy companies with technical indicators")
    
    # Load data
    with st.spinner("Loading data from database..."):
        df = load_data()
        companies_df = load_companies()
    
    if df.empty:
        st.error("⚠️ No data found! Please run the ETL pipeline first.")
        st.code("python main.py")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Date range filter
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(max_date - timedelta(days=30), max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Company filter
    all_symbols = sorted(df['symbol'].unique())
    selected_symbols = st.sidebar.multiselect(
        "Select Companies",
        options=all_symbols,
        default=all_symbols[:5]  # Default to first 5
    )
    
    # Sector filter
    all_sectors = sorted(df['sector'].unique())
    selected_sectors = st.sidebar.multiselect(
        "Select Sectors",
        options=all_sectors,
        default=all_sectors
    )
    
    # Filter data
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = df[
            (df['date'].dt.date >= start_date) &
            (df['date'].dt.date <= end_date) &
            (df['symbol'].isin(selected_symbols)) &
            (df['sector'].isin(selected_sectors))
        ]
    else:
        filtered_df = df[
            (df['symbol'].isin(selected_symbols)) &
            (df['sector'].isin(selected_sectors))
        ]
    
    if filtered_df.empty:
        st.warning("No data matches your filters. Please adjust your selection.")
        return
    
    # Key Metrics
    st.header("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Records",
            f"{len(filtered_df):,}"
        )
    
    with col2:
        avg_change = filtered_df['pct_change'].mean()
        st.metric(
            "Avg Daily Change",
            f"{avg_change:.2f}%"
        )
    
    with col3:
        latest_data = filtered_df[filtered_df['date'] == filtered_df['date'].max()]
        gainers = len(latest_data[latest_data['trend'] == 'up'])
        st.metric(
            "Gainers Today",
            gainers
        )
    
    with col4:
        avg_volatility = filtered_df['volatility'].mean()
        st.metric(
            "Avg Volatility",
            f"{avg_volatility:.2f}"
        )
    
    # Chart 1: Price Trends Over Time
    st.header("💹 Stock Price Trends")
    
    fig_line = px.line(
        filtered_df,
        x='date',
        y='close_price',
        color='symbol',
        title='Daily Closing Prices',
        labels={'close_price': 'Price ($)', 'date': 'Date'},
        hover_data=['company_name', 'pct_change']
    )
    fig_line.update_layout(height=500)
    st.plotly_chart(fig_line, use_container_width=True)
    
    # Chart 2: Moving Averages
    st.header("📉 Moving Averages (7-day & 30-day)")
    
    # Let user select one company for MA chart
    ma_symbol = st.selectbox("Select Company for Moving Averages", selected_symbols)
    ma_data = filtered_df[filtered_df['symbol'] == ma_symbol].sort_values('date')
    
    fig_ma = go.Figure()
    fig_ma.add_trace(go.Scatter(x=ma_data['date'], y=ma_data['close_price'],
                                 name='Close Price', line=dict(color='blue')))
    fig_ma.add_trace(go.Scatter(x=ma_data['date'], y=ma_data['ma_7'],
                                 name='7-Day MA', line=dict(color='orange')))
    fig_ma.add_trace(go.Scatter(x=ma_data['date'], y=ma_data['ma_30'],
                                 name='30-Day MA', line=dict(color='red')))
    fig_ma.update_layout(title=f'{ma_symbol} - Price vs Moving Averages', height=400)
    st.plotly_chart(fig_ma, use_container_width=True)
    
    # Chart 3: Top Gainers & Losers
    st.header("🏆 Top Performers (Latest Date)")
    
    latest_date = filtered_df['date'].max()
    latest_data = filtered_df[filtered_df['date'] == latest_date].sort_values('pct_change')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Top Gainers")
        gainers = latest_data.nlargest(5, 'pct_change')[['symbol', 'company_name', 'close_price', 'pct_change']]
        st.dataframe(gainers, hide_index=True)
    
    with col2:
        st.subheader("📉 Top Losers")
        losers = latest_data.nsmallest(5, 'pct_change')[['symbol', 'company_name', 'close_price', 'pct_change']]
        st.dataframe(losers, hide_index=True)
    
    # Chart 4: Sector Comparison
    st.header("🏭 Sector Performance")
    
    sector_avg = filtered_df.groupby(['date', 'sector'])['close_price'].mean().reset_index()
    
    fig_sector = px.line(
        sector_avg,
        x='date',
        y='close_price',
        color='sector',
        title='Average Price by Sector',
        labels={'close_price': 'Avg Price ($)', 'date': 'Date'}
    )
    fig_sector.update_layout(height=400)
    st.plotly_chart(fig_sector, use_container_width=True)
    
    # Chart 5: Volatility Heatmap
    st.header("🔥 Volatility Heatmap")
    
    # Get latest volatility for each stock
    latest_vol = filtered_df[filtered_df['date'] == filtered_df['date'].max()][['symbol', 'volatility']].sort_values('volatility', ascending=False)
    
    fig_vol = px.bar(
        latest_vol,
        x='symbol',
        y='volatility',
        title='Stock Volatility (Latest)',
        labels={'volatility': 'Volatility', 'symbol': 'Company'},
        color='volatility',
        color_continuous_scale='Reds'
    )
    fig_vol.update_layout(height=400)
    st.plotly_chart(fig_vol, use_container_width=True)
    
    # Data Table
    st.header("📋 Detailed Data Table")
    
    # Select columns to display
    display_cols = ['date', 'symbol', 'company_name', 'sector', 'close_price', 
                   'pct_change', 'ma_7', 'ma_30', 'volume', 'trend']
    
    display_df = filtered_df[display_cols].sort_values('date', ascending=False)
    
    # Add color coding to trend column
    def color_trend(val):
        if val == 'up':
            return 'background-color: lightgreen'
        elif val == 'down':
            return 'background-color: lightcoral'
        return ''
    
    styled_df = display_df.style.applymap(color_trend, subset=['trend'])
    
    st.dataframe(styled_df, height=400)
    
    # Download button
    st.download_button(
        label="📥 Download Data as CSV",
        data=filtered_df.to_csv(index=False),
        file_name=f"energy_stocks_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    # Footer
    st.markdown("---")
    st.markdown("📊 Data updated automatically via ETL pipeline | Powered by yFinance & Supabase")


if __name__ == "__main__":
    main()