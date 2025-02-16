# Automatic Data Collection Guide

## Overview

This system automatically:
1. Downloads historical data (2010-present) for all Nifty 500 stocks
2. Updates data daily after market close (3:30 PM IST)
3. Calculates technical indicators automatically
4. Handles errors and retries

## Quick Start

1. **Install Dependencies:**
```bash
pip install yfinance pandas requests schedule
```

2. **Run the Collector:**
```bash
python auto_data_collector.py
```

That's it! The script will:
- First time: Download all historical data since 2010
- Subsequently: Update daily at market close
- Create all necessary folders automatically
- Handle all error cases

## What Data is Collected?

1. **Price Data:**
   - Open, High, Low, Close
   - Volume
   - Adjusted Close

2. **Technical Indicators:**
   - SMA (20 and 50 days)
   - RSI (14 days)
   - MACD

3. **Coverage:**
   - All Nifty 500 stocks
   - Major indices
   - 13+ years of historical data

## Where is Data Stored?

```
training_data/
├── stocks/                 # Individual stock data
│   ├── RELIANCE_historical.csv
│   ├── TCS_historical.csv
│   └── ...
├── indices/               # Index data
├── processed/            # Processed data for AI
└── news/                 # News data
```

## Automatic Updates

The system automatically:
1. Runs every trading day at 3:30 PM IST
2. Updates all stock data
3. Recalculates indicators
4. Handles market holidays

## Data Requirements

1. **Historical Training:**
   - Minimum: 2 years
   - Recommended: 5+ years
   - Provided: 13+ years (since 2010)

2. **Storage Space:**
   - ~100MB for 500 stocks
   - ~1GB with all indicators
   - ~2GB with news data

## Running as a Service

1. **Using systemd (Linux):**
```bash
sudo nano /etc/systemd/system/data-collector.service

[Unit]
Description=Stock Data Collector
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/auto_data_collector.py
WorkingDirectory=/path/to/project
User=your-user
Restart=always

[Install]
WantedBy=multi-user.target
```

2. **Using Task Scheduler (Windows):**
   - Open Task Scheduler
   - Create Basic Task
   - Action: Start Program
   - Program: python
   - Arguments: auto_data_collector.py
   - Run at system startup

## Troubleshooting

1. **No Data Downloaded:**
   - Check internet connection
   - Verify NSE website access
   - Check disk space

2. **Missing Updates:**
   - Check if it was a market holiday
   - Verify system was running at 3:30 PM
   - Check error logs

3. **Incomplete Data:**
   - Run manual update:
   ```bash
   python auto_data_collector.py --force-update
   ```

## Monitoring

Check the logs at:
```
training_data/logs/collector.log
```

Contains:
- Download status
- Update times
- Error messages
- Data quality checks
