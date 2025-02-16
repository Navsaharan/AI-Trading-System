from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum
import json
import os

class TradingMode(Enum):
    NORMAL = "normal"
    HFT = "hft"
    PAPER = "paper"

class TradingRiskLevel(Enum):
    SAFE = "safe"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"

@dataclass
class TradingAllocation:
    mode: TradingMode
    amount: float
    risk_level: TradingRiskLevel
    enabled: bool
    max_trades_per_day: int
    stop_loss_percentage: float
    take_profit_percentage: float

class TradingAllocationService:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.allocations = self._load_allocations()
        self.paper_trading = PaperTradingManager()

    def _load_allocations(self) -> Dict[str, TradingAllocation]:
        """Load user's trading allocations"""
        try:
            # Load from database/file
            config_path = self._get_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    data = json.load(f)
                return self._parse_allocations(data)
            return self._get_default_allocations()
        except Exception as e:
            print(f"Error loading allocations: {e}")
            return self._get_default_allocations()

    def _get_default_allocations(self) -> Dict[str, TradingAllocation]:
        """Get default trading allocations"""
        return {
            TradingMode.NORMAL.value: TradingAllocation(
                mode=TradingMode.NORMAL,
                amount=10000.0,  # Default 10k
                risk_level=TradingRiskLevel.BALANCED,
                enabled=True,
                max_trades_per_day=20,
                stop_loss_percentage=2.0,
                take_profit_percentage=3.0
            ),
            TradingMode.HFT.value: TradingAllocation(
                mode=TradingMode.HFT,
                amount=5000.0,  # Default 5k
                risk_level=TradingRiskLevel.SAFE,
                enabled=False,
                max_trades_per_day=100,
                stop_loss_percentage=0.5,
                take_profit_percentage=1.0
            ),
            TradingMode.PAPER.value: TradingAllocation(
                mode=TradingMode.PAPER,
                amount=100000.0,  # Default 100k for paper trading
                risk_level=TradingRiskLevel.AGGRESSIVE,
                enabled=True,
                max_trades_per_day=50,
                stop_loss_percentage=5.0,
                take_profit_percentage=7.0
            )
        }

    def update_allocation(self, mode: TradingMode, allocation: Dict) -> bool:
        """Update trading allocation for a specific mode"""
        try:
            # Validate allocation
            if not self._validate_allocation(allocation):
                return False

            # Update allocation
            self.allocations[mode.value] = TradingAllocation(
                mode=mode,
                amount=float(allocation['amount']),
                risk_level=TradingRiskLevel(allocation['risk_level']),
                enabled=bool(allocation['enabled']),
                max_trades_per_day=int(allocation['max_trades_per_day']),
                stop_loss_percentage=float(allocation['stop_loss_percentage']),
                take_profit_percentage=float(allocation['take_profit_percentage'])
            )

            # Save updated allocations
            self._save_allocations()
            return True

        except Exception as e:
            print(f"Error updating allocation: {e}")
            return False

    def get_allocation(self, mode: TradingMode) -> Optional[TradingAllocation]:
        """Get trading allocation for a specific mode"""
        return self.allocations.get(mode.value)

    def _validate_allocation(self, allocation: Dict) -> bool:
        """Validate trading allocation"""
        try:
            # Check required fields
            required_fields = ['amount', 'risk_level', 'enabled', 
                             'max_trades_per_day', 'stop_loss_percentage', 
                             'take_profit_percentage']
            
            if not all(field in allocation for field in required_fields):
                return False

            # Validate amount
            if float(allocation['amount']) <= 0:
                return False

            # Validate risk level
            if allocation['risk_level'] not in [level.value for level in TradingRiskLevel]:
                return False

            # Validate trade limits
            if int(allocation['max_trades_per_day']) <= 0:
                return False

            # Validate percentages
            if (float(allocation['stop_loss_percentage']) <= 0 or 
                float(allocation['take_profit_percentage']) <= 0):
                return False

            return True

        except Exception as e:
            print(f"Error validating allocation: {e}")
            return False

    def _save_allocations(self):
        """Save trading allocations"""
        try:
            config_path = self._get_config_path()
            data = {
                mode: {
                    'amount': alloc.amount,
                    'risk_level': alloc.risk_level.value,
                    'enabled': alloc.enabled,
                    'max_trades_per_day': alloc.max_trades_per_day,
                    'stop_loss_percentage': alloc.stop_loss_percentage,
                    'take_profit_percentage': alloc.take_profit_percentage
                }
                for mode, alloc in self.allocations.items()
            }
            
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(data, f, indent=4)

        except Exception as e:
            print(f"Error saving allocations: {e}")

    def _get_config_path(self) -> str:
        """Get path to configuration file"""
        return os.path.join(os.path.dirname(__file__), 
                          '..', 'config', 
                          f'trading_allocation_{self.user_id}.json')
