"""
api/etl.py - Vercel Serverless Function for ETL Pipeline
This endpoint is called by Uptime Robot to trigger the ETL process

URL will be: https://your-project.vercel.app/api/etl
"""

from flask import Flask, jsonify
import os
from datetime import datetime, time, timedelta
import pytz
from dotenv import load_dotenv



from etl.extract import get_stock_data, get_oil_price
from etl.transform import transform_all
from etl.load import (
    connect_to_supabase,
    get_companies_from_db,
    load_stock_data,
    log_etl_run
)

# Load environment variables
load_dotenv()

app = Flask(__name__)


def check_if_etl_ran_today(supabase):
    """
    Check if ETL has already run today
    Returns: True if ETL ran today, False if not
    """
    try:
        # Get today's date in IST
        ist = pytz.timezone('Asia/Kolkata')
        today = datetime.now(ist).date()
        
        # Query the etl_log table for today's runs
        response = supabase.table('etl_log')\
            .select('*')\
            .gte('run_time', f'{today} 00:00:00')\
            .lte('run_time', f'{today} 23:59:59')\
            .eq('status', 'success')\
            .execute()
        
        # If we have any successful runs today, return True
        if response.data and len(response.data) > 0:
            return True
        return False
        
    except Exception as e:
        print(f"Error checking ETL status: {e}")
        return False


def check_if_after_8am_ist():
    """
    Check if current time is after 8:00 AM IST
    Returns: True if after 8 AM IST, False otherwise
    """
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    target_time = time(8, 0)  # 8:00 AM
    
    return now_ist.time() >= target_time


def run_etl_pipeline():
    """
    Run the complete ETL pipeline
    Returns: dict with results
    """
    try:
        # Step 1: Connect to Supabase
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            return {
                'success': False,
                'error': 'Missing Supabase credentials'
            }
        
        supabase = connect_to_supabase(supabase_url, supabase_key)
        if not supabase:
            return {
                'success': False,
                'error': 'Failed to connect to Supabase'
            }
        
        # Step 2: Get companies from database
        companies_dict = get_companies_from_db(supabase)
        if not companies_dict:
            return {
                'success': False,
                'error': 'No companies found in database'
            }
        
        symbols = list(companies_dict.keys())
        
        # Step 3: Extract - Download stock data
        days_to_download = 90
        stock_df = get_stock_data(symbols, days_back=days_to_download)
        oil_df = get_oil_price(days_back=days_to_download)
        
        if stock_df.empty:
            log_etl_run(supabase, 0, 'failed', 'No data downloaded')
            return {
                'success': False,
                'error': 'No stock data downloaded'
            }
        
        # Step 4: Transform - Clean and calculate values
        transformed_df = transform_all(stock_df, oil_df, companies_dict)
        
        if transformed_df.empty:
            log_etl_run(supabase, 0, 'failed', 'Transformation failed')
            return {
                'success': False,
                'error': 'Data transformation failed'
            }
        
        # Step 5: Load - Save to database
        rows_inserted = load_stock_data(supabase, transformed_df)
        
        # Step 6: Log the ETL run
        if rows_inserted > 0:
            status = 'success'
            notes = f"Successfully processed {len(symbols)} companies"
            log_etl_run(supabase, rows_inserted, status, notes)
            
            return {
                'success': True,
                'rows_inserted': rows_inserted,
                'companies': len(symbols),
                'date_range': f"{transformed_df['date'].min()} to {transformed_df['date'].max()}"
            }
        else:
            log_etl_run(supabase, 0, 'failed', 'No data inserted')
            return {
                'success': False,
                'error': 'No data was inserted into database'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@app.route('/api/etl', methods=['GET', 'POST'])
def etl_endpoint():
    """
    Main ETL endpoint - called by Uptime Robot
    
    Logic:
    1. Check if current time is after 8:00 AM IST
    2. If not, return message saying "too early"
    3. If yes, check if ETL already ran today
    4. If already ran, return message saying "already done"
    5. If not ran yet, run the ETL pipeline
    """
    
    try:
        # Get current time in IST
        ist = pytz.timezone('Asia/Kolkata')
        current_time_ist = datetime.now(ist)
        
        # Check 1: Is it after 8:00 AM IST?
        if not check_if_after_8am_ist():
            return jsonify({
                'status': 'skipped',
                'message': 'ETL not scheduled yet - waiting for 8:00 AM IST',
                'current_time_ist': current_time_ist.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'next_run_time': '8:00 AM IST'
            }), 200
        
        # Check 2: Connect to Supabase
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            return jsonify({
                'status': 'error',
                'message': 'Supabase credentials not configured'
            }), 500
        
        supabase = connect_to_supabase(supabase_url, supabase_key)
        
        # Check 3: Did ETL already run today?
        if check_if_etl_ran_today(supabase):
            return jsonify({
                'status': 'skipped',
                'message': 'ETL already completed today',
                'current_time_ist': current_time_ist.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'next_run_time': 'Tomorrow after 8:00 AM IST'
            }), 200
        
        # Check 4: Run the ETL pipeline
        print(f"🚀 Starting ETL pipeline at {current_time_ist.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        result = run_etl_pipeline()
        
        if result['success']:
            return jsonify({
                'status': 'success',
                'message': 'ETL pipeline completed successfully',
                'current_time_ist': current_time_ist.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'details': result
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'ETL pipeline failed',
                'error': result.get('error', 'Unknown error')
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Unexpected error occurred',
            'error': str(e)
        }), 500


# For local testing
if __name__ == '__main__':
    app.run(debug=True, port=5000)