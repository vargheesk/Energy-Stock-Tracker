"""
load.py - Save data to Supabase database
This file uploads the transformed data to the database
"""

import pandas as pd
from supabase import create_client, Client
from datetime import datetime


def connect_to_supabase(url, key):
    """
    Connect to Supabase database
    
    url: your Supabase project URL
    key: your Supabase API key
    
    Returns: Supabase client
    """
    
    print("\n🔌 Connecting to Supabase...")
    
    try:
        supabase = create_client(url, key)
        print("   ✅ Connected to Supabase")
        return supabase
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return None


def get_companies_from_db(supabase):
    """
    Get list of companies from database
    
    supabase: Supabase client
    
    Returns: dictionary mapping symbol to (name, sector)
    """
    
    print("\n📋 Getting companies from database...")
    
    try:
        # SELECT query to get all companies
        response = supabase.table('companies').select('*').execute()
        
        companies_dict = {}
        for company in response.data:
            symbol = company['symbol']
            name = company['name']
            sector = company['sector']
            companies_dict[symbol] = (name, sector)
        
        print(f"   ✅ Got {len(companies_dict)} companies")
        return companies_dict
        
    except Exception as e:
        print(f"   ❌ Error getting companies: {e}")
        return {}


def load_stock_data(supabase, df):
    """
    Save stock data to database
    
    supabase: Supabase client
    df: pandas DataFrame with transformed stock data
    
    Returns: number of rows inserted
    """
    
    print("\n💾 Saving stock data to database...")
    
    if df.empty:
        print("   ⚠️  No data to save")
        return 0
    
    # Convert DataFrame to list of dictionaries
    records = df.to_dict('records')
    
    # Convert date objects to strings
    for record in records:
        if 'date' in record:
            record['date'] = str(record['date'])
    
    inserted_count = 0
    failed_count = 0
    
    # Insert records one batch at a time (Supabase handles duplicates)
    batch_size = 100
    total_batches = (len(records) + batch_size - 1) // batch_size
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        try:
            # Insert or update if record exists (upsert)
            response = supabase.table('stock_data').upsert(batch).execute()
            inserted_count += len(batch)
            print(f"   ✅ Batch {batch_num}/{total_batches}: saved {len(batch)} records")
            
        except Exception as e:
            failed_count += len(batch)
            print(f"   ❌ Batch {batch_num}/{total_batches} failed: {e}")
    
    print(f"\n   📊 Results: {inserted_count} saved, {failed_count} failed")
    return inserted_count


def log_etl_run(supabase, rows_inserted, status, notes=""):
    """
    Save ETL run information to log table
    
    supabase: Supabase client
    rows_inserted: number of rows inserted
    status: 'success' or 'failed'
    notes: any additional notes
    """
    
    print("\n📝 Logging ETL run...")
    
    try:
        log_entry = {
            'run_time': datetime.now().isoformat(),
            'rows_inserted': rows_inserted,
            'status': status,
            'notes': notes
        }
        
        supabase.table('etl_log').insert(log_entry).execute()
        print(f"   ✅ ETL run logged")
        
    except Exception as e:
        print(f"   ⚠️  Failed to log ETL run: {e}")


def get_recent_data(supabase, days=7):
    """
    Get recent stock data from database
    
    supabase: Supabase client
    days: number of recent days to get
    
    Returns: pandas DataFrame
    """
    
    print(f"\n📊 Getting last {days} days of data...")
    
    try:
        # Simple SELECT query with ORDER BY and LIMIT
        response = supabase.table('stock_data')\
            .select('*')\
            .order('date', desc=True)\
            .limit(days * 10)\
            .execute()
        
        df = pd.DataFrame(response.data)
        print(f"   ✅ Got {len(df)} records")
        return df
        
    except Exception as e:
        print(f"   ❌ Error getting data: {e}")
        return pd.DataFrame()


def get_all_stock_data(supabase):
    """
    Get ALL stock data from database
    
    supabase: Supabase client
    
    Returns: pandas DataFrame with all data
    """
    
    print("\n📊 Getting all stock data from database...")
    
    try:
        # Simple SELECT query to get everything
        response = supabase.table('stock_data').select('*').execute()
        
        df = pd.DataFrame(response.data)
        print(f"   ✅ Got {len(df)} total records")
        return df
        
    except Exception as e:
        print(f"   ❌ Error getting data: {e}")
        return pd.DataFrame()


def get_top_gainers_losers(supabase, date=None, limit=5):
    """
    Get top gaining and losing stocks for a specific date
    
    supabase: Supabase client
    date: specific date (default: latest date)
    limit: how many top/bottom stocks to show
    
    Returns: tuple of (gainers_df, losers_df)
    """
    
    print(f"\n📈 Getting top {limit} gainers and losers...")
    
    try:
        # If no date specified, get latest date
        if date is None:
            response = supabase.table('stock_data')\
                .select('date')\
                .order('date', desc=True)\
                .limit(1)\
                .execute()
            
            if response.data:
                date = response.data[0]['date']
        
        # Get all data for that date
        response = supabase.table('stock_data')\
            .select('*')\
            .eq('date', date)\
            .execute()
        
        df = pd.DataFrame(response.data)
        
        if df.empty:
            print(f"   ⚠️  No data found for date {date}")
            return pd.DataFrame(), pd.DataFrame()
        
        # Sort by percent change
        df = df.sort_values('pct_change', ascending=False)
        
        # Get top gainers and losers
        gainers = df.head(limit)
        losers = df.tail(limit)
        
        print(f"   ✅ Got top {limit} gainers and losers for {date}")
        return gainers, losers
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return pd.DataFrame(), pd.DataFrame()


# Test function
if __name__ == "__main__":
    print("⚠️  This file needs to be run with valid Supabase credentials")
    print("   Set SUPABASE_URL and SUPABASE_KEY in your .env file")