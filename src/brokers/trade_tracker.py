from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from abc import ABC, abstractmethod

class BrokerAPI(ABC):
    """Abstract base class for broker APIs"""
    
    @abstractmethod
    def get_trades(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get trades for the given date range"""
        pass
    
    @abstractmethod
    def get_charges(self, trade_id: str) -> Dict:
        """Get charges for a specific trade"""
        pass

class ZerodhaAPI(BrokerAPI):
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        # Initialize Zerodha API client here
        
    def get_trades(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        # Implement Zerodha-specific trade fetching
        pass
        
    def get_charges(self, trade_id: str) -> Dict:
        # Implement Zerodha-specific charges fetching
        pass

class UpstoxAPI(BrokerAPI):
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        # Initialize Upstox API client here
        
    def get_trades(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        # Implement Upstox-specific trade fetching
        pass
        
    def get_charges(self, trade_id: str) -> Dict:
        # Implement Upstox-specific charges fetching
        pass

class TradeTracker:
    def __init__(self, broker_api: BrokerAPI):
        """
        Initialize TradeTracker with a broker API
        
        Args:
            broker_api: Instance of a broker API (Zerodha, Upstox, etc.)
        """
        self.broker_api = broker_api
        self.trades_df = pd.DataFrame()
        self.charges_df = pd.DataFrame()
        
    def fetch_trades(self, days: int = 30) -> None:
        """
        Fetch trades for the last N days
        
        Args:
            days: Number of days to fetch trades for (default: 30)
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        trades = self.broker_api.get_trades(start_date, end_date)
        self.trades_df = pd.DataFrame(trades)
        
        # Fetch charges for each trade
        charges = []
        for trade_id in self.trades_df['trade_id']:
            charge = self.broker_api.get_charges(trade_id)
            charges.append(charge)
        
        self.charges_df = pd.DataFrame(charges)
    
    def get_trade_summary(self) -> Dict:
        """
        Get summary of trades and charges
        
        Returns:
            Dictionary containing:
            - total_invested: Total investment amount
            - total_return: Total return amount
            - charges: Breakdown of all charges
            - net_profit: Profit after all charges
        """
        if self.trades_df.empty:
            return {
                'total_invested': 0,
                'total_return': 0,
                'charges': {
                    'brokerage': 0,
                    'stt': 0,
                    'transaction_charges': 0,
                    'gst': 0,
                    'sebi_charges': 0,
                    'stamp_duty': 0,
                    'total': 0
                },
                'net_profit': 0
            }
        
        # Calculate investment and returns
        total_invested = self.trades_df[self.trades_df['type'] == 'BUY']['value'].sum()
        total_return = self.trades_df[self.trades_df['type'] == 'SELL']['value'].sum()
        
        # Sum up all charges
        charges = {
            'brokerage': self.charges_df['brokerage'].sum(),
            'stt': self.charges_df['stt'].sum(),
            'transaction_charges': self.charges_df['transaction_charges'].sum(),
            'gst': self.charges_df['gst'].sum(),
            'sebi_charges': self.charges_df['sebi_charges'].sum(),
            'stamp_duty': self.charges_df['stamp_duty'].sum()
        }
        
        # Calculate total charges
        total_charges = sum(charges.values())
        charges['total'] = total_charges
        
        # Calculate net profit
        net_profit = total_return - total_invested - total_charges
        
        return {
            'total_invested': total_invested,
            'total_return': total_return,
            'charges': charges,
            'net_profit': net_profit
        }
    
    def get_charge_history(self, days: Optional[int] = None) -> pd.DataFrame:
        """
        Get historical charge data
        
        Args:
            days: Optional, number of days to get history for
                 If None, returns all available data
                 
        Returns:
            DataFrame with daily charge breakdown
        """
        if days:
            start_date = datetime.now() - timedelta(days=days)
            charges_df = self.charges_df[self.charges_df['date'] >= start_date]
        else:
            charges_df = self.charges_df
            
        return charges_df.groupby('date').sum()
    
    def export_to_excel(self, filename: str) -> None:
        """
        Export trade and charge data to Excel
        
        Args:
            filename: Name of the Excel file to create
        """
        with pd.ExcelWriter(filename) as writer:
            self.trades_df.to_excel(writer, sheet_name='Trades')
            self.charges_df.to_excel(writer, sheet_name='Charges')
            
            # Create summary sheet
            summary = pd.DataFrame([self.get_trade_summary()])
            summary.to_excel(writer, sheet_name='Summary')
