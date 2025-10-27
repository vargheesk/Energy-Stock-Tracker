"""
transform.py - Clean and calculate values for stock data
This file does math on the stock data to make it more useful
"""

import pandas as pd
import numpy as np


def clean_data(df):
    """
    Clean the stock data - remove bad values
    
    df: pandas DataFrame with stock data
    
    Returns: cleaned DataFrame
    """
    
    print("\n🧹 Cleaning data...")
    
    original_rows = len(df)
    
    # Remove duplicate rows (same date and symbol)
    df = df.drop_duplicates(subset=['date', 'symbol'], keep='last')
    
    # Remove rows where close_price is missing or zero
    df = df[df['close_price'] > 0]
    
    # Fill missing volume with 0
    df['volume'] = df['volume'].fillna(0)
    
    # Sort by symbol and date (important for calculations)
    df = df.sort_values(['symbol', 'date'])
    
    rows_removed = original_rows - len(df)
    print(f"   ✅ Cleaned data: removed {rows_removed} bad rows")
    
    return df


def calculate_percent_change(df):
    """
    Calculate daily percent change for each stock
    
    df: pandas DataFrame with stock data
    
    Returns: DataFrame with pct_change column added
    """
    
    print("\n📈 Calculating percent changes...")
    
    # Group by symbol (each stock separately)
    df['pct_change'] = df.groupby('symbol')['close_price'].pct_change() * 100
    
    # First day for each stock will have NaN, fill with 0
    df['pct_change'] = df['pct_change'].fillna(0)
    
    print(f"   ✅ Calculated percent changes")
    
    return df


def calculate_moving_averages(df):
    """
    Calculate 7-day and 30-day moving averages
    
    df: pandas DataFrame with stock data
    
    Returns: DataFrame with ma_7 and ma_30 columns added
    """
    
    print("\n📊 Calculating moving averages...")
    
    # Calculate 7-day moving average for each stock
    df['ma_7'] = df.groupby('symbol')['close_price'].transform(
        lambda x: x.rolling(window=7, min_periods=1).mean()
    )
    
    # Calculate 30-day moving average for each stock
    df['ma_30'] = df.groupby('symbol')['close_price'].transform(
        lambda x: x.rolling(window=30, min_periods=1).mean()
    )
    
    print(f"   ✅ Calculated moving averages")
    
    return df


def calculate_volatility(df):
    """
    Calculate 30-day volatility (how much price moves)
    
    df: pandas DataFrame with stock data
    
    Returns: DataFrame with volatility column added
    """
    
    print("\n📉 Calculating volatility...")
    
    # Calculate standard deviation of close price over 30 days
    df['volatility'] = df.groupby('symbol')['close_price'].transform(
        lambda x: x.rolling(window=30, min_periods=1).std()
    )
    
    # Fill missing values with 0
    df['volatility'] = df['volatility'].fillna(0)
    
    print(f"   ✅ Calculated volatility")
    
    return df


def add_trend_label(df):
    """
    Add trend label: 'up' if price increased, 'down' if decreased
    
    df: pandas DataFrame with stock data
    
    Returns: DataFrame with trend column added
    """
    
    print("\n🎯 Adding trend labels...")
    
    # If percent change is positive, trend is 'up', otherwise 'down'
    df['trend'] = df['pct_change'].apply(lambda x: 'up' if x > 0 else 'down' if x < 0 else 'flat')
    
    print(f"   ✅ Added trend labels")
    
    return df


def add_company_info(df, companies_dict):
    """
    Add company name and sector to the data
    
    df: pandas DataFrame with stock data
    companies_dict: dictionary mapping symbol to (name, sector)
    
    Returns: DataFrame with company_name and sector columns added
    """
    
    print("\n🏢 Adding company information...")
    
    # Add company name
    df['company_name'] = df['symbol'].map(lambda x: companies_dict.get(x, ('Unknown', 'Unknown'))[0])
    
    # Add sector
    df['sector'] = df['symbol'].map(lambda x: companies_dict.get(x, ('Unknown', 'Unknown'))[1])
    
    print(f"   ✅ Added company information")
    
    return df


def merge_oil_price(stock_df, oil_df):
    """
    Add oil price to stock data for each date
    
    stock_df: DataFrame with stock data
    oil_df: DataFrame with oil prices
    
    Returns: DataFrame with oil_price column added
    """
    
    print("\n🛢️  Merging oil prices...")
    
    if oil_df.empty:
        stock_df['oil_price'] = None
        print(f"   ⚠️  No oil price data to merge")
        return stock_df
    
    # Merge oil prices with stock data by date
    stock_df = stock_df.merge(oil_df, on='date', how='left')
    
    # Fill missing oil prices with previous day's price
    stock_df['oil_price'] = stock_df['oil_price'].fillna(method='ffill')
    
    print(f"   ✅ Merged oil prices")
    
    return stock_df


def transform_all(stock_df, oil_df, companies_dict):
    """
    Run all transformation steps
    
    stock_df: raw stock DataFrame
    oil_df: raw oil price DataFrame
    companies_dict: dictionary of company info
    
    Returns: fully transformed DataFrame ready for database
    """
    
    print("\n" + "="*50)
    print("🔄 STARTING DATA TRANSFORMATION")
    print("="*50)
    
    # Step 1: Clean data
    df = clean_data(stock_df)
    
    # Step 2: Add company information
    df = add_company_info(df, companies_dict)
    
    # Step 3: Calculate percent change
    df = calculate_percent_change(df)
    
    # Step 4: Calculate moving averages
    df = calculate_moving_averages(df)
    
    # Step 5: Calculate volatility
    df = calculate_volatility(df)
    
    # Step 6: Add trend labels
    df = add_trend_label(df)
    
    # Step 7: Merge oil prices
    df = merge_oil_price(df, oil_df)
    
    # Round decimal values to 2 places for readability
    numeric_cols = ['open_price', 'high_price', 'low_price', 'close_price', 
                    'pct_change', 'ma_7', 'ma_30', 'volatility', 'oil_price']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].round(2)
    
    print("\n" + "="*50)
    print(f"✅ TRANSFORMATION COMPLETE: {len(df)} rows ready")
    print("="*50)
    
    return df


# Test function
if __name__ == "__main__":
    # Create sample data for testing
    sample_data = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=10),
        'symbol': ['XOM'] * 10,
        'open_price': [100, 101, 102, 101, 103, 104, 103, 105, 106, 107],
        'high_price': [101, 102, 103, 102, 104, 105, 104, 106, 107, 108],
        'low_price': [99, 100, 101, 100, 102, 103, 102, 104, 105, 106],
        'close_price': [100.5, 101.5, 102.5, 101.5, 103.5, 104.5, 103.5, 105.5, 106.5, 107.5],
        'volume': [1000000] * 10
    })
    
    companies = {
        'XOM': ('Exxon Mobil', 'Oil & Gas')
    }
    
    oil_data = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=10),
        'oil_price': [75.5] * 10
    })
    
    result = transform_all(sample_data, oil_data, companies)
    print("\n📊 Sample transformed data:")
    print(result.head())