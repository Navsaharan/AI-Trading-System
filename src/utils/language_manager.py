import json
from pathlib import Path
from typing import Dict, Optional

class LanguageManager:
    def __init__(self):
        self.translations: Dict[str, Dict] = {}
        self.current_language = 'en'
        self._load_translations()
    
    def _load_translations(self):
        """Load all translation files from the translations directory"""
        translations_dir = Path(__file__).parent.parent / 'translations'
        for file in translations_dir.glob('*.json'):
            lang_code = file.stem
            with open(file, 'r', encoding='utf-8') as f:
                self.translations[lang_code] = json.load(f)
    
    def set_language(self, lang_code: str) -> bool:
        """Set the current language"""
        if lang_code in self.translations:
            self.current_language = lang_code
            return True
        return False
    
    def get_text(self, key: str, lang_code: Optional[str] = None) -> str:
        """Get translated text for a key"""
        lang = lang_code or self.current_language
        
        # Default to English if language not found
        if lang not in self.translations:
            lang = 'en'
        
        # Navigate nested keys (e.g., "common.save")
        keys = key.split('.')
        value = self.translations[lang]
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            # Return the key itself if translation not found
            return key.split('.')[-1]
    
    def get_all_languages(self) -> Dict[str, str]:
        """Get list of available languages"""
        return {
            'en': 'English',
            'hi': 'हिंदी'
        }
    
    def is_rtl(self, lang_code: Optional[str] = None) -> bool:
        """Check if language is RTL"""
        rtl_languages = ['ar', 'he', 'fa']  # Add more as needed
        return (lang_code or self.current_language) in rtl_languages

# Create a global instance
language_manager = LanguageManager()
