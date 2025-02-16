from dataclasses import dataclass
from typing import Dict, Optional
import json
import os

@dataclass
class ChargeRates:
    # Basic charges
    brokerage_delivery: float  # Percentage for delivery trades
    brokerage_intraday: float  # Percentage for intraday trades
    brokerage_futures: float  # Percentage for futures trades
    brokerage_options: float  # Percentage for options trades
    
    # Government and Exchange Charges
    stt_delivery: float  # Securities Transaction Tax for delivery
    stt_intraday: float  # STT for intraday
    stt_futures: float  # STT for futures
    stt_options: float  # STT for options
    
    exchange_transaction_charge: float  # Exchange transaction charge
    sebi_charge: float  # SEBI turnover charge
    
    # Tax Rates
    gst_rate: float  # GST percentage
    stamp_duty_rate: float  # Stamp duty percentage
    
    # Minimum charges
    min_brokerage: float  # Minimum brokerage per trade
    
    @classmethod
    def default(cls):
        return cls(
            # Brokerage (varies by broker)
            brokerage_delivery=0.0,  # Many brokers offer 0 for delivery
            brokerage_intraday=0.03,  # 0.03% or ₹20 per executed order
            brokerage_futures=0.03,  # 0.03% or ₹20 per executed order
            brokerage_options=0.03,  # 0.03% or ₹20 per executed order
            
            # STT (Securities Transaction Tax)
            stt_delivery=0.1,  # 0.1% on buy and sell
            stt_intraday=0.025,  # 0.025% on sell side
            stt_futures=0.01,  # 0.01% on sell side
            stt_options=0.05,  # 0.05% on sell side of options
            
            # Exchange and Regulatory
            exchange_transaction_charge=0.00345,  # 0.00345%
            sebi_charge=0.0001,  # ₹1 per lakh
            
            # Taxes
            gst_rate=18.0,  # 18% on brokerage and transaction charges
            stamp_duty_rate=0.015,  # 0.015% on buy side only
            
            # Minimum
            min_brokerage=20.0  # ₹20 minimum per executed order
        )

class ChargeManager:
    def __init__(self, config_path: str = "config/charges.json"):
        self.config_path = config_path
        self.charges = self.load_charges()
    
    def load_charges(self) -> ChargeRates:
        """Load charge rates from config file or create with defaults"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                return ChargeRates(**data)
        return ChargeRates.default()
    
    def save_charges(self) -> None:
        """Save current charge rates to config file"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.charges.__dict__, f, indent=4)
    
    def calculate_charges(self, 
                         trade_type: str,
                         trade_value: float,
                         is_buy: bool = True) -> Dict[str, float]:
        """
        Calculate all charges for a trade
        
        Args:
            trade_type: 'delivery', 'intraday', 'futures', or 'options'
            trade_value: Total value of the trade
            is_buy: Whether this is a buy trade
            
        Returns:
            Dictionary with breakdown of all charges
        """
        charges = {}
        
        # 1. Brokerage
        brokerage_rate = getattr(self.charges, f'brokerage_{trade_type}')
        brokerage = max(trade_value * brokerage_rate / 100, self.charges.min_brokerage)
        charges['brokerage'] = brokerage
        
        # 2. Securities Transaction Tax (STT)
        stt_rate = getattr(self.charges, f'stt_{trade_type}')
        # STT applies to both sides for delivery, only sell side for others
        if trade_type == 'delivery' or not is_buy:
            charges['stt'] = trade_value * stt_rate / 100
        else:
            charges['stt'] = 0
        
        # 3. Exchange Transaction Charge
        charges['exchange_charge'] = trade_value * self.charges.exchange_transaction_charge / 100
        
        # 4. SEBI Charges
        charges['sebi_charge'] = trade_value * self.charges.sebi_charge / 100
        
        # 5. Stamp Duty (only on buy side)
        if is_buy:
            charges['stamp_duty'] = trade_value * self.charges.stamp_duty_rate / 100
        else:
            charges['stamp_duty'] = 0
        
        # 6. GST (on brokerage and exchange transaction charge)
        taxable_amount = charges['brokerage'] + charges['exchange_charge']
        charges['gst'] = taxable_amount * self.charges.gst_rate / 100
        
        # 7. Total Charges
        charges['total'] = sum(charges.values())
        
        return charges
    
    def update_charge_rate(self, charge_type: str, new_rate: float) -> None:
        """Update a specific charge rate"""
        if hasattr(self.charges, charge_type):
            setattr(self.charges, charge_type, new_rate)
            self.save_charges()
        else:
            raise ValueError(f"Invalid charge type: {charge_type}")
    
    def get_minimum_profitable_trade(self, trade_type: str) -> float:
        """
        Calculate the minimum trade value needed to be profitable after charges
        
        Args:
            trade_type: 'delivery', 'intraday', 'futures', or 'options'
            
        Returns:
            Minimum trade value needed
        """
        # Start with a sample trade value
        trade_value = 10000
        
        # Calculate charges for buy and sell
        buy_charges = self.calculate_charges(trade_type, trade_value, is_buy=True)
        sell_charges = self.calculate_charges(trade_type, trade_value, is_buy=False)
        
        total_charges = buy_charges['total'] + sell_charges['total']
        charge_percentage = (total_charges / trade_value) * 100
        
        # Return the minimum value needed to overcome charges with 0.5% profit
        return (total_charges / 0.005)  # 0.5% minimum profit
    
    def get_charge_summary(self) -> Dict[str, Dict[str, float]]:
        """Get a summary of charges for all trade types"""
        trade_types = ['delivery', 'intraday', 'futures', 'options']
        summary = {}
        
        for trade_type in trade_types:
            trade_value = 100000  # Sample value of ₹1 lakh
            buy_charges = self.calculate_charges(trade_type, trade_value, is_buy=True)
            sell_charges = self.calculate_charges(trade_type, trade_value, is_buy=False)
            
            total_charges = buy_charges['total'] + sell_charges['total']
            charge_percentage = (total_charges / trade_value) * 100
            
            summary[trade_type] = {
                'sample_trade_value': trade_value,
                'total_charges': total_charges,
                'charge_percentage': charge_percentage,
                'min_profitable_trade': self.get_minimum_profitable_trade(trade_type)
            }
        
        return summary
