import os
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import streamlit as st
from dotenv import load_dotenv

print("1. Starting app execution.")
print(f"2. Current working directory: {os.getcwd()}")
print(f"3. Python executable being used: {sys.executable}")
print(f"4. Python path: {sys.path}")

# Load environment variables
print("5. Attempting to load environment variables...")
load_dotenv()
print("6. Environment variables loaded.")

from config.settings import settings
from src.ui.pages import MainPage, DebugPage
from src.utils.logger import setup_logger
from src.utils.exceptions import ConfigurationError

# Set up logging
logger = setup_logger(__name__)

def signal_handler(sig, frame):
    logger.info("SIGINT received, exiting gracefully.")
    st.info("Application is shutting down. Please wait...")
    sys.exit(0)

def main():
    """Main application entry point."""
    # Check dependencies before anything else
    check_dependencies()

    # Configure Streamlit page
    st.set_page_config(
        page_title=settings.PAGE_TITLE,
        page_icon=settings.PAGE_ICON,
        layout=settings.LAYOUT,
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/ArashIranfar/cv-generator',
            'Report a bug': 'https://github.com/ArashIranfar/cv-generator/issues',
            'About': f"""
            # AI-Powered CV Generator
            
            Generate customized CVs tailored to specific job descriptions using AI.
            
            **Version:** 1.0.0
            **Model:** {settings.OPENAI_MODEL}
            """
        }
    )
    
    # Initialize session state
    if 'app_initialized' not in st.session_state:
        initialize_session_state()
    
    # Validate configuration
    try:
        validate_configuration()
    except ConfigurationError as e:
        st.error(f"Configuration Error: {e}")
        st.info("Please check your .env file and ensure all required settings are configured.")
        return
    
    # Create navigation
    page = create_navigation()
    
    # Render selected page
    try:
        if page == "CV Generator":
            main_page = MainPage()
            main_page.render()
        elif page == "Debug":
            debug_page = DebugPage()
            debug_page.render()
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error(f"An unexpected error occurred: {e}")
        with st.expander("Error Details"):
            import traceback
            st.code(traceback.format_exc())


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    # Clear any existing state on first load
    for key in list(st.session_state.keys()):
        if key not in ['app_initialized']:
            del st.session_state[key]
    
    # Set initialization flag
    st.session_state.app_initialized = True
    
    logger.info("Session state initialized")


def validate_configuration():
    """Validate application configuration."""
    if not settings.validate():
        missing_items = []
        
        if not settings.OPENAI_API_KEY:
            missing_items.append("OpenAI API key (OPENAI_API_KEY)")
        
        if settings.DEFAULT_LANGUAGE not in settings.SUPPORTED_LANGUAGES:
            missing_items.append(f"Valid default language (got {settings.DEFAULT_LANGUAGE})")
        
        raise ConfigurationError(f"Missing required configuration: {', '.join(missing_items)}")
    
    logger.info("Configuration validation passed")


def create_navigation():
    """Create navigation sidebar."""
    with st.sidebar:
        st.markdown("---")
        st.subheader("Navigation")
        
        pages = ["CV Generator"]
        
        # Add debug page in development mode
        if os.getenv("DEBUG", "false").lower() == "true":
            pages.append("Debug")
        
        page = st.radio("Select Page", pages, index=0)
        
        # Application info
        st.markdown("---")
        st.markdown(f"""
        **Version:** 1.0.0  
        **Model:** {settings.OPENAI_MODEL}  
        **Languages:** {', '.join(settings.SUPPORTED_LANGUAGES)}
        """)
        
        return page


def check_dependencies():
    """Check if all required dependencies are available."""
    required_modules = [
        'streamlit',
        'jinja2', 
        'weasyprint',
        'langchain_openai',
        'dotenv'
    ]
    
    missing_modules = []

    print("7. Checking for dependencies...")
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        st.error(
            f"Missing required dependencies: {', '.join(missing_modules)}. "
            "Please install them using pip."
        )
        st.stop()
    else:
        print("8. All dependencies found.")


if __name__ == "__main__":
    main()