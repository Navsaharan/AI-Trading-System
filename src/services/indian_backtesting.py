import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import talib
from datetime import datetime, timedelta
import logging
from .indian_broker_service import IndianBrokerService

class IndianBacktesting:
    def __init__(self, broker_service: IndianBrokerService):
        self.broker_service = broker_service
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    async def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """Get historical data for backtesting"""
        try:
            data = await self.broker_service.get_historical_data(
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date
            )
            return pd.DataFrame(data)
        except Exception as e:
            self.logger.error(f"Error fetching historical data: {e}")
            return pd.DataFrame()

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for strategy testing"""
        try:
            # Basic indicators
            df['SMA_20'] = talib.SMA(df['close'], timeperiod=20)
            df['SMA_50'] = talib.SMA(df['close'], timeperiod=50)
            df['EMA_20'] = talib.EMA(df['close'], timeperiod=20)
            df['RSI'] = talib.RSI(df['close'], timeperiod=14)
            
            # MACD
            df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = talib.MACD(
                df['close'], fastperiod=12, slowperiod=26, signalperiod=9
            )
            
            # Bollinger Bands
            df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = talib.BBANDS(
                df['close'], timeperiod=20, nbdevup=2, nbdevdn=2
            )
            
            # Supertrend
            high = df['high']
            low = df['low']
            close = df['close']
            atr_period = 10
            atr_multiplier = 3.0
            
            # Calculate ATR
            df['ATR'] = talib.ATR(high, low, close, timeperiod=atr_period)
            
            # Calculate basic upper and lower bands
            basic_upper = (high + low) / 2 + atr_multiplier * df['ATR']
            basic_lower = (high + low) / 2 - atr_multiplier * df['ATR']
            
            # Initialize Supertrend columns
            df['ST_Upper'] = basic_upper
            df['ST_Lower'] = basic_lower
            df['Supertrend'] = np.nan
            df['ST_Direction'] = 0
            
            # Calculate Supertrend
            for i in range(1, len(df)):
                if close[i] > df['ST_Upper'][i-1]:
                    df.at[i, 'ST_Direction'] = 1
                elif close[i] < df['ST_Lower'][i-1]:
                    df.at[i, 'ST_Direction'] = -1
                else:
                    df.at[i, 'ST_Direction'] = df['ST_Direction'][i-1]
                    
                if df['ST_Direction'][i] == 1:
                    df.at[i, 'Supertrend'] = df['ST_Lower'][i]
                else:
                    df.at[i, 'Supertrend'] = df['ST_Upper'][i]
            
            # Volume indicators
            df['OBV'] = talib.OBV(df['close'], df['volume'])
            df['ADL'] = talib.AD(df['high'], df['low'], df['close'], df['volume'])
            
            # Momentum indicators
            df['ROC'] = talib.ROC(df['close'], timeperiod=10)
            df['MFI'] = talib.MFI(df['high'], df['low'], df['close'], df['volume'], timeperiod=14)
            
            # Volatility indicators
            df['ATR'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
            df['Volatility'] = df['close'].pct_change().rolling(window=20).std()
            
            return df
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {e}")
            return df

    def moving_average_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        """Moving Average Crossover Strategy"""
        df['Signal'] = 0
        df.loc[df['SMA_20'] > df['SMA_50'], 'Signal'] = 1
        df.loc[df['SMA_20'] < df['SMA_50'], 'Signal'] = -1
        return df

    def rsi_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        """RSI Strategy"""
        df['Signal'] = 0
        df.loc[df['RSI'] < 30, 'Signal'] = 1
        df.loc[df['RSI'] > 70, 'Signal'] = -1
        return df

    def supertrend_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        """Supertrend Strategy"""
        df['Signal'] = df['ST_Direction']
        return df

    def option_selling_strategy(
        self,
        df: pd.DataFrame,
        strike_selection: str = 'atm',
        delta_threshold: float = 0.3
    ) -> pd.DataFrame:
        """Option Selling Strategy"""
        df['Signal'] = 0
        
        # Sell options when volatility is high
        df.loc[df['Volatility'] > df['Volatility'].rolling(window=20).mean(), 'Signal'] = -1
        
        # Buy back when volatility reduces
        df.loc[df['Volatility'] < df['Volatility'].rolling(window=20).mean(), 'Signal'] = 1
        
        return df

    def calculate_position_size(
        self,
        capital: float,
        risk_per_trade: float,
        stop_loss: float,
        entry_price: float
    ) -> int:
        """Calculate position size based on risk management"""
        risk_amount = capital * (risk_per_trade / 100)
        position_size = int(risk_amount / abs(entry_price - stop_loss))
        return position_size

    def calculate_performance_metrics(
        self,
        df: pd.DataFrame,
        risk_free_rate: float = 0.05
    ) -> Dict:
        """Calculate trading performance metrics"""
        try:
            # Calculate daily returns
            df['Returns'] = df['close'].pct_change()
            df['Strategy_Returns'] = df['Returns'] * df['Signal'].shift(1)
            
            # Calculate cumulative returns
            df['Cumulative_Returns'] = (1 + df['Strategy_Returns']).cumprod()
            
            # Calculate various metrics
            total_returns = (df['Cumulative_Returns'].iloc[-1] - 1) * 100
            
            # Annualized return
            days = len(df)
            annual_return = ((1 + total_returns/100) ** (252/days) - 1) * 100
            
            # Volatility
            annual_volatility = df['Strategy_Returns'].std() * np.sqrt(252) * 100
            
            # Sharpe Ratio
            excess_returns = df['Strategy_Returns'] - risk_free_rate/252
            sharpe_ratio = np.sqrt(252) * excess_returns.mean() / df['Strategy_Returns'].std()
            
            # Maximum Drawdown
            cumulative = df['Cumulative_Returns']
            rolling_max = cumulative.expanding().max()
            drawdowns = (cumulative - rolling_max) / rolling_max
            max_drawdown = drawdowns.min() * 100
            
            # Win Rate
            winning_trades = (df['Strategy_Returns'] > 0).sum()
            total_trades = (df['Strategy_Returns'] != 0).sum()
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            
            # Profit Factor
            gross_profits = df.loc[df['Strategy_Returns'] > 0, 'Strategy_Returns'].sum()
            gross_losses = abs(df.loc[df['Strategy_Returns'] < 0, 'Strategy_Returns'].sum())
            profit_factor = gross_profits / gross_losses if gross_losses != 0 else float('inf')
            
            return {
                'total_returns': round(total_returns, 2),
                'annual_return': round(annual_return, 2),
                'annual_volatility': round(annual_volatility, 2),
                'sharpe_ratio': round(sharpe_ratio, 2),
                'max_drawdown': round(max_drawdown, 2),
                'win_rate': round(win_rate, 2),
                'profit_factor': round(profit_factor, 2),
                'total_trades': total_trades,
                'portfolio_values': df['Cumulative_Returns'].tolist(),
                'dates': df.index.tolist()
            }
        except Exception as e:
            self.logger.error(f"Error calculating performance metrics: {e}")
            return {}

    async def run_backtest(
        self,
        strategy: str,
        symbol: str,
        timeframe: str,
        start_date: str,
        end_date: str,
        initial_capital: float = 100000,
        risk_per_trade: float = 1,
        **strategy_params
    ) -> Dict:
        """Run backtest for a given strategy"""
        try:
            # Get historical data
            df = await self.get_historical_data(symbol, timeframe, start_date, end_date)
            if df.empty:
                return {'status': 'error', 'message': 'No historical data available'}
            
            # Calculate indicators
            df = self.calculate_indicators(df)
            
            # Apply strategy
            if strategy == 'moving_average':
                df = self.moving_average_strategy(df)
            elif strategy == 'rsi':
                df = self.rsi_strategy(df)
            elif strategy == 'supertrend':
                df = self.supertrend_strategy(df)
            elif strategy == 'option_selling':
                df = self.option_selling_strategy(df, **strategy_params)
            else:
                return {'status': 'error', 'message': 'Invalid strategy'}
            
            # Calculate performance metrics
            metrics = self.calculate_performance_metrics(df)
            
            return {
                'status': 'success',
                'data': {
                    'metrics': metrics,
                    'trades': len(df[df['Signal'] != 0]),
                    'strategy': strategy,
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'start_date': start_date,
                    'end_date': end_date
                }
            }
        except Exception as e:
            self.logger.error(f"Error running backtest: {e}")
            return {'status': 'error', 'message': str(e)}
