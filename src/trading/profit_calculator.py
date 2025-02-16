from typing import Dict, Optional
from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN

@dataclass
class TradeCharges:
    # Brokerage
    delivery_brokerage: Decimal = Decimal('0')  # Free for delivery
    intraday_brokerage_percent: Decimal = Decimal('0.0003')  # 0.03%
    intraday_brokerage_cap: Decimal = Decimal('20.0')  # Max ₹20 per order
    
    # Taxes and other charges
    gst_rate: Decimal = Decimal('0.18')  # 18% GST
    stt_delivery: Decimal = Decimal('0.001')  # 0.1% STT for delivery
    stt_intraday: Decimal = Decimal('0.00025')  # 0.025% STT for intraday
    exchange_txn_charge: Decimal = Decimal('0.0000325')  # ₹3.25 per crore
    sebi_charges: Decimal = Decimal('0.000001')  # ₹10 per crore
    stamp_duty: Decimal = Decimal('0.00015')  # 0.015% on buy side only
    dp_charges: Decimal = Decimal('15.93')  # ₹15.93 per scrip on sell

    def calculate_brokerage(self, trade_value: Decimal, is_intraday: bool = False) -> Decimal:
        """Calculate brokerage based on trade type"""
        if not is_intraday:
            return self.delivery_brokerage
        
        percentage_brokerage = trade_value * self.intraday_brokerage_percent
        return min(percentage_brokerage, self.intraday_brokerage_cap)

    def calculate_stt(self, trade_value: Decimal, is_intraday: bool = False) -> Decimal:
        """Calculate STT based on trade type"""
        stt_rate = self.stt_intraday if is_intraday else self.stt_delivery
        return trade_value * stt_rate

class ProfitCalculator:
    def __init__(self):
        self.charges = TradeCharges()
    
    def calculate_net_profit(
        self,
        base_price: float,
        selling_price: float,
        quantity: int,
        slippage_estimate: Optional[float] = None,
        is_intraday: bool = False
    ) -> Dict:
        """Calculate net profit considering all charges"""
        base_price = Decimal(str(base_price))
        selling_price = Decimal(str(selling_price))
        quantity = Decimal(str(quantity))
        
        # Use provided slippage or default
        slippage = Decimal(str(slippage_estimate)) if slippage_estimate else Decimal('5.0')
        
        # Calculate gross value
        base_value = base_price * quantity
        selling_value = selling_price * quantity
        gross_profit = selling_value - base_value
        
        # Calculate charges
        charges = self._calculate_charges(base_value, selling_value, is_intraday)
        
        # Add slippage to charges
        charges['slippage'] = slippage
        total_charges = sum(charges.values())
        
        # Calculate net profit
        net_profit = gross_profit - total_charges
        
        return {
            'base_price': float(base_price),
            'selling_price': float(selling_price),
            'quantity': int(quantity),
            'gross_profit': float(gross_profit),
            'charges': {k: float(v) for k, v in charges.items()},
            'total_charges': float(total_charges),
            'net_profit': float(net_profit),
            'is_profitable': net_profit > 0 and selling_price > base_price
        }
    
    def _calculate_charges(self, buy_value: Decimal, sell_value: Decimal, is_intraday: bool = False) -> Dict[str, Decimal]:
        """Calculate all trading charges"""
        # Brokerage
        buy_brokerage = self.charges.calculate_brokerage(buy_value, is_intraday)
        sell_brokerage = self.charges.calculate_brokerage(sell_value, is_intraday)
        total_brokerage = buy_brokerage + sell_brokerage
        
        # STT (only on sell side for intraday)
        stt = self.charges.calculate_stt(sell_value, is_intraday)
        if not is_intraday:
            stt += self.charges.calculate_stt(buy_value, is_intraday)
        
        charges = {
            'brokerage': total_brokerage,
            'stt': stt,
            'exchange_charges': (buy_value + sell_value) * self.charges.exchange_txn_charge,
            'sebi_charges': (buy_value + sell_value) * self.charges.sebi_charges,
            'stamp_duty': buy_value * self.charges.stamp_duty,  # Only on buy side
            'dp_charges': self.charges.dp_charges if not is_intraday else Decimal('0'),
            'gst': total_brokerage * self.charges.gst_rate
        }
        
        # Round all charges to 2 decimal places
        return {k: v.quantize(Decimal('0.01'), rounding=ROUND_DOWN) for k, v in charges.items()}

    def suggest_better_price(
        self,
        base_price: float,
        quantity: int,
        target_profit: float
    ) -> Dict:
        """Suggest better selling price to achieve target profit"""
        base_price = Decimal(str(base_price))
        quantity = Decimal(str(quantity))
        target_profit = Decimal(str(target_profit))
        
        # Start with base price and increment until we find profitable price
        test_price = base_price
        increment = Decimal('0.05')  # 5 paise increment
        
        while True:
            result = self.calculate_net_profit(
                float(base_price),
                float(test_price),
                int(quantity)
            )
            
            if result['net_profit'] >= target_profit:
                break
                
            test_price += increment
        
        return {
            'suggested_price': float(test_price),
            'price_difference': float(test_price - base_price),
            'expected_profit': result['net_profit']
        }

    def calculate_partial_sell_strategy(
        self,
        base_price: float,
        current_price: float,
        total_quantity: int,
        min_profit_per_unit: float
    ) -> Dict:
        """Calculate optimal partial sell strategy"""
        base_price = Decimal(str(base_price))
        current_price = Decimal(str(current_price))
        total_quantity = Decimal(str(total_quantity))
        min_profit_per_unit = Decimal(str(min_profit_per_unit))
        
        # Try different quantities to find optimal partial sell
        best_quantity = Decimal('0')
        best_profit = Decimal('0')
        
        for q in range(1, int(total_quantity) + 1):
            result = self.calculate_net_profit(
                float(base_price),
                float(current_price),
                q
            )
            
            profit_per_unit = Decimal(str(result['net_profit'])) / Decimal(str(q))
            
            if profit_per_unit >= min_profit_per_unit and result['net_profit'] > best_profit:
                best_quantity = Decimal(str(q))
                best_profit = Decimal(str(result['net_profit']))
        
        if best_quantity > 0:
            return {
                'should_partial_sell': True,
                'suggested_quantity': int(best_quantity),
                'remaining_quantity': int(total_quantity - best_quantity),
                'expected_profit': float(best_profit),
                'profit_per_unit': float(best_profit / best_quantity)
            }
        
        return {
            'should_partial_sell': False,
            'reason': 'No profitable partial sell quantity found'
        }
