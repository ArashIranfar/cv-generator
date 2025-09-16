# -*- coding: utf-8 -*-
"""
Configuration settings for the CV Generator application.
"""
import os
from typing import List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    """Application configuration settings."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL: str = "gpt-5-mini"
    OPENAI_BASE_URL: Optional[str] = os.getenv('THIRD_PARTY_BASE_URL')
    OPENAI_TEMPERATURE: float = 0.3
    
    # Application Configuration
    SUPPORTED_LANGUAGES: List[str] = None
    DEFAULT_LANGUAGE: str = 'en'
    
    # File Paths
    TEMPLATE_FILE: str = 'templates/cv_template.html'
    DATA_DIRECTORY: str = 'data'
    SAMPLE_DATA_DIRECTORY: str = 'data/sample'

    PROJECT_ROOT = Path(__file__).parent.parent
    ASSETS_DIR = PROJECT_ROOT / 'assets'
    
    # CV Sections
    CV_SECTIONS: List[str] = None
    
    # PDF Configuration
    PDF_MAX_SIZE_MB: float = 10.0
    
    # UI Configuration
    PAGE_TITLE: str = "AI-Powered CV Generator"
    PAGE_ICON: str = "🤖"
    LAYOUT: str = "wide"
    
    def __post_init__(self):
        """Initialize default values that require list creation."""
        if self.SUPPORTED_LANGUAGES is None:
            self.SUPPORTED_LANGUAGES = ['en', 'fa']
        
        if self.CV_SECTIONS is None:
            self.CV_SECTIONS = [
                'personal', 'summary', 'skills', 'experience', 
                'projects', 'education', 'publications', 'teaching'
            ]
    
    def validate(self) -> bool:
        """Validate that required settings are present."""
        if not self.OPENAI_API_KEY:
            return False
        
        if self.DEFAULT_LANGUAGE not in self.SUPPORTED_LANGUAGES:
            return False
            
        return True
    
    def get_language_display_name(self, lang_code: str) -> str:
        """Get display name for language code."""
        language_names = {
            'en': 'English',
            'fa': 'Farsi'
        }
        return language_names.get(lang_code, lang_code.upper())

# Global settings instance
settings = Settings()