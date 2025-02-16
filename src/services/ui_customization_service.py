from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import os
from datetime import datetime

@dataclass
class UILayout:
    id: str
    name: str
    user_id: str
    components: Dict
    theme: Dict
    is_active: bool
    created_at: datetime
    updated_at: datetime

@dataclass
class UIComponent:
    id: str
    type: str
    position: Dict
    settings: Dict
    visible: bool

class UICustomizationService:
    def __init__(self):
        self.layouts_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'layouts')
        os.makedirs(self.layouts_dir, exist_ok=True)

    async def create_layout(self, user_id: str, name: str, template: Optional[str] = None) -> UILayout:
        """Create a new UI layout"""
        try:
            # Load template if specified
            base_layout = self._load_template(template) if template else self._get_default_layout()
            
            # Create layout object
            layout = UILayout(
                id=self._generate_id(),
                name=name,
                user_id=user_id,
                components=base_layout["components"],
                theme=base_layout["theme"],
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Save layout
            await self._save_layout(layout)
            
            return layout

        except Exception as e:
            print(f"Error creating layout: {e}")
            return None

    async def update_layout(self, layout_id: str, updates: Dict) -> UILayout:
        """Update existing layout"""
        try:
            # Load existing layout
            layout = await self._load_layout(layout_id)
            if not layout:
                return None
            
            # Apply updates
            if "components" in updates:
                layout.components.update(updates["components"])
            if "theme" in updates:
                layout.theme.update(updates["theme"])
            if "name" in updates:
                layout.name = updates["name"]
            
            layout.updated_at = datetime.now()
            
            # Save updated layout
            await self._save_layout(layout)
            
            return layout

        except Exception as e:
            print(f"Error updating layout: {e}")
            return None

    async def get_user_layouts(self, user_id: str) -> List[UILayout]:
        """Get all layouts for a user"""
        try:
            layouts = []
            layout_files = os.listdir(self.layouts_dir)
            
            for file in layout_files:
                if file.startswith(f"layout_{user_id}_"):
                    layout = await self._load_layout_from_file(file)
                    if layout:
                        layouts.append(layout)
            
            return layouts

        except Exception as e:
            print(f"Error getting user layouts: {e}")
            return []

    async def set_active_layout(self, user_id: str, layout_id: str) -> bool:
        """Set active layout for user"""
        try:
            # Get all user layouts
            layouts = await self.get_user_layouts(user_id)
            
            # Update active status
            for layout in layouts:
                layout.is_active = layout.id == layout_id
                await self._save_layout(layout)
            
            return True

        except Exception as e:
            print(f"Error setting active layout: {e}")
            return False

    async def update_component(self, layout_id: str, component_id: str, updates: Dict) -> bool:
        """Update specific component in layout"""
        try:
            # Load layout
            layout = await self._load_layout(layout_id)
            if not layout:
                return False
            
            # Update component
            if component_id in layout.components:
                layout.components[component_id].update(updates)
                layout.updated_at = datetime.now()
                
                # Save layout
                await self._save_layout(layout)
                return True
            
            return False

        except Exception as e:
            print(f"Error updating component: {e}")
            return False

    async def create_component(self, layout_id: str, component: Dict) -> UIComponent:
        """Add new component to layout"""
        try:
            # Load layout
            layout = await self._load_layout(layout_id)
            if not layout:
                return None
            
            # Create component
            new_component = UIComponent(
                id=self._generate_id(),
                type=component["type"],
                position=component["position"],
                settings=component.get("settings", {}),
                visible=True
            )
            
            # Add to layout
            layout.components[new_component.id] = new_component.__dict__
            layout.updated_at = datetime.now()
            
            # Save layout
            await self._save_layout(layout)
            
            return new_component

        except Exception as e:
            print(f"Error creating component: {e}")
            return None

    def get_available_templates(self) -> List[Dict]:
        """Get list of available layout templates"""
        return [
            {
                "id": "trading",
                "name": "Trading Dashboard",
                "description": "Optimized for active trading with charts and order book"
            },
            {
                "id": "analysis",
                "name": "Analysis Dashboard",
                "description": "Focus on technical and fundamental analysis"
            },
            {
                "id": "portfolio",
                "name": "Portfolio Dashboard",
                "description": "Track your investments and performance"
            },
            {
                "id": "news",
                "name": "News Dashboard",
                "description": "Stay updated with market news and events"
            }
        ]

    def get_available_themes(self) -> List[Dict]:
        """Get list of available UI themes"""
        return [
            {
                "id": "dark",
                "name": "Dark Theme",
                "colors": {
                    "background": "#1a1a1a",
                    "text": "#ffffff",
                    "primary": "#2196f3",
                    "secondary": "#f50057"
                }
            },
            {
                "id": "light",
                "name": "Light Theme",
                "colors": {
                    "background": "#ffffff",
                    "text": "#000000",
                    "primary": "#1976d2",
                    "secondary": "#dc004e"
                }
            },
            {
                "id": "trading",
                "name": "Trading Theme",
                "colors": {
                    "background": "#0a0e17",
                    "text": "#e0e0e0",
                    "primary": "#00c853",
                    "secondary": "#ff1744"
                }
            }
        ]

    async def _save_layout(self, layout: UILayout) -> bool:
        """Save layout to file"""
        try:
            file_path = os.path.join(
                self.layouts_dir,
                f"layout_{layout.user_id}_{layout.id}.json"
            )
            
            with open(file_path, 'w') as f:
                json.dump(layout.__dict__, f, indent=4, default=str)
            
            return True

        except Exception as e:
            print(f"Error saving layout: {e}")
            return False

    async def _load_layout(self, layout_id: str) -> Optional[UILayout]:
        """Load layout from file"""
        try:
            layout_files = os.listdir(self.layouts_dir)
            
            for file in layout_files:
                if layout_id in file:
                    return await self._load_layout_from_file(file)
            
            return None

        except Exception as e:
            print(f"Error loading layout: {e}")
            return None

    def _load_template(self, template_id: str) -> Dict:
        """Load layout template"""
        templates = {
            "trading": {
                "components": {
                    "chart": {
                        "type": "tradingview",
                        "position": {"x": 0, "y": 0, "w": 8, "h": 6},
                        "settings": {"interval": "1m", "studies": ["RSI", "MACD"]}
                    },
                    "orderbook": {
                        "type": "orderbook",
                        "position": {"x": 8, "y": 0, "w": 4, "h": 6},
                        "settings": {"depth": 10}
                    },
                    "trades": {
                        "type": "trades",
                        "position": {"x": 0, "y": 6, "w": 12, "h": 3},
                        "settings": {"limit": 50}
                    }
                },
                "theme": self.get_available_themes()[2]
            },
            # Add more templates
        }
        
        return templates.get(template_id, self._get_default_layout())

    def _get_default_layout(self) -> Dict:
        """Get default layout configuration"""
        return {
            "components": {
                "welcome": {
                    "type": "welcome",
                    "position": {"x": 0, "y": 0, "w": 12, "h": 3},
                    "settings": {}
                }
            },
            "theme": self.get_available_themes()[0]
        }

    def _generate_id(self) -> str:
        """Generate unique ID"""
        return f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(4).hex()}"
