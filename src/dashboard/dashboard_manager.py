from typing import Dict, List, Optional
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from ..visualization.chart_manager import ChartManager
from ..models.model_manager import ModelManager
from ..analysis.market_analysis import MarketAnalysis

class DashboardManager:
    """Manage the trading system dashboard with real-time updates."""
    
    def __init__(self):
        self.app = dash.Dash(__name__)
        self.chart_manager = ChartManager()
        self.model_manager = ModelManager()
        self.market_analysis = MarketAnalysis()
        
        # Initialize dashboard
        self._initialize_dashboard()
    
    def _initialize_dashboard(self):
        """Initialize dashboard layout and callbacks."""
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1("FamilyHVSDN Trading Platform",
                        style={
                            "textAlign": "center",
                            "color": "#00ff1a",
                            "fontFamily": "Arial, sans-serif",
                            "fontSize": "32px",
                            "fontWeight": "bold",
                            "padding": "20px",
                            "backgroundColor": "#1e1e1e",
                            "borderBottom": "2px solid #00ff1a",
                            "marginBottom": "20px"
                        }),
                html.Div([
                    html.Div(id="last-update"),
                    html.Button("Refresh", 
                              id="refresh-button",
                              style={
                                  "backgroundColor": "#00ff1a",
                                  "color": "#1e1e1e",
                                  "border": "none",
                                  "padding": "10px 20px",
                                  "borderRadius": "5px",
                                  "cursor": "pointer"
                              })
                ], style={
                    "display": "flex",
                    "justifyContent": "flex-end",
                    "padding": "10px"
                })
            ], style={
                "marginBottom": "20px"
            }),
            
            # Main content
            html.Div([
                # Left panel - Portfolio Overview
                html.Div([
                    html.H2("Portfolio Overview"),
                    dcc.Graph(id="portfolio-chart"),
                    html.Div(id="portfolio-metrics"),
                    html.Div(id="top-holdings")
                ], className="panel"),
                
                # Center panel - Trading Activity
                html.Div([
                    html.H2("Trading Activity"),
                    dcc.Graph(id="trading-chart"),
                    html.Div(id="trading-signals"),
                    html.Div(id="active-trades")
                ], className="panel"),
                
                # Right panel - Risk Analysis
                html.Div([
                    html.H2("Risk Analysis"),
                    dcc.Graph(id="risk-chart"),
                    html.Div(id="risk-metrics"),
                    html.Div(id="alerts")
                ], className="panel")
            ], className="main-content"),
            
            # Bottom panel - Detailed Analysis
            html.Div([
                # Market Analysis
                html.Div([
                    html.H2("Market Analysis"),
                    dcc.Tabs([
                        dcc.Tab(label="Technical Analysis", children=[
                            dcc.Graph(id="technical-chart")
                        ]),
                        dcc.Tab(label="Sentiment Analysis", children=[
                            dcc.Graph(id="sentiment-chart")
                        ]),
                        dcc.Tab(label="AI Predictions", children=[
                            dcc.Graph(id="prediction-chart")
                        ])
                    ])
                ], className="panel"),
                
                # Performance Analysis
                html.Div([
                    html.H2("Performance Analysis"),
                    dcc.Tabs([
                        dcc.Tab(label="Returns", children=[
                            dcc.Graph(id="returns-chart")
                        ]),
                        dcc.Tab(label="Attribution", children=[
                            dcc.Graph(id="attribution-chart")
                        ]),
                        dcc.Tab(label="Risk Metrics", children=[
                            dcc.Graph(id="risk-metrics-chart")
                        ])
                    ])
                ], className="panel")
            ], className="bottom-content")
        ])
        
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """Setup dashboard callbacks for interactivity."""
        
        @self.app.callback(
            [Output("portfolio-chart", "figure"),
             Output("portfolio-metrics", "children"),
             Output("top-holdings", "children")],
            [Input("refresh-button", "n_clicks")]
        )
        def update_portfolio(n_clicks):
            """Update portfolio section."""
            try:
                # Get portfolio data
                portfolio_data = self._get_portfolio_data()
                
                # Create portfolio chart
                portfolio_chart = self._create_portfolio_chart(portfolio_data)
                
                # Create portfolio metrics
                portfolio_metrics = self._create_portfolio_metrics(portfolio_data)
                
                # Create top holdings
                top_holdings = self._create_top_holdings(portfolio_data)
                
                return portfolio_chart, portfolio_metrics, top_holdings
            except Exception as e:
                print(f"Error updating portfolio: {str(e)}")
                return {}, [], []
        
        @self.app.callback(
            [Output("trading-chart", "figure"),
             Output("trading-signals", "children"),
             Output("active-trades", "children")],
            [Input("refresh-button", "n_clicks")]
        )
        def update_trading(n_clicks):
            """Update trading section."""
            try:
                # Get trading data
                trading_data = self._get_trading_data()
                
                # Create trading chart
                trading_chart = self._create_trading_chart(trading_data)
                
                # Create trading signals
                trading_signals = self._create_trading_signals(trading_data)
                
                # Create active trades
                active_trades = self._create_active_trades(trading_data)
                
                return trading_chart, trading_signals, active_trades
            except Exception as e:
                print(f"Error updating trading: {str(e)}")
                return {}, [], []
        
        @self.app.callback(
            [Output("risk-chart", "figure"),
             Output("risk-metrics", "children"),
             Output("alerts", "children")],
            [Input("refresh-button", "n_clicks")]
        )
        def update_risk(n_clicks):
            """Update risk section."""
            try:
                # Get risk data
                risk_data = self._get_risk_data()
                
                # Create risk chart
                risk_chart = self._create_risk_chart(risk_data)
                
                # Create risk metrics
                risk_metrics = self._create_risk_metrics(risk_data)
                
                # Create alerts
                alerts = self._create_alerts(risk_data)
                
                return risk_chart, risk_metrics, alerts
            except Exception as e:
                print(f"Error updating risk: {str(e)}")
                return {}, [], []
    
    def _get_portfolio_data(self) -> Dict:
        """Get portfolio data for dashboard."""
        try:
            return {
                "holdings": self._get_holdings(),
                "performance": self._get_performance(),
                "allocation": self._get_allocation()
            }
        except Exception:
            return {}
    
    def _get_trading_data(self) -> Dict:
        """Get trading data for dashboard."""
        try:
            return {
                "signals": self._get_trading_signals(),
                "active_trades": self._get_active_trades(),
                "history": self._get_trading_history()
            }
        except Exception:
            return {}
    
    def _get_risk_data(self) -> Dict:
        """Get risk data for dashboard."""
        try:
            return {
                "metrics": self._get_risk_metrics(),
                "exposure": self._get_risk_exposure(),
                "alerts": self._get_risk_alerts()
            }
        except Exception:
            return {}
    
    def _create_portfolio_chart(self, data: Dict) -> go.Figure:
        """Create portfolio chart."""
        try:
            return self.chart_manager.create_advanced_chart(
                data["holdings"],
                {
                    "type": "portfolio",
                    "metrics": ["value", "allocation", "performance"]
                }
            )
        except Exception:
            return go.Figure()
    
    def _create_trading_chart(self, data: Dict) -> go.Figure:
        """Create trading activity chart."""
        try:
            return self.chart_manager.create_advanced_chart(
                data["history"],
                {
                    "type": "trading",
                    "metrics": ["signals", "executions", "pnl"]
                }
            )
        except Exception:
            return go.Figure()
    
    def _create_risk_chart(self, data: Dict) -> go.Figure:
        """Create risk analysis chart."""
        try:
            return self.chart_manager.create_advanced_chart(
                data["metrics"],
                {
                    "type": "risk",
                    "metrics": ["var", "exposure", "correlation"]
                }
            )
        except Exception:
            return go.Figure()
    
    def _create_portfolio_metrics(self, data: Dict) -> List[html.Div]:
        """Create portfolio metrics display."""
        try:
            metrics = []
            
            for metric, value in data["performance"].items():
                metrics.append(
                    html.Div([
                        html.H4(metric),
                        html.P(value)
                    ], className="metric-box")
                )
            
            return metrics
        except Exception:
            return []
    
    def _create_trading_signals(self, data: Dict) -> List[html.Div]:
        """Create trading signals display."""
        try:
            signals = []
            
            for signal in data["signals"]:
                signals.append(
                    html.Div([
                        html.H4(signal["symbol"]),
                        html.P(f"Type: {signal['type']}"),
                        html.P(f"Price: {signal['price']}"),
                        html.P(f"Confidence: {signal['confidence']}")
                    ], className="signal-box")
                )
            
            return signals
        except Exception:
            return []
    
    def _create_risk_metrics(self, data: Dict) -> List[html.Div]:
        """Create risk metrics display."""
        try:
            metrics = []
            
            for metric, value in data["metrics"].items():
                metrics.append(
                    html.Div([
                        html.H4(metric),
                        html.P(value)
                    ], className="metric-box")
                )
            
            return metrics
        except Exception:
            return []
    
    def run_dashboard(self, host: str = "0.0.0.0",
                     port: int = 8050,
                     debug: bool = False):
        """Run the dashboard server."""
        self.app.run_server(host=host, port=port, debug=debug)
