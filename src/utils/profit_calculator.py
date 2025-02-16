from dataclasses import dataclass
from typing import Dict, List

@dataclass
class TradeCharges:
    brokerage: float
    stt: float  # Securities Transaction Tax
    transaction_charges: float
    gst: float  # Goods and Services Tax
    sebi_charges: float
    stamp_duty: float

class ProfitCalculator:
    def __init__(self):
        # Standard charges in percentage
        self.charges = {
            'equity_delivery': {
                'brokerage': 0,  # Many brokers offer 0 brokerage for delivery
                'stt': 0.1,  # 0.1% on buy and sell
                'transaction_charges': 0.00345,  # NSE: 0.00345%
                'gst': 18,  # 18% on (brokerage + transaction charges)
                'sebi_charges': 0.0001,  # 0.0001% (Re.1 per lakh)
                'stamp_duty': 0.015  # 0.015% on buy side only
            },
            'equity_intraday': {
                'brokerage': 0.03,  # 0.03% or Rs.20 per executed order
                'stt': 0.025,  # 0.025% on sell side only
                'transaction_charges': 0.00345,
                'gst': 18,
                'sebi_charges': 0.0001,
                'stamp_duty': 0.003  # 0.003% on buy side only
            },
            'futures': {
                'brokerage': 0.03,
                'stt': 0.01,  # 0.01% on sell side only
                'transaction_charges': 0.002,
                'gst': 18,
                'sebi_charges': 0.0001,
                'stamp_duty': 0.002  # 0.002% on buy side only
            },
            'options': {
                'brokerage': 0.03,
                'stt': 0.05,  # 0.05% on sell side of options
                'transaction_charges': 0.053,
                'gst': 18,
                'sebi_charges': 0.0001,
                'stamp_duty': 0.003  # 0.003% on buy side only
            }
        }

    def calculate_charges(self, trade_type: str, buy_value: float, sell_value: float) -> TradeCharges:
        """
        Calculate all charges for a trade
        
        Args:
            trade_type: Type of trade ('equity_delivery', 'equity_intraday', 'futures', 'options')
            buy_value: Total buy value of the trade
            sell_value: Total sell value of the trade
            
        Returns:
            TradeCharges object containing all charges
        """
        charge_rates = self.charges[trade_type]
        
        # Calculate brokerage
        brokerage = min(
            max(buy_value * charge_rates['brokerage'] / 100, 20),  # Min Rs.20 per order
            max(sell_value * charge_rates['brokerage'] / 100, 20)
        ) if charge_rates['brokerage'] > 0 else 0
        
        # Calculate STT
        stt = 0
        if trade_type == 'equity_delivery':
            stt = (buy_value + sell_value) * charge_rates['stt'] / 100
        else:
            stt = sell_value * charge_rates['stt'] / 100
        
        # Calculate transaction charges
        transaction_charges = (buy_value + sell_value) * charge_rates['transaction_charges'] / 100
        
        # Calculate GST
        gst = (brokerage + transaction_charges) * charge_rates['gst'] / 100
        
        # Calculate SEBI charges
        sebi_charges = (buy_value + sell_value) * charge_rates['sebi_charges'] / 100
        
        # Calculate stamp duty (only on buy side)
        stamp_duty = buy_value * charge_rates['stamp_duty'] / 100
        
        return TradeCharges(
            brokerage=brokerage,
            stt=stt,
            transaction_charges=transaction_charges,
            gst=gst,
            sebi_charges=sebi_charges,
            stamp_duty=stamp_duty
        )

    def calculate_net_profit(self, trades: List[Dict]) -> Dict[str, float]:
        """
        Calculate net profit after all charges
        
        Args:
            trades: List of trade dictionaries containing:
                   - trade_type: Type of trade
                   - buy_value: Buy value
                   - sell_value: Sell value
                   
        Returns:
            Dictionary containing:
            - gross_profit: Profit before charges
            - total_charges: Sum of all charges
            - net_profit: Profit after charges
            - charges_breakdown: Detailed breakdown of all charges
        """
        total_charges = TradeCharges(0, 0, 0, 0, 0, 0)
        total_buy_value = 0
        total_sell_value = 0
        
        # Calculate charges for each trade
        for trade in trades:
            trade_charges = self.calculate_charges(
                trade['trade_type'],
                trade['buy_value'],
                trade['sell_value']
            )
            
            # Accumulate charges
            total_charges.brokerage += trade_charges.brokerage
            total_charges.stt += trade_charges.stt
            total_charges.transaction_charges += trade_charges.transaction_charges
            total_charges.gst += trade_charges.gst
            total_charges.sebi_charges += trade_charges.sebi_charges
            total_charges.stamp_duty += trade_charges.stamp_duty
            
            total_buy_value += trade['buy_value']
            total_sell_value += trade['sell_value']
        
        gross_profit = total_sell_value - total_buy_value
        total_charges_value = (
            total_charges.brokerage +
            total_charges.stt +
            total_charges.transaction_charges +
            total_charges.gst +
            total_charges.sebi_charges +
            total_charges.stamp_duty
        )
        
        return {
            'gross_profit': gross_profit,
            'total_charges': total_charges_value,
            'net_profit': gross_profit - total_charges_value,
            'charges_breakdown': {
                'brokerage': total_charges.brokerage,
                'stt': total_charges.stt,
                'transaction_charges': total_charges.transaction_charges,
                'gst': total_charges.gst,
                'sebi_charges': total_charges.sebi_charges,
                'stamp_duty': total_charges.stamp_duty
            }
        }
