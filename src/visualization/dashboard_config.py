from typing import Dict, List
import pandas as pd
from sqlalchemy import create_engine
from ..config.database import DATABASE_URL

class DashboardManager:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.superset_config = {
            'host': 'localhost',
            'port': 8088,
            'username': 'admin',
            'password': 'admin'
        }
        
        # Pre-built dashboard templates
        self.templates = {
            'trading_overview': {
                'title': 'Trading Overview',
                'charts': [
                    {
                        'name': 'portfolio_performance',
                        'type': 'line',
                        'data_source': 'portfolio_daily',
                        'metrics': ['total_value', 'invested_value'],
                        'dimensions': ['date']
                    },
                    {
                        'name': 'profit_loss',
                        'type': 'bar',
                        'data_source': 'trades',
                        'metrics': ['realized_pl', 'unrealized_pl'],
                        'dimensions': ['date']
                    }
                ]
            },
            'ai_performance': {
                'title': 'AI Model Performance',
                'charts': [
                    {
                        'name': 'prediction_accuracy',
                        'type': 'line',
                        'data_source': 'model_predictions',
                        'metrics': ['accuracy', 'confidence'],
                        'dimensions': ['timestamp']
                    },
                    {
                        'name': 'trading_signals',
                        'type': 'scatter',
                        'data_source': 'trading_signals',
                        'metrics': ['signal_strength'],
                        'dimensions': ['timestamp', 'symbol']
                    }
                ]
            }
        }
    
    def create_superset_dashboard(self, template_name: str, user_id: str) -> Dict:
        """Create a new Superset dashboard from template"""
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"Template {template_name} not found")
        
        dashboard_config = {
            'dashboard_title': f"{template['title']} - {user_id}",
            'css': self._get_custom_css(),
            'position_json': self._get_chart_positions(template['charts']),
            'metadata': {
                'show_native_filters': True,
                'color_scheme': 'supersetColors',
                'refresh_frequency': 60
            }
        }
        
        # Create charts
        charts = []
        for chart_config in template['charts']:
            chart = self._create_chart(chart_config, user_id)
            charts.append(chart)
        
        dashboard_config['charts'] = charts
        return dashboard_config
    
    def _create_chart(self, config: Dict, user_id: str) -> Dict:
        """Create a single chart configuration"""
        return {
            'slice_name': config['name'],
            'viz_type': config['type'],
            'datasource': self._get_datasource(config['data_source'], user_id),
            'form_data': {
                'metrics': config['metrics'],
                'groupby': config['dimensions'],
                'time_range': 'last week',
                'rolling_type': 'None',
                'comparison_type': 'values',
                'annotation_layers': [],
                'show_legend': True,
                'show_controls': True
            }
        }
    
    def _get_custom_css(self) -> str:
        """Get custom CSS for dashboard"""
        return """
        .dashboard-header {
            background: #1a1a1a;
            color: white;
        }
        .chart-container {
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 10px;
            padding: 15px;
        }
        .filter-box {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
        }
        """
    
    def _get_chart_positions(self, charts: List[Dict]) -> str:
        """Generate chart position JSON"""
        positions = {}
        for i, chart in enumerate(charts):
            positions[chart['name']] = {
                'type': 'CHART',
                'id': i + 1,
                'children': [],
                'meta': {
                    'width': 6,
                    'height': 50,
                    'chartId': i + 1
                }
            }
        return positions
    
    def _get_datasource(self, source_name: str, user_id: str) -> Dict:
        """Get or create datasource for charts"""
        query_map = {
            'portfolio_daily': f"""
                SELECT date, total_value, invested_value
                FROM portfolio_snapshots
                WHERE user_id = '{user_id}'
                ORDER BY date
            """,
            'trades': f"""
                SELECT date, realized_pl, unrealized_pl
                FROM trades
                WHERE user_id = '{user_id}'
                ORDER BY date
            """,
            'model_predictions': f"""
                SELECT timestamp, accuracy, confidence
                FROM model_predictions
                WHERE user_id = '{user_id}'
                ORDER BY timestamp
            """,
            'trading_signals': f"""
                SELECT timestamp, symbol, signal_strength
                FROM trading_signals
                WHERE user_id = '{user_id}'
                ORDER BY timestamp
            """
        }
        
        query = query_map.get(source_name)
        if not query:
            raise ValueError(f"Data source {source_name} not found")
        
        df = pd.read_sql(query, self.engine)
        return {
            'name': f"{source_name}_{user_id}",
            'type': 'table',
            'columns': list(df.columns),
            'metrics': [col for col in df.columns if col not in ['date', 'timestamp', 'symbol']]
        }
