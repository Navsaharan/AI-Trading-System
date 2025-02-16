import yfinance as yf
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import os
import schedule
import time
from concurrent.futures import ThreadPoolExecutor
import logging
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoDataCollector:
    def __init__(self):
        self.base_path = 'training_data'
        self.ensure_directories()
        
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            'training_data/stocks',
            'training_data/indices',
            'training_data/processed',
            'training_data/news'
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def get_nse_symbols(self):
        """Get list of all NSE symbols"""
        try:
            # Get Nifty 500 symbols as they are most liquid
            url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
            df = pd.read_csv(url)
            return df['Symbol'].tolist()
        except:
            # Fallback to most common stocks if NSE website is not accessible
            return [
                'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
                'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK',
                'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'WIPRO'
            ]

    def download_historical_data(self, symbol, start_date='2010-01-01'):
        """Download historical data for a single symbol"""
        try:
            # Add .NS suffix for NSE stocks
            ticker = f"{symbol}.NS"
            df = yf.download(ticker, start=start_date, progress=False)
            
            if not df.empty:
                # Add technical indicators
                df['SMA_20'] = df['Close'].rolling(window=20).mean()
                df['SMA_50'] = df['Close'].rolling(window=50).mean()
                df['RSI'] = self.calculate_rsi(df['Close'])
                df['MACD'] = self.calculate_macd(df['Close'])
                
                # Save data
                output_path = f'{self.base_path}/stocks/{symbol}_historical.csv'
                df.to_csv(output_path)
                logger.info(f"Downloaded historical data for {symbol}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error downloading {symbol}: {str(e)}")
            return False

    def download_bulk_historical_data(self):
        """Download historical data for all symbols in parallel"""
        symbols = self.get_nse_symbols()
        logger.info(f"Starting bulk download for {len(symbols)} symbols")
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(self.download_historical_data, symbols))
        
        success_count = sum(results)
        logger.info(f"Successfully downloaded {success_count} out of {len(symbols)} symbols")

    def update_daily_data(self):
        """Update data for all symbols with today's data"""
        symbols = self.get_nse_symbols()
        today = datetime.now().strftime('%Y-%m-%d')
        
        for symbol in symbols:
            try:
                file_path = f'{self.base_path}/stocks/{symbol}_historical.csv'
                if os.path.exists(file_path):
                    # Load existing data
                    df = pd.read_csv(file_path, index_col=0)
                    df.index = pd.to_datetime(df.index)
                    
                    # Get latest data
                    latest_data = yf.download(f"{symbol}.NS", start=today, end=None, progress=False)
                    
                    if not latest_data.empty:
                        # Append new data
                        df = pd.concat([df, latest_data])
                        df = df[~df.index.duplicated(keep='last')]
                        df.to_csv(file_path)
                        logger.info(f"Updated daily data for {symbol}")
            except Exception as e:
                logger.error(f"Error updating {symbol}: {str(e)}")

    @staticmethod
    def calculate_rsi(prices, period=14):
        """Calculate RSI technical indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_macd(prices, fast=12, slow=26, signal=9):
        """Calculate MACD technical indicator"""
        exp1 = prices.ewm(span=fast, adjust=False).mean()
        exp2 = prices.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        return macd - signal_line

    def schedule_updates(self):
        """Schedule automatic updates"""
        # Update data at market close (3:30 PM IST)
        schedule.every().monday.at("15:30").do(self.update_daily_data)
        schedule.every().tuesday.at("15:30").do(self.update_daily_data)
        schedule.every().wednesday.at("15:30").do(self.update_daily_data)
        schedule.every().thursday.at("15:30").do(self.update_daily_data)
        schedule.every().friday.at("15:30").do(self.update_daily_data)
        
        # Run the scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    collector = AutoDataCollector()
    
    # First time: Download all historical data
    if not os.path.exists('training_data/stocks'):
        logger.info("First time setup: Downloading historical data...")
        collector.download_bulk_historical_data()
    
    # Start automatic updates
    logger.info("Starting automatic updates...")
    collector.schedule_updates()

if __name__ == "__main__":
    main()
