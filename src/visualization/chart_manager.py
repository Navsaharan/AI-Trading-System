from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class ChartManager:
    """Advanced charting system for the trading platform."""
    
    def __init__(self):
        self.chart_themes = {
            "light": {
                "bg_color": "white",
                "grid_color": "lightgrey",
                "text_color": "black",
                "up_color": "green",
                "down_color": "red"
            },
            "dark": {
                "bg_color": "#1e1e1e",
                "grid_color": "#333333",
                "text_color": "white",
                "up_color": "#00ff1a",
                "down_color": "#ff355e"
            }
        }
    
    def create_advanced_chart(self, market_data: pd.DataFrame,
                            indicators: Dict = None,
                            theme: str = "dark") -> Dict:
        """Create an advanced trading chart with multiple indicators."""
        try:
            # Create figure with secondary y-axis
            fig = make_subplots(
                rows=2,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                subplot_titles=("Price", "Volume"),
                row_heights=[0.7, 0.3]
            )
            
            # Add candlestick
            fig.add_trace(
                go.Candlestick(
                    x=market_data.index,
                    open=market_data["open"],
                    high=market_data["high"],
                    low=market_data["low"],
                    close=market_data["close"],
                    name="OHLC"
                ),
                row=1,
                col=1
            )
            
            # Add volume bars
            colors = [
                self.chart_themes[theme]["up_color"]
                if row["close"] >= row["open"]
                else self.chart_themes[theme]["down_color"]
                for index, row in market_data.iterrows()
            ]
            
            fig.add_trace(
                go.Bar(
                    x=market_data.index,
                    y=market_data["volume"],
                    name="Volume",
                    marker_color=colors
                ),
                row=2,
                col=1
            )
            
            # Add indicators if provided
            if indicators:
                self._add_indicators(fig, market_data, indicators, theme)
            
            # Update layout
            fig.update_layout(
                title_text="Advanced Trading Chart",
                xaxis_rangeslider_visible=False,
                plot_bgcolor=self.chart_themes[theme]["bg_color"],
                paper_bgcolor=self.chart_themes[theme]["bg_color"],
                font=dict(color=self.chart_themes[theme]["text_color"])
            )
            
            return {
                "success": True,
                "chart": fig,
                "message": "Chart created successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create chart"
            }
    
    def create_technical_dashboard(self, market_data: pd.DataFrame,
                                 analysis_data: Dict,
                                 theme: str = "dark") -> Dict:
        """Create a technical analysis dashboard."""
        try:
            # Create figure with multiple subplots
            fig = make_subplots(
                rows=4,
                cols=2,
                shared_xaxes=True,
                vertical_spacing=0.03,
                subplot_titles=(
                    "Price Action",
                    "Momentum",
                    "Volume Analysis",
                    "Volatility",
                    "Trend Analysis",
                    "Support/Resistance",
                    "Order Flow",
                    "Market Profile"
                )
            )
            
            # Add price action chart
            self._add_price_action(fig, market_data, theme, row=1, col=1)
            
            # Add momentum indicators
            self._add_momentum_indicators(
                fig,
                market_data,
                analysis_data,
                theme,
                row=1,
                col=2
            )
            
            # Add volume analysis
            self._add_volume_analysis(
                fig,
                market_data,
                analysis_data,
                theme,
                row=2,
                col=1
            )
            
            # Add volatility indicators
            self._add_volatility_indicators(
                fig,
                market_data,
                analysis_data,
                theme,
                row=2,
                col=2
            )
            
            # Add trend analysis
            self._add_trend_analysis(
                fig,
                market_data,
                analysis_data,
                theme,
                row=3,
                col=1
            )
            
            # Add support/resistance levels
            self._add_support_resistance(
                fig,
                market_data,
                analysis_data,
                theme,
                row=3,
                col=2
            )
            
            # Add order flow
            self._add_order_flow(
                fig,
                market_data,
                analysis_data,
                theme,
                row=4,
                col=1
            )
            
            # Add market profile
            self._add_market_profile(
                fig,
                market_data,
                analysis_data,
                theme,
                row=4,
                col=2
            )
            
            # Update layout
            fig.update_layout(
                height=1200,
                showlegend=True,
                plot_bgcolor=self.chart_themes[theme]["bg_color"],
                paper_bgcolor=self.chart_themes[theme]["bg_color"],
                font=dict(color=self.chart_themes[theme]["text_color"])
            )
            
            return {
                "success": True,
                "dashboard": fig,
                "message": "Technical dashboard created successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create technical dashboard"
            }
    
    def create_ai_insight_chart(self, market_data: pd.DataFrame,
                              ai_predictions: Dict,
                              theme: str = "dark") -> Dict:
        """Create chart with AI insights and predictions."""
        try:
            # Create figure with secondary y-axis
            fig = make_subplots(
                rows=3,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                subplot_titles=(
                    "Price & AI Predictions",
                    "AI Confidence",
                    "Risk Analysis"
                ),
                row_heights=[0.5, 0.25, 0.25]
            )
            
            # Add price chart with AI predictions
            self._add_price_with_predictions(
                fig,
                market_data,
                ai_predictions,
                theme,
                row=1,
                col=1
            )
            
            # Add AI confidence indicators
            self._add_ai_confidence(
                fig,
                ai_predictions,
                theme,
                row=2,
                col=1
            )
            
            # Add risk analysis
            self._add_risk_analysis(
                fig,
                ai_predictions,
                theme,
                row=3,
                col=1
            )
            
            # Update layout
            fig.update_layout(
                height=800,
                showlegend=True,
                plot_bgcolor=self.chart_themes[theme]["bg_color"],
                paper_bgcolor=self.chart_themes[theme]["bg_color"],
                font=dict(color=self.chart_themes[theme]["text_color"])
            )
            
            return {
                "success": True,
                "chart": fig,
                "message": "AI insight chart created successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create AI insight chart"
            }
    
    def _add_indicators(self, fig: go.Figure, market_data: pd.DataFrame,
                       indicators: Dict, theme: str):
        """Add technical indicators to the chart."""
        try:
            # Add Moving Averages
            if "ma" in indicators:
                for ma in indicators["ma"]:
                    ma_data = market_data["close"].rolling(
                        window=ma["period"]
                    ).mean()
                    fig.add_trace(
                        go.Scatter(
                            x=market_data.index,
                            y=ma_data,
                            name=f"MA{ma['period']}",
                            line=dict(width=1)
                        ),
                        row=1,
                        col=1
                    )
            
            # Add Bollinger Bands
            if "bollinger" in indicators:
                period = indicators["bollinger"]["period"]
                std_dev = indicators["bollinger"]["std_dev"]
                
                ma = market_data["close"].rolling(window=period).mean()
                std = market_data["close"].rolling(window=period).std()
                
                upper_band = ma + (std * std_dev)
                lower_band = ma - (std * std_dev)
                
                fig.add_trace(
                    go.Scatter(
                        x=market_data.index,
                        y=upper_band,
                        name="Upper BB",
                        line=dict(width=1)
                    ),
                    row=1,
                    col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=market_data.index,
                        y=lower_band,
                        name="Lower BB",
                        line=dict(width=1)
                    ),
                    row=1,
                    col=1
                )
            
            # Add RSI
            if "rsi" in indicators:
                period = indicators["rsi"]["period"]
                rsi = self._calculate_rsi(market_data["close"], period)
                
                fig.add_trace(
                    go.Scatter(
                        x=market_data.index,
                        y=rsi,
                        name="RSI",
                        line=dict(width=1)
                    ),
                    row=2,
                    col=1
                )
            
            # Add MACD
            if "macd" in indicators:
                macd_line, signal_line, macd_hist = self._calculate_macd(
                    market_data["close"]
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=market_data.index,
                        y=macd_line,
                        name="MACD",
                        line=dict(width=1)
                    ),
                    row=2,
                    col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=market_data.index,
                        y=signal_line,
                        name="Signal",
                        line=dict(width=1)
                    ),
                    row=2,
                    col=1
                )
        except Exception as e:
            print(f"Error adding indicators: {str(e)}")
    
    def _calculate_rsi(self, data: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, data: pd.Series,
                       fast_period: int = 12,
                       slow_period: int = 26,
                       signal_period: int = 9) -> tuple:
        """Calculate MACD (Moving Average Convergence Divergence)."""
        exp1 = data.ewm(span=fast_period, adjust=False).mean()
        exp2 = data.ewm(span=slow_period, adjust=False).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        macd_hist = macd_line - signal_line
        return macd_line, signal_line, macd_hist
    
    def _add_price_with_predictions(self, fig: go.Figure,
                                  market_data: pd.DataFrame,
                                  ai_predictions: Dict,
                                  theme: str,
                                  row: int,
                                  col: int):
        """Add price chart with AI predictions."""
        try:
            # Add candlestick chart
            fig.add_trace(
                go.Candlestick(
                    x=market_data.index,
                    open=market_data["open"],
                    high=market_data["high"],
                    low=market_data["low"],
                    close=market_data["close"],
                    name="Price"
                ),
                row=row,
                col=col
            )
            
            # Add AI predictions
            if "price_predictions" in ai_predictions:
                fig.add_trace(
                    go.Scatter(
                        x=ai_predictions["price_predictions"]["timestamp"],
                        y=ai_predictions["price_predictions"]["values"],
                        name="AI Prediction",
                        line=dict(
                            color="yellow",
                            width=2,
                            dash="dash"
                        )
                    ),
                    row=row,
                    col=col
                )
            
            # Add prediction intervals
            if "prediction_intervals" in ai_predictions:
                fig.add_trace(
                    go.Scatter(
                        x=ai_predictions["prediction_intervals"]["timestamp"],
                        y=ai_predictions["prediction_intervals"]["upper"],
                        name="Upper Bound",
                        line=dict(width=0),
                        showlegend=False
                    ),
                    row=row,
                    col=col
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=ai_predictions["prediction_intervals"]["timestamp"],
                        y=ai_predictions["prediction_intervals"]["lower"],
                        name="Lower Bound",
                        line=dict(width=0),
                        fill="tonexty",
                        fillcolor="rgba(255, 255, 0, 0.1)",
                        showlegend=False
                    ),
                    row=row,
                    col=col
                )
        except Exception as e:
            print(f"Error adding price with predictions: {str(e)}")
    
    def _add_ai_confidence(self, fig: go.Figure, ai_predictions: Dict,
                          theme: str, row: int, col: int):
        """Add AI confidence indicators."""
        try:
            if "confidence_scores" in ai_predictions:
                fig.add_trace(
                    go.Scatter(
                        x=ai_predictions["confidence_scores"]["timestamp"],
                        y=ai_predictions["confidence_scores"]["values"],
                        name="AI Confidence",
                        fill="tozeroy",
                        fillcolor="rgba(0, 255, 0, 0.1)",
                        line=dict(color="green", width=2)
                    ),
                    row=row,
                    col=col
                )
        except Exception as e:
            print(f"Error adding AI confidence: {str(e)}")
    
    def _add_risk_analysis(self, fig: go.Figure, ai_predictions: Dict,
                          theme: str, row: int, col: int):
        """Add risk analysis indicators."""
        try:
            if "risk_metrics" in ai_predictions:
                fig.add_trace(
                    go.Scatter(
                        x=ai_predictions["risk_metrics"]["timestamp"],
                        y=ai_predictions["risk_metrics"]["values"],
                        name="Risk Level",
                        fill="tozeroy",
                        fillcolor="rgba(255, 0, 0, 0.1)",
                        line=dict(color="red", width=2)
                    ),
                    row=row,
                    col=col
                )
        except Exception as e:
            print(f"Error adding risk analysis: {str(e)}")
