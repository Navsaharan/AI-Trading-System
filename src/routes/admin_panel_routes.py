from flask import Blueprint, jsonify, request
from typing import Dict, Optional
import json
import os
from datetime import datetime

admin_panel = Blueprint('admin_panel', __name__)

class AdminPanelManager:
    def __init__(self):
        self.config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        os.makedirs(self.config_dir, exist_ok=True)

    def get_layout_path(self, user_id: str) -> str:
        """Get path to user's layout configuration file"""
        return os.path.join(self.config_dir, f'admin_layout_{user_id}.json')

    def get_default_layout_path(self) -> str:
        """Get path to default layout configuration file"""
        return os.path.join(self.config_dir, 'admin_layout_default.json')

    def load_layout(self, user_id: str) -> Dict:
        """Load user's admin panel layout"""
        try:
            layout_path = self.get_layout_path(user_id)
            if os.path.exists(layout_path):
                with open(layout_path, 'r') as f:
                    return json.load(f)
            return self.load_default_layout()
        except Exception as e:
            print(f"Error loading layout: {e}")
            return self.load_default_layout()

    def load_default_layout(self) -> Dict:
        """Load default admin panel layout"""
        try:
            default_path = self.get_default_layout_path()
            if os.path.exists(default_path):
                with open(default_path, 'r') as f:
                    return json.load(f)
            return self.get_default_layout()
        except Exception as e:
            print(f"Error loading default layout: {e}")
            return self.get_default_layout()

    def save_layout(self, user_id: str, layout: Dict) -> bool:
        """Save user's admin panel layout"""
        try:
            layout_path = self.get_layout_path(user_id)
            with open(layout_path, 'w') as f:
                json.dump(layout, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving layout: {e}")
            return False

    def get_default_layout(self) -> Dict:
        """Get default admin panel layout structure"""
        return {
            "pages": [
                {
                    "id": "dashboard",
                    "title": "Dashboard",
                    "icon": "dashboard",
                    "order": 1,
                    "visible": True,
                    "sections": [
                        {
                            "id": "overview",
                            "title": "Overview",
                            "order": 1,
                            "options": [
                                {
                                    "id": "performance",
                                    "title": "Performance Metrics",
                                    "type": "widget"
                                },
                                {
                                    "id": "portfolio",
                                    "title": "Portfolio Overview",
                                    "type": "widget"
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "trading",
                    "title": "Trading",
                    "icon": "trending_up",
                    "order": 2,
                    "visible": True,
                    "sections": [
                        {
                            "id": "allocations",
                            "title": "Trading Allocations",
                            "order": 1,
                            "options": [
                                {
                                    "id": "hft_settings",
                                    "title": "HFT Settings",
                                    "type": "settings"
                                },
                                {
                                    "id": "normal_settings",
                                    "title": "Normal Trading Settings",
                                    "type": "settings"
                                }
                            ]
                        },
                        {
                            "id": "paper_trading",
                            "title": "Paper Trading",
                            "order": 2,
                            "options": [
                                {
                                    "id": "paper_settings",
                                    "title": "Paper Trading Settings",
                                    "type": "settings"
                                },
                                {
                                    "id": "simulation",
                                    "title": "Market Simulation",
                                    "type": "widget"
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "analytics",
                    "title": "Analytics",
                    "icon": "insights",
                    "order": 3,
                    "visible": True,
                    "sections": [
                        {
                            "id": "performance",
                            "title": "Performance Analysis",
                            "order": 1,
                            "options": [
                                {
                                    "id": "charts",
                                    "title": "Performance Charts",
                                    "type": "chart"
                                },
                                {
                                    "id": "reports",
                                    "title": "Trading Reports",
                                    "type": "table"
                                }
                            ]
                        }
                    ]
                }
            ],
            "sidebar": {
                "visible": True,
                "expanded": True
            }
        }

# Initialize admin panel manager
panel_manager = AdminPanelManager()

@admin_panel.route('/api/admin/layout', methods=['GET'])
def get_layout():
    """Get user's admin panel layout"""
    try:
        # Get user ID from session/token
        user_id = request.headers.get('User-ID', 'default')
        layout = panel_manager.load_layout(user_id)
        return jsonify(layout)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_panel.route('/api/admin/layout', methods=['POST'])
def save_layout():
    """Save user's admin panel layout"""
    try:
        # Get user ID from session/token
        user_id = request.headers.get('User-ID', 'default')
        layout = request.json
        
        # Validate layout
        if not layout or 'pages' not in layout:
            return jsonify({"error": "Invalid layout data"}), 400
        
        # Save layout
        success = panel_manager.save_layout(user_id, layout)
        if success:
            return jsonify({"message": "Layout saved successfully"})
        return jsonify({"error": "Failed to save layout"}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_panel.route('/api/admin/default-layout', methods=['GET'])
def get_default_layout():
    """Get default admin panel layout"""
    try:
        layout = panel_manager.load_default_layout()
        return jsonify(layout)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_panel.route('/api/admin/layout/reset', methods=['POST'])
def reset_layout():
    """Reset user's admin panel layout to default"""
    try:
        # Get user ID from session/token
        user_id = request.headers.get('User-ID', 'default')
        
        # Load default layout
        default_layout = panel_manager.load_default_layout()
        
        # Save as user's layout
        success = panel_manager.save_layout(user_id, default_layout)
        if success:
            return jsonify({"message": "Layout reset successfully"})
        return jsonify({"error": "Failed to reset layout"}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
