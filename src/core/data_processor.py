import json
import os
from io import BytesIO
from typing import Dict, Any, List, Optional

from config.settings import settings
from src.utils.exceptions import FileLoadError, DataValidationError
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DataProcessor:
    """Handles loading and preprocessing of CV data from various sources."""
    
    def __init__(self, lang: str = 'en'):
        """
        Initialize the data processor.
        
        Args:
            lang: Language code ('en' or 'fa')
        """
        if lang not in settings.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {lang}")
        
        self.lang = lang
        self.data_sections = settings.CV_SECTIONS.copy()
        
    def load_data_from_directory(self, data_dir: str = None) -> Dict[str, Any]:
        """
        Load CV data from JSON files in a directory.
        
        Args:
            data_dir: Directory containing JSON files. Defaults to settings.DATA_DIRECTORY
            
        Returns:
            Dictionary containing loaded CV data
            
        Raises:
            FileLoadError: If directory doesn't exist or files can't be loaded
        """
        if data_dir is None:
            data_dir = settings.DATA_DIRECTORY
            
        if not os.path.isdir(data_dir):
            raise FileLoadError(f"Data directory not found: {data_dir}")
        
        data = {}
        missing_files = []
        
        for section in self.data_sections:
            filename = os.path.join(data_dir, f"{section}_{self.lang}.json")
            
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data[section] = json.load(f)
                logger.info(f"Loaded {filename}")
                
            except FileNotFoundError:
                missing_files.append(filename)
                data[section] = {}
                logger.warning(f"File not found: {filename}")
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error in {filename}: {e}")
                data[section] = {}
                
            except Exception as e:
                logger.error(f"Unexpected error loading {filename}: {e}")
                data[section] = {}
        
        if missing_files:
            logger.warning(f"Missing data files: {', '.join(missing_files)}")
        
        return data
    
    def load_from_file(self, file_content: bytes) -> Dict[str, Any]:
        """
        Load CV data from a single JSON file.
        
        Args:
            file_content: Raw file content as bytes
            
        Returns:
            Dictionary containing loaded CV data
            
        Raises:
            FileLoadError: If file cannot be parsed
        """
        try:
            # Parse JSON from bytes
            data = json.load(BytesIO(file_content))
            logger.info("Successfully loaded data from uploaded file")
            
            # Validate the structure
            if not self.validate_data_structure(data):
                logger.warning("Data structure validation failed, but proceeding anyway")
            
            return data
            
        except json.JSONDecodeError as e:
            raise FileLoadError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise FileLoadError(f"Error reading file: {e}")
    
    def validate_data_structure(self, data: Dict[str, Any]) -> bool:
        """
        Validate that the data dictionary has expected structure.
        
        Args:
            data: CV data dictionary to validate
            
        Returns:
            True if structure is valid, False otherwise
        """
        if not isinstance(data, dict):
            logger.error("Data is not a dictionary")
            return False
        
        # Check if at least some expected sections are present
        present_sections = [section for section in self.data_sections if section in data]
        
        if len(present_sections) == 0:
            logger.error("No expected sections found in data")
            return False
        
        logger.info(f"Found {len(present_sections)} out of {len(self.data_sections)} expected sections")
        return True
    
    def preprocess_teaching_section(self, teaching_data: Any) -> Dict[str, Any]:
        """
        Convert various teaching section formats to template-compatible structure.
        
        Args:
            teaching_data: Raw teaching section data (can be dict or list)
            
        Returns:
            Processed teaching data in template-compatible format
        """
        # Handle case where teaching_data is a list (common in Farsi data)
        if isinstance(teaching_data, list):
            # Convert list format to expected dictionary format
            return {
                "title": "سوابق تدریس، راهبری و گواهینامه‌ها",
                "certifications_title": "گواهینامه‌های حرفه‌ای",
                "leadership_title": "راهبری تحقیقاتی",
                "positions": teaching_data,  # Use the list directly
                "certifications": [],
                "leadership": []
            }
        
        # Handle case where teaching_data is not a dict
        if not isinstance(teaching_data, dict):
            logger.warning(f"Unexpected teaching data type: {type(teaching_data)}")
            return {
                "title": "سوابق تدریس، راهبری و گواهینامه‌ها",
                "certifications_title": "گواهینامه‌های حرفه‌ای", 
                "leadership_title": "راهبری تحقیقاتی",
                "positions": [],
                "certifications": [],
                "leadership": []
            }
        
        # Default structure expected by template
        output_data = {
            "title": teaching_data.get("title", "سوابق تدریس، راهبری و گواهینامه‌ها"),
            "certifications_title": "گواهینامه‌های حرفه‌ای",
            "leadership_title": "راهبری تحقیقاتی",
            "positions": [],
            "certifications": [],
            "leadership": []
        }

        # Case 1: Simple 'items' list format
        if 'items' in teaching_data and isinstance(teaching_data.get('items'), list):
            for item_string in teaching_data['items']:
                # Parse string to separate description from date/year
                parts = item_string.rsplit('(', 1)
                description = parts[0].strip() if len(parts) > 1 else item_string
                date_or_year = parts[1].replace(')', '').replace('.', '').strip() if len(parts) > 1 else ""

                # Categorize based on keywords (Persian-specific)
                if "گواهینامه" in description:
                    output_data["certifications"].append({
                        "year": date_or_year, 
                        "name": description
                    })
                elif "راهبر" in description:
                    output_data["leadership"].append({
                        "year": date_or_year, 
                        "description": description
                    })
                else:  # Default to teaching position
                    output_data["positions"].append({
                        "dates": date_or_year, 
                        "description": description
                    })
            
            return output_data

        # Case 2: Complex nested structure (from AI customization)
        if 'university_teaching' in teaching_data:
            output_data['positions'].extend(
                teaching_data.get('university_teaching', {}).get('positions', [])
            )
        
        if 'additional_teaching' in teaching_data:
            output_data['positions'].extend(
                teaching_data.get('additional_teaching', {}).get('positions', [])
            )
        
        if 'leadership' in teaching_data:
            output_data['leadership'].extend(
                teaching_data.get('leadership', {}).get('positions', [])
            )
        
        if 'certifications' in teaching_data:
            output_data['certifications'].extend(
                teaching_data.get('certifications', {}).get('items', [])
            )
        
        return output_data
    
    def preprocess_data(self, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess entire CV data dictionary for template compatibility.
        
        Args:
            cv_data: Raw CV data dictionary
            
        Returns:
            Processed CV data ready for template rendering
        """
        # Create deep copy to avoid modifying original
        processed_data = json.loads(json.dumps(cv_data))
        
        # Check each section and handle lists/unexpected formats
        for section in self.data_sections:
            if section in processed_data:
                section_data = processed_data[section]
                
                # Special handling for teaching section
                if section == 'teaching':
                    processed_data['teaching'] = self.preprocess_teaching_section(section_data)
                
                # Handle other sections that might be lists instead of dicts
                elif isinstance(section_data, list):
                    logger.warning(f"Section '{section}' is a list, wrapping in dict")
                    processed_data[section] = {
                        'items': section_data
                    }
        
        logger.info("Data preprocessing completed")
        return processed_data
    
    def get_missing_sections(self, data: Dict[str, Any]) -> List[str]:
        """
        Get list of expected sections that are missing from the data.
        
        Args:
            data: CV data dictionary
            
        Returns:
            List of missing section names
        """
        return [section for section in self.data_sections if section not in data]