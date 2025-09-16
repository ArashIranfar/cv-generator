import os
from typing import Dict, Any, Optional
import base64
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from config.settings import settings
from src.core.data_processor import DataProcessor
from src.utils.exceptions import TemplateNotFoundError, PDFGenerationError
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class CVGenerator:
    """
    Generates CV PDFs from JSON data using HTML templates and WeasyPrint.
    Supports both English (LTR) and Farsi (RTL) languages.
    """

    def __init__(self, lang: str = 'en', template_path: str = None):
        """
        Initialize the CV Generator.

        Args:
            lang: Language code ('en' for English, 'fa' for Farsi)
            template_path: Path to template directory. Defaults to settings.TEMPLATE_FILE
            
        Raises:
            ValueError: If language is not supported
            TemplateNotFoundError: If template file cannot be loaded
        """
        if lang not in settings.SUPPORTED_LANGUAGES:
            raise ValueError(f"Language must be one of {settings.SUPPORTED_LANGUAGES}")
        
        self.lang = lang
        self.template_path = template_path or os.path.dirname(settings.TEMPLATE_FILE)
        self.template_name = os.path.basename(settings.TEMPLATE_FILE)
        
        # Initialize data processor for preprocessing
        self.data_processor = DataProcessor(lang=lang)
        
        # Set up Jinja2 template engine
        self._setup_template_engine()

    def _setup_template_engine(self):
        """Set up Jinja2 environment and load template."""
        try:
            self.env = Environment(loader=FileSystemLoader(self.template_path))
            self.template = self.env.get_template(self.template_name)
            logger.info(f"Template loaded successfully: {self.template_name}")
        except Exception as e:
            logger.error(f"Error loading template {self.template_name}: {e}")
            raise TemplateNotFoundError(f"Could not load template: {e}")

    def _get_profile_image_base64(self) -> str:
        """
        Load profile picture, with a fallback to a default image.
        Looks for 'profile.jpg' first, then 'default_profile_pic.jpg'.
        """
        assets_dir = Path(settings.PROJECT_ROOT) / 'assets'
        primary_pic_path = assets_dir / 'profile.jpg'
        default_pic_path = assets_dir / 'default_profile_pic.jpg'

        image_path_to_load = None
        if primary_pic_path.exists():
            image_path_to_load = primary_pic_path
            logger.info(f"Found primary profile picture: {primary_pic_path}")
        elif default_pic_path.exists():
            image_path_to_load = default_pic_path
            logger.info(f"Using default profile picture: {default_pic_path}")

        if image_path_to_load:
            try:
                with open(image_path_to_load, "rb") as img_file:
                    return base64.b64encode(img_file.read()).decode("utf-8")
            except Exception as e:
                logger.error(f"Could not read or encode image file {image_path_to_load}: {e}")
        
        logger.warning("No profile picture found (neither profile.jpg nor default_profile_pic.jpg).")
        return ""

    def generate_pdf_bytes(self, cv_data: Dict[str, Any]) -> Optional[bytes]:
        """
        Generate PDF from CV data and return as bytes.

        Args:
            cv_data: Complete CV data dictionary
            
        Returns:
            PDF content as bytes, or None if generation failed
            
        Raises:
            PDFGenerationError: If PDF generation fails
        """
        if not self.template:
            raise PDFGenerationError("Template not loaded")
        
        try:
            # Preprocess data for template compatibility
            processed_data = self.data_processor.preprocess_data(cv_data)
            logger.info("Data preprocessing completed")
            
            # Render HTML template
            profile_image = self._get_profile_image_base64()
            rendered_html = self.template.render(
                data=processed_data, 
                lang=self.lang,
                profile_image=profile_image
            )
            logger.info("HTML template rendered successfully")
            
            # Generate PDF using WeasyPrint
            base_url = os.path.dirname(os.path.realpath(__file__))
            pdf_bytes = HTML(string=rendered_html, base_url=base_url).write_pdf()
            
            # Validate PDF size
            pdf_size_mb = len(pdf_bytes) / (1024 * 1024)
            if pdf_size_mb > settings.PDF_MAX_SIZE_MB:
                logger.warning(f"Generated PDF is large: {pdf_size_mb:.2f} MB")
            
            logger.info(f"PDF generated successfully ({pdf_size_mb:.2f} MB)")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            raise PDFGenerationError(f"PDF generation failed: {e}")

    def validate_template(self) -> bool:
        """
        Validate that the template can be loaded and rendered.
        
        Returns:
            True if template is valid, False otherwise
        """
        try:
            # Try to render with minimal data
            test_data = {section: {} for section in settings.CV_SECTIONS}
            self.template.render(data=test_data, lang=self.lang)
            return True
        except Exception as e:
            logger.error(f"Template validation failed: {e}")
            return False

    def get_template_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded template.
        
        Returns:
            Dictionary with template information
        """
        template_file_path = os.path.join(self.template_path, self.template_name)
        
        info = {
            'template_name': self.template_name,
            'template_path': self.template_path,
            'full_path': template_file_path,
            'exists': os.path.exists(template_file_path),
            'language': self.lang,
            'is_loaded': self.template is not None
        }
        
        if info['exists']:
            try:
                stat = os.stat(template_file_path)
                info['size_bytes'] = stat.st_size
                info['modified_time'] = stat.st_mtime
            except OSError:
                pass
        
        return info

    def render_html_preview(self, cv_data: Dict[str, Any]) -> str:
        """
        Render HTML without converting to PDF (for debugging).
        
        Args:
            cv_data: Complete CV data dictionary
            
        Returns:
            Rendered HTML as string
        """
        if not self.template:
            raise TemplateNotFoundError("Template not loaded")
        
        try:
            processed_data = self.data_processor.preprocess_data(cv_data)
            return self.template.render(data=processed_data, lang=self.lang)
        except Exception as e:
            logger.error(f"Error rendering HTML preview: {e}")
            raise PDFGenerationError(f"HTML rendering failed: {e}")
