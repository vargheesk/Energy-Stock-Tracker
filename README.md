# 📈 Energy Stock Tracker

> **Automated ETL Pipeline for Energy Sector Stock Analysis**  
> Track daily stock prices of major energy companies with real-time data extraction, transformation, and interactive visualization.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg)](https://streamlit.io/)
[![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E.svg)](https://supabase.com/)
[![Vercel](https://img.shields.io/badge/Vercel-Deployed-000000.svg)](https://vercel.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Features

- **📊 Automated Data Collection**: Daily extraction of stock data from Yahoo Finance
- **🔄 ETL Pipeline**: Complete Extract, Transform, Load workflow with error handling
- **📈 Technical Indicators**: Moving averages (7-day & 30-day), volatility, percent change
- **🎯 Smart Scheduling**: Automated daily runs after 8:00 AM IST with duplicate prevention
- **📱 Interactive Dashboard**: Real-time visualization with Streamlit
- **🛢️ Oil Price Tracking**: Monitors WTI Crude Oil prices alongside energy stocks
- **🏢 Multi-Sector Coverage**: Tracks both traditional Oil & Gas and Renewable Energy companies

---

## 🚀 Live Demo

- **📊 Dashboard**: [View Live Dashboard](#) *(Streamlit link coming soon)*
- **🔗 API Endpoint**: `https://your-project.vercel.app/etl`
- **📂 GitHub Repository**: [Energy-Stock-Tracker](https://github.com/vargheesk/Energy-Stock-Tracker.git)

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Uptime Robot   │  ← Triggers ETL every 15 minutes
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vercel API     │  ← Checks time & runs ETL once per day
│  (etl.py)       │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│ Yahoo  │ │ Supabase │  ← Stores transformed data
│Finance │ │ Database │
└────────┘ └────┬─────┘
                │
                ▼
         ┌──────────────┐
         │  Streamlit   │  ← Interactive Dashboard
         │  Dashboard   │
         └──────────────┘
```

---

## 📦 Tech Stack

| Technology | Purpose |
|-----------|---------|
| **Python 3.9+** | Core programming language |
| **yFinance** | Stock data extraction from Yahoo Finance |
| **Pandas** | Data manipulation and transformation |
| **Supabase** | PostgreSQL database (cloud-hosted) |
| **Streamlit** | Interactive web dashboard |
| **Plotly** | Interactive charts and visualizations |
| **Flask** | API framework for Vercel serverless function |
| **Vercel** | Serverless deployment for ETL endpoint |
| **Uptime Robot** | Scheduled job trigger (cron alternative) |

---

## 🗂️ Project Structure

```
Energy-Stock-Tracker/
│
├── etl/                          # ETL Package
│   ├── __init__.py              # Package initialization
│   ├── extract.py               # Data extraction from Yahoo Finance
│   ├── transform.py             # Data transformation & calculations
│   └── load.py                  # Data loading to Supabase
│
├── Streamlit_Dashboard/          # Dashboard Application
│   ├── streamlit_app.py         # Main dashboard code
│   └── secrets.toml             # Streamlit secrets (gitignored)
│
├── sql/                         # Database Schema
│   └── schema.sql               # Table definitions & initial data
│
├── etl.py                       # Vercel serverless function
├── vercel.json                  # Vercel deployment config
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (gitignored)
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

---

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.9 or higher
- Supabase account ([sign up here](https://supabase.com/))
- Vercel account ([sign up here](https://vercel.com/))
- Uptime Robot account ([sign up here](https://uptimerobot.com/))

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/vargheesk/Energy-Stock-Tracker.git
cd Energy-Stock-Tracker
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Set Up Supabase Database

1. Create a new Supabase project
2. Go to **SQL Editor** in your Supabase dashboard
3. Copy the contents of `sql/schema.sql`
4. Paste and run the SQL script
5. Verify tables are created:
   - `companies` (10 energy companies pre-loaded)
   - `stock_data` (stores daily stock data)
   - `etl_log` (tracks ETL runs)

### 4️⃣ Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Supabase Credentials
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

> **💡 Where to find these:**
> - Supabase Dashboard → Settings → API
> - Copy the `Project URL` and `anon/public` key

### 5️⃣ Test ETL Pipeline Locally

```bash
python etl.py
```

You should see:
```
🔌 Connecting to Supabase...
   ✅ Connected to Supabase

📋 Getting companies from database...
   ✅ Got 10 companies

🔥 Downloading stock data from 2024-XX-XX to 2024-XX-XX
   Getting data for XOM...
   ✅ Got 90 days of data for XOM
   ...

✅ Total records downloaded: 900

🧹 Cleaning data...
📈 Calculating percent changes...
📊 Calculating moving averages...
...

💾 Saving stock data to database...
   ✅ Batch 1/9: saved 100 records
   ...

✅ ETL pipeline completed successfully
```

---

## ☁️ Deployment

### Deploy API to Vercel

1. **Install Vercel CLI**:
```bash
npm i -g vercel
```

2. **Login to Vercel**:
```bash
vercel login
```

3. **Deploy**:
```bash
vercel --prod
```

4. **Add Environment Variables**:
   - Go to your Vercel project → Settings → Environment Variables
   - Add:
     - `SUPABASE_URL` = your Supabase URL
     - `SUPABASE_KEY` = your Supabase key

5. **Your API endpoint will be**:
```
https://your-project.vercel.app/etl
```

### Deploy Dashboard to Streamlit Cloud

1. **Push code to GitHub**:
```bash
git add .
git commit -m "Deploy to Streamlit"
git push origin main
```

2. **Go to [Streamlit Cloud](https://streamlit.io/cloud)**

3. **Create New App**:
   - Repository: `vargheesk/Energy-Stock-Tracker`
   - Branch: `main`
   - Main file path: `Streamlit_Dashboard/streamlit_app.py`

4. **Add Secrets** (in Streamlit Cloud dashboard):
```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-supabase-anon-key"
```

5. **Deploy!** Your dashboard will be live at:
```
https://your-app.streamlit.app
```

### Set Up Automated Scheduling with Uptime Robot

1. **Go to [Uptime Robot](https://uptimerobot.com/)**

2. **Create New Monitor**:
   - Monitor Type: `HTTP(s)`
   - Friendly Name: `Energy Stock ETL`
   - URL: `https://your-project.vercel.app/etl`
   - Monitoring Interval: `15 minutes`

3. **How it works**:
   - Uptime Robot pings your API every 15 minutes
   - API checks if it's after 8:00 AM IST
   - API checks if ETL already ran today
   - If both conditions pass, ETL runs once
   - Otherwise, returns a "skipped" message

---

## 📊 Dashboard Features

### 1. 🔢 Key Metrics
- Total records in database
- Average daily price change
- Number of gainers today
- Average market volatility

### 2. 📈 Interactive Charts
- **Price Trends**: Line chart showing daily closing prices for all selected stocks
- **Moving Averages**: 7-day and 30-day moving averages comparison
- **Top Performers**: Top 5 gainers and losers of the day
- **Sector Comparison**: Average price trends by sector (Oil & Gas vs Renewable Energy)
- **Volatility Heatmap**: Bar chart showing stock volatility rankings

### 3. 🎛️ Filters
- Date range selector
- Company multi-select
- Sector multi-select

### 4. 📋 Data Table
- Sortable and filterable table
- Color-coded trend indicators (green = up, red = down)
- Export to CSV functionality

---

## 🏢 Tracked Companies

### Oil & Gas Sector
| Symbol | Company Name |
|--------|--------------|
| XOM | Exxon Mobil Corporation |
| BP | BP plc |
| CVX | Chevron Corporation |
| SHEL | Shell plc |
| TTE | TotalEnergies SE |
| COP | ConocoPhillips |

### Renewable Energy Sector
| Symbol | Company Name |
|--------|--------------|
| TSLA | Tesla Inc |
| ENPH | Enphase Energy Inc |
| NEE | NextEra Energy Inc |
| FSLR | First Solar Inc |

---

## 📝 API Documentation

### `GET/POST /etl`

Triggers the ETL pipeline if conditions are met.

**Response Cases:**

1. **Before 8:00 AM IST**:
```json
{
  "status": "skipped",
  "message": "ETL not scheduled yet - waiting for 8:00 AM IST",
  "current_time_ist": "2024-10-27 07:30:00 IST",
  "next_run_time": "8:00 AM IST"
}
```

2. **Already Ran Today**:
```json
{
  "status": "skipped",
  "message": "ETL already completed today",
  "current_time_ist": "2024-10-27 09:00:00 IST",
  "next_run_time": "Tomorrow after 8:00 AM IST"
}
```

3. **Success**:
```json
{
  "status": "success",
  "message": "ETL pipeline completed successfully",
  "current_time_ist": "2024-10-27 08:15:00 IST",
  "details": {
    "rows_inserted": 900,
    "companies": 10,
    "date_range": "2024-07-28 to 2024-10-27"
  }
}
```

4. **Error**:
```json
{
  "status": "error",
  "message": "ETL pipeline failed",
  "error": "Connection timeout"
}
```

---

## 🧪 Testing

### Test Extract Module
```bash
python etl/extract.py
```

### Test Transform Module
```bash
python etl/transform.py
```

### Test Load Module
```bash
python etl/load.py
```

### Test Full ETL Pipeline
```bash
python etl.py
```

### Run Dashboard Locally
```bash
cd Streamlit_Dashboard
streamlit run streamlit_app.py
```

---

## 🔧 Configuration

### Add More Companies

1. Open Supabase SQL Editor
2. Run:
```sql
INSERT INTO companies (symbol, name, sector) VALUES
('AAPL', 'Apple Inc', 'Technology'),
('GOOGL', 'Alphabet Inc', 'Technology');
```

### Change Data History Range

In `etl.py`, modify:
```python
days_to_download = 90  # Change this number
```

### Modify Scheduling

**Option 1: Change Time Check** (in `etl.py`):
```python
target_time = time(8, 0)  # Change to your preferred time
```

**Option 2: Change Uptime Robot Interval**:
- Min interval: 5 minutes (paid plan)
- Max interval: 24 hours

---

## 📊 Database Schema

### `companies` Table
```sql
company_id    SERIAL PRIMARY KEY
symbol        VARCHAR(10)
name          VARCHAR(100)
sector        VARCHAR(50)
created_at    TIMESTAMP
```

### `stock_data` Table
```sql
id            SERIAL PRIMARY KEY
date          DATE
symbol        VARCHAR(10)
company_name  VARCHAR(100)
sector        VARCHAR(50)
open_price    FLOAT
high_price    FLOAT
low_price     FLOAT
close_price   FLOAT
volume        BIGINT
pct_change    FLOAT           -- Daily % change
ma_7          FLOAT           -- 7-day moving average
ma_30         FLOAT           -- 30-day moving average
volatility    FLOAT           -- 30-day standard deviation
trend         VARCHAR(10)     -- 'up', 'down', or 'flat'
oil_price     FLOAT           -- WTI Crude Oil price
created_at    TIMESTAMP
```

### `etl_log` Table
```sql
id              SERIAL PRIMARY KEY
run_time        TIMESTAMP
rows_inserted   INT
status          VARCHAR(20)    -- 'success' or 'failed'
notes           TEXT
```

---

## 🐛 Troubleshooting

### Issue: "No data downloaded"
**Solution**: Check if stock symbols are valid on Yahoo Finance
```bash
# Test a symbol directly
python -c "import yfinance as yf; print(yf.Ticker('XOM').history(period='5d'))"
```

### Issue: "Supabase connection failed"
**Solution**: Verify credentials
```bash
# Check if .env file exists
cat .env

# Test connection
python -c "from supabase import create_client; import os; from dotenv import load_dotenv; load_dotenv(); client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY')); print('Connected!')"
```

### Issue: "Vercel deployment timeout"
**Solution**: The default timeout is 10s for free tier. Our `vercel.json` sets `maxDuration: 300` (5 minutes) which requires Vercel Pro plan.

**Workaround**: Reduce `days_back` in extract functions to speed up execution.

### Issue: "Streamlit secrets not found"
**Solution**: 
- **Local testing**: Create `Streamlit_Dashboard/.streamlit/secrets.toml`
- **Cloud deployment**: Add secrets in Streamlit Cloud dashboard

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
```bash
git checkout -b feature/amazing-feature
```
3. **Commit your changes**
```bash
git commit -m "Add some amazing feature"
```
4. **Push to the branch**
```bash
git push origin feature/amazing-feature
```
5. **Open a Pull Request**

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Varghese K**

- GitHub: [@vargheesk](https://github.com/vargheesk)
- Project Link: [Energy-Stock-Tracker](https://github.com/vargheesk/Energy-Stock-Tracker.git)

---

## 🙏 Acknowledgments

- [yFinance](https://github.com/ranaroussi/yfinance) for stock data API
- [Supabase](https://supabase.com/) for the amazing database platform
- [Streamlit](https://streamlit.io/) for the dashboard framework
- [Vercel](https://vercel.com/) for serverless deployment
- [Uptime Robot](https://uptimerobot.com/) for scheduling automation

---

## 📈 Roadmap

- [ ] Add more technical indicators (RSI, MACD, Bollinger Bands)
- [ ] Email alerts for significant price movements
- [ ] Sentiment analysis from news articles
- [ ] Machine learning price predictions
- [ ] Mobile app version
- [ ] Real-time streaming data (WebSocket)

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=vargheesk/Energy-Stock-Tracker&type=Date)](https://star-history.com/#vargheesk/Energy-Stock-Tracker&Date)

---

<div align="center">

**Made with ❤️ and Python**

[Report Bug](https://github.com/vargheesk/Energy-Stock-Tracker/issues) · [Request Feature](https://github.com/vargheesk/Energy-Stock-Tracker/issues)

</div>