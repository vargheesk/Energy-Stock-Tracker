"""
extract.py - Get stock data from Yahoo Finance
This file downloads stock prices from the internet
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_stock_data(symbols, days_back=90):
    """
    Download stock data for multiple companies
    
    symbols: list of stock symbols like ['XOM', 'BP', 'CVX']
    days_back: how many days of history to get (default 90 days)
    
    Returns: pandas DataFrame with all stock data
    """
    
    # Calculate start and end dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    print(f"📥 Downloading stock data from {start_date.date()} to {end_date.date()}")
    
    # This will store all the data
    all_stock_data = []
    
    # Loop through each stock symbol
    for symbol in symbols:
        print(f"   Getting data for {symbol}...")
        
        try:
            # Download data from Yahoo Finance
            stock = yf.Ticker(symbol)
            df = stock.history(start=start_date, end=end_date)
            
            # Check if we got data
            if df.empty:
                print(f"   ⚠️  No data found for {symbol}")
                continue
            
            # Reset index to make Date a regular column
            df = df.reset_index()
            
            # Add the stock symbol to each row
            df['symbol'] = symbol
            
            # Rename columns to simpler names
            df = df.rename(columns={
                'Date': 'date',
                'Open': 'open_price',
                'High': 'high_price',
                'Low': 'low_price',
                'Close': 'close_price',
                'Volume': 'volume'
            })
            
            # Keep only the columns we need
            df = df[['date', 'symbol', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']]
            
            # Convert date to just date (remove time)
            df['date'] = pd.to_datetime(df['date']).dt.date
            
            # Add this stock's data to our collection
            all_stock_data.append(df)
            
            print(f"   ✅ Got {len(df)} days of data for {symbol}")
            
        except Exception as e:
            print(f"   ❌ Error getting {symbol}: {e}")
            continue
    
    # Combine all stock data into one big table
    if all_stock_data:
        final_df = pd.concat(all_stock_data, ignore_index=True)
        print(f"\n✅ Total records downloaded: {len(final_df)}")
        return final_df
    else:
        print("❌ No data was downloaded")
        return pd.DataFrame()


def get_oil_price(days_back=90):
    """
    Download oil price data (WTI Crude Oil)
    
    days_back: how many days of history to get
    
    Returns: pandas DataFrame with oil prices
    """
    
    print(f"\n🛢️  Downloading oil price data...")
    
    try:
        # WTI Crude Oil symbol
        oil_symbol = "CL=F"
        
        # Calculate dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Download oil data
        oil = yf.Ticker(oil_symbol)
        df = oil.history(start=start_date, end=end_date)
        
        if df.empty:
            print("   ⚠️  No oil price data found")
            return pd.DataFrame()
        
        # Reset index and simplify
        df = df.reset_index()
        df = df[['Date', 'Close']]
        df = df.rename(columns={'Date': 'date', 'Close': 'oil_price'})
        df['date'] = pd.to_datetime(df['date']).dt.date
        
        print(f"   ✅ Got {len(df)} days of oil prices")
        return df
        
    except Exception as e:
        print(f"   ❌ Error getting oil prices: {e}")
        return pd.DataFrame()


# Test function - run this file directly to test
if __name__ == "__main__":
    # Test with a few symbols
    test_symbols = ['XOM', 'BP', 'TSLA']
    data = get_stock_data(test_symbols, days_back=30)
    
    if not data.empty:
        print("\n📊 Sample data:")
        print(data.head())
        
    oil_data = get_oil_price(days_back=30)
    if not oil_data.empty:
        print("\n🛢️  Sample oil data:")
        print(oil_data.head())