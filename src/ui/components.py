# import base64
# import os
# from typing import Dict, Any, Optional, List
# from pathlib import Path
# import streamlit as st

# from config.settings import settings
# from src.utils.logger import setup_logger

# logger = setup_logger(__name__)


# class UIComponents:
#     """Collection of reusable UI components for the CV Generator app."""
    
#     @staticmethod
#     def display_file_status() -> Dict[str, bool]:
#         """
#         Display file status in sidebar and return status dictionary.
#         Checks for profile.jpg and a fallback default_profile_pic.jpg.
        
#         Returns:
#             Dictionary with file existence status
#         """
#         st.subheader("📁 File Status")
        
#         file_status = {}
        
#         # Template file
#         template_exists = os.path.exists(settings.TEMPLATE_FILE)
#         file_status['template'] = template_exists
#         st.write(f"{'✅' if template_exists else '❌'} {settings.TEMPLATE_FILE}")
        
#         # Data directory
#         data_dir_exists = os.path.isdir(settings.DATA_DIRECTORY)
#         file_status['data_dir'] = data_dir_exists
#         st.write(f"{'✅' if data_dir_exists else '❌'} {settings.DATA_DIRECTORY}/ directory")
        
#         # Profile image (optional)
#         assets_dir = Path(settings.PROJECT_ROOT) / 'assets'
#         primary_pic_path = assets_dir / 'profile.jpg'
#         default_pic_path = assets_dir / 'default_profile_pic.jpg'
        
#         profile_exists = primary_pic_path.exists() or default_pic_path.exists()
#         file_status['profile'] = profile_exists
        
#         # Display a more informative message
#         if primary_pic_path.exists():
#             st.write(f"✅ {primary_pic_path.name} (Primary)")
#         elif default_pic_path.exists():
#             st.write(f"✅ {default_pic_path.name} (Default)")
#         else:
#             st.write("⚠️ No profile picture found")

#         # Environment file
#         env_exists = os.path.exists('.env')
#         file_status['env'] = env_exists
#         st.write(f"{'✅' if env_exists else '❌'} .env file")
        
#         return file_status
    
#     @staticmethod
#     def display_data_files_status(lang_choice: str):
#         """
#         Display status of individual JSON data files.
        
#         Args:
#             lang_choice: Selected language code
#         """
#         if not os.path.isdir(settings.DATA_DIRECTORY):
#             return
            
#         st.subheader("Data Files (from directory)")
        
#         for section in settings.CV_SECTIONS:
#             filename = f"{section}_{lang_choice}.json"
#             file_path = os.path.join(settings.DATA_DIRECTORY, filename)
#             file_exists = os.path.exists(file_path)
#             st.write(f"{'✅' if file_exists else '❌'} {filename}")
    
#     @staticmethod
#     def create_sidebar_config() -> tuple:
#         """
#         Create sidebar configuration section.
        
#         Returns:
#             Tuple of (language_choice, uploaded_file, mode)
#         """
#         with st.sidebar:
#             st.header("⚙️ Configuration")
            
#             # Language selection
#             lang_choice = st.selectbox(
#                 "Choose Language",
#                 options=settings.SUPPORTED_LANGUAGES,
#                 format_func=lambda x: settings.get_language_display_name(x),
#                 index=0
#             )
            
#             st.header("📂 Data Source")
#             uploaded_file = st.file_uploader(
#                 "Load Comprehensive JSON",
#                 type=['json'],
#                 help="Upload a single JSON file containing all CV data."
#             )
            
#             st.header("🚀 Generation Mode")
#             mode = st.radio(
#                 "Select Mode",
#                 options=["Standard", "AI-Customized"],
#                 help="Standard: Use data as-is. AI-Customized: Tailor CV to a job description."
#             )
            
#             # File status display
#             UIComponents.display_file_status()
            
#             # Data files status (only if not uploading)
#             if not uploaded_file:
#                 st.info("Using data from `data/` directory. Upload a file to override.")
#                 UIComponents.display_data_files_status(lang_choice)
            
#             return lang_choice, uploaded_file, mode
    
#     @staticmethod
#     def display_analysis_results(result: Dict[str, Any]):
#         """
#         Display AI analysis results in a structured format.
        
#         Args:
#             result: Analysis result dictionary from AI agent
#         """
#         st.subheader("Job Analysis Breakdown")
#         analysis = result.get('analysis', {})
        
#         # Key requirements
#         st.markdown("**Key Job Requirements:**")
#         for req in analysis.get('key_requirements', []):
#             st.write(f"• {req}")
        
#         # Matching skills
#         st.markdown("**Your Matching Skills:**")
#         for skill in analysis.get('matching_skills', []):
#             st.write(f"✅ {skill}")
        
#         # Identified gaps
#         st.markdown("**Identified Gaps:**")
#         for gap in analysis.get('gaps_identified', []):
#             st.write(f"⚠️ {gap}")
        
#         # Optimization strategy
#         st.markdown("**AI's Optimization Strategy:**")
#         st.info(analysis.get('optimization_strategy', 'No strategy provided.'))
    
#     @staticmethod
#     def display_reasoning_details(result: Dict[str, Any]):
#         """
#         Display AI reasoning chain of thought.
        
#         Args:
#             result: Analysis result dictionary from AI agent
#         """
#         st.subheader("AI's Chain of Thought")
#         reasoning = result.get('reasoning', {})
        
#         reasoning_sections = [
#             ('Summary Changes', 'summary_changes'),
#             ('Skills Prioritization', 'skills_prioritization'),
#             ('Experience Highlighting', 'experience_highlighting'),
#             ('Projects Selection', 'projects_selection'),
#             ('Overall Strategy', 'overall_strategy')
#         ]
        
#         for title, key in reasoning_sections:
#             with st.expander(title):
#                 st.write(reasoning.get(key, f'No {title.lower()} explained.'))
    
#     @staticmethod
#     def display_pdf_preview(pdf_bytes: bytes, height: int = 800):
#         """
#         Display PDF preview in an iframe.
        
#         Args:
#             pdf_bytes: PDF content as bytes
#             height: Height of the iframe in pixels
#         """
#         try:
#             b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
#             pdf_display = f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="{height}" type="application/pdf"></iframe>'
#             st.markdown(pdf_display, unsafe_allow_html=True)
#         except Exception as e:
#             st.error(f"Cannot display PDF preview: {e}")
#             logger.error(f"PDF preview error: {e}")
    
#     @staticmethod
#     def create_download_section(pdf_bytes: bytes, filename: str, 
#                               customized_data: Optional[Dict[str, Any]] = None,
#                               lang_choice: str = 'en'):
#         """
#         Create download section with PDF and optional JSON download.
        
#         Args:
#             pdf_bytes: Generated PDF as bytes
#             filename: Filename for the PDF download
#             customized_data: Optional customized CV data for JSON download
#             lang_choice: Language code for JSON filename
#         """
#         col1, col2 = st.columns([3, 1])
        
#         with col1:
#             # Display PDF info
#             pdf_size_mb = len(pdf_bytes) / (1024 * 1024)
#             st.info(f"📊 PDF size: {pdf_size_mb:.2f} MB")
            
#             if pdf_size_mb > settings.PDF_MAX_SIZE_MB:
#                 st.warning(f"PDF is larger than recommended size ({settings.PDF_MAX_SIZE_MB} MB)")
        
#         with col2:
#             # PDF download button
#             st.download_button(
#                 label="📥 Download PDF",
#                 data=pdf_bytes,
#                 file_name=filename,
#                 mime="application/pdf",
#                 use_container_width=True
#             )
            
#             # JSON download button (for customized data)
#             if customized_data:
#                 import json
#                 customized_json = json.dumps(customized_data, indent=2, ensure_ascii=False)
#                 st.download_button(
#                     label="📄 Download Customized JSON",
#                     data=customized_json.encode('utf-8'),
#                     file_name=f"customized_cv_data_{lang_choice}.json",
#                     mime="application/json",
#                     use_container_width=True
#                 )
    
#     @staticmethod
#     def display_job_input() -> str:
#         """
#         Display job description input area.
        
#         Returns:
#             Job description text
#         """
#         return st.text_area(
#             "📋 Paste Job Description Here",
#             placeholder="Paste the complete job posting text here for AI analysis...",
#             height=250,
#             help="Enter the full job description for AI to analyze and customize your CV accordingly."
#         )
    
#     @staticmethod
#     def display_loading_state(message: str = "Processing..."):
#         """
#         Display loading spinner with custom message.
        
#         Args:
#             message: Loading message to display
#         """
#         return st.spinner(message)
    
#     @staticmethod
#     def display_success_message(message: str, details: Optional[Dict[str, Any]] = None):
#         """
#         Display success message with optional details.
        
#         Args:
#             message: Success message
#             details: Optional details to show in expander
#         """
#         st.success(message)
        
#         if details:
#             with st.expander("View Details"):
#                 st.json(details)
    
#     @staticmethod
#     def display_error_message(error: Exception, show_traceback: bool = False):
#         """
#         Display error message with optional traceback.
        
#         Args:
#             error: Exception object
#             show_traceback: Whether to show full traceback
#         """
#         st.error(f"❌ Error: {str(error)}")
        
#         if show_traceback:
#             import traceback
#             with st.expander("Full Error Details"):
#                 st.code(traceback.format_exc())
    
#     @staticmethod
#     def display_warning_message(message: str, items: Optional[List[str]] = None):
#         """
#         Display warning message with optional item list.
        
#         Args:
#             message: Warning message
#             items: Optional list of items to display
#         """
#         st.warning(message)
        
#         if items:
#             for item in items:
#                 st.write(f"• {item}")
    
#     @staticmethod
#     def create_tabs_layout(has_analysis: bool = False) -> tuple:
#         """
#         Create tab layout based on whether AI analysis is available.
        
#         Args:
#             has_analysis: Whether to include analysis tabs
            
#         Returns:
#             Tuple of tab objects
#         """
#         if has_analysis:
#             return st.tabs(["📄 Generated PDF", "🔍 AI Analysis", "🧠 AI Reasoning"])
#         else:
#             return (st.tabs(["📄 Generated PDF"])[0],)

import base64
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
import streamlit as st

from config.settings import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class UIComponents:
    """Collection of reusable UI components for the CV Generator app."""
    
    @staticmethod
    def display_file_status() -> Dict[str, bool]:
        """
        Display file status in sidebar and return status dictionary.
        Checks for profile.jpg and a fallback default_profile_pic.jpg.
        
        Returns:
            Dictionary with file existence status
        """
        st.subheader("📁 File Status")
        
        file_status = {}
        
        # Template file
        template_exists = os.path.exists(settings.TEMPLATE_FILE)
        file_status['template'] = template_exists
        st.write(f"{'✅' if template_exists else '❌'} {settings.TEMPLATE_FILE}")
        
        # Data directory
        data_dir_exists = os.path.isdir(settings.DATA_DIRECTORY)
        file_status['data_dir'] = data_dir_exists
        st.write(f"{'✅' if data_dir_exists else '❌'} {settings.DATA_DIRECTORY}/ directory")
        
        # Profile image (optional)
        assets_dir = Path(settings.PROJECT_ROOT) / 'assets'
        primary_pic_path = assets_dir / 'profile.jpg'
        default_pic_path = assets_dir / 'default_profile_pic.jpg'
        
        profile_exists = primary_pic_path.exists() or default_pic_path.exists()
        file_status['profile'] = profile_exists
        
        # Display a more informative message
        if primary_pic_path.exists():
            st.write(f"✅ {primary_pic_path.name} (Primary)")
        elif default_pic_path.exists():
            st.write(f"✅ {default_pic_path.name} (Default)")
        else:
            st.write("⚠️ No profile picture found")

        # Environment file
        env_exists = os.path.exists('.env')
        file_status['env'] = env_exists
        st.write(f"{'✅' if env_exists else '❌'} .env file")
        
        return file_status
    
    @staticmethod
    def display_data_files_status(lang_choice: str):
        """
        Display status of individual JSON data files.
        
        Args:
            lang_choice: Selected language code
        """
        if not os.path.isdir(settings.DATA_DIRECTORY):
            return
            
        st.subheader("Data Files (from directory)")
        
        for section in settings.CV_SECTIONS:
            filename = f"{section}_{lang_choice}.json"
            file_path = os.path.join(settings.DATA_DIRECTORY, filename)
            file_exists = os.path.exists(file_path)
            st.write(f"{'✅' if file_exists else '❌'} {filename}")
    
    @staticmethod
    def create_sidebar_config() -> tuple:
        """
        Create sidebar configuration section.
        
        Returns:
            Tuple of (language_choice, uploaded_file, mode)
        """
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            # Language selection
            lang_choice = st.selectbox(
                "Choose Language",
                options=settings.SUPPORTED_LANGUAGES,
                format_func=lambda x: settings.get_language_display_name(x),
                index=0
            )
            
            st.header("📂 Data Source")
            uploaded_file = st.file_uploader(
                "Load Comprehensive JSON",
                type=['json'],
                help="Upload a single JSON file containing all CV data."
            )
            
            st.header("🚀 Generation Mode")
            mode = st.radio(
                "Select Mode",
                options=["Standard", "AI-Customized"],
                help="Standard: Use data as-is. AI-Customized: Tailor CV to a job description."
            )
            
            # File status display
            UIComponents.display_file_status()
            
            # Data files status (only if not uploading)
            if not uploaded_file:
                st.info("Using data from `data/` directory. Upload a file to override.")
                UIComponents.display_data_files_status(lang_choice)
            
            return lang_choice, uploaded_file, mode
    
    @staticmethod
    def display_analysis_results(result: Dict[str, Any]):
        """
        Display AI analysis results in a structured format.
        
        Args:
            result: Analysis result dictionary from AI agent
        """
        st.subheader("Job Analysis Breakdown")
        analysis = result.get('analysis', {})
        
        # Key requirements
        st.markdown("**Key Job Requirements:**")
        for req in analysis.get('key_requirements', []):
            st.write(f"• {req}")
        
        # Matching skills
        st.markdown("**Your Matching Skills:**")
        for skill in analysis.get('matching_skills', []):
            st.write(f"✅ {skill}")
        
        # Identified gaps
        st.markdown("**Identified Gaps:**")
        for gap in analysis.get('gaps_identified', []):
            st.write(f"⚠️ {gap}")
        
        # Optimization strategy
        st.markdown("**AI's Optimization Strategy:**")
        st.info(analysis.get('optimization_strategy', 'No strategy provided.'))
    
    @staticmethod
    def display_reasoning_details(result: Dict[str, Any]):
        """
        Display AI reasoning chain of thought.
        
        Args:
            result: Analysis result dictionary from AI agent
        """
        st.subheader("AI's Chain of Thought")
        reasoning = result.get('reasoning', {})
        
        reasoning_sections = [
            ('Summary Changes', 'summary_changes'),
            ('Skills Prioritization', 'skills_prioritization'),
            ('Experience Highlighting', 'experience_highlighting'),
            ('Projects Selection', 'projects_selection'),
            ('Overall Strategy', 'overall_strategy')
        ]
        
        for title, key in reasoning_sections:
            with st.expander(title):
                st.write(reasoning.get(key, f'No {title.lower()} explained.'))
    
    @staticmethod
    def display_pdf_preview(pdf_bytes: bytes, height: int = 800):
        """
        Display PDF preview in an iframe.
        
        Args:
            pdf_bytes: PDF content as bytes
            height: Height of the iframe in pixels
        """
        try:
            b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="{height}" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Cannot display PDF preview: {e}")
            logger.error(f"PDF preview error: {e}")
    
    @staticmethod
    def create_download_section(pdf_bytes: bytes, filename: str, 
                              customized_data: Optional[Dict[str, Any]] = None,
                              lang_choice: str = 'en'):
        """
        Create download section with PDF and optional JSON download.
        
        Args:
            pdf_bytes: Generated PDF as bytes
            filename: Filename for the PDF download
            customized_data: Optional customized CV data for JSON download
            lang_choice: Language code for JSON filename
        """
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Display PDF info
            pdf_size_mb = len(pdf_bytes) / (1024 * 1024)
            st.info(f"📊 PDF size: {pdf_size_mb:.2f} MB")
            
            if pdf_size_mb > settings.PDF_MAX_SIZE_MB:
                st.warning(f"PDF is larger than recommended size ({settings.PDF_MAX_SIZE_MB} MB)")
        
        with col2:
            # PDF download button
            st.download_button(
                label="📥 Download PDF",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True
            )
            
            # JSON download button (for customized data)
            if customized_data:
                import json
                customized_json = json.dumps(customized_data, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📄 Download Customized JSON",
                    data=customized_json.encode('utf-8'),
                    file_name=f"customized_cv_data_{lang_choice}.json",
                    mime="application/json",
                    use_container_width=True
                )
    
    @staticmethod
    def display_job_input() -> str:
        """
        Display job description input area.
        
        Returns:
            Job description text
        """
        return st.text_area(
            "📋 Paste Job Description Here",
            placeholder="Paste the complete job posting text here for AI analysis...",
            height=250,
            help="Enter the full job description for AI to analyze and customize your CV accordingly."
        )
    
    @staticmethod
    def display_loading_state(message: str = "Processing..."):
        """
        Display loading spinner with custom message.
        
        Args:
            message: Loading message to display
        """
        return st.spinner(message)
    
    @staticmethod
    def display_success_message(message: str, details: Optional[Dict[str, Any]] = None):
        """
        Display success message with optional details.
        
        Args:
            message: Success message
            details: Optional details to show in expander
        """
        st.success(message)
        
        if details:
            with st.expander("View Details"):
                st.json(details)
    
    @staticmethod
    def display_error_message(error: Exception, show_traceback: bool = False):
        """
        Display error message with optional traceback.
        
        Args:
            error: Exception object
            show_traceback: Whether to show full traceback
        """
        st.error(f"❌ Error: {str(error)}")
        
        if show_traceback:
            import traceback
            with st.expander("Full Error Details"):
                st.code(traceback.format_exc())
    
    @staticmethod
    def display_warning_message(message: str, items: Optional[List[str]] = None):
        """
        Display warning message with optional item list.
        
        Args:
            message: Warning message
            items: Optional list of items to display
        """
        st.warning(message)
        
        if items:
            for item in items:
                st.write(f"• {item}")
    
    @staticmethod
    def create_tabs_layout(has_analysis: bool = False) -> tuple:
        """
        Create tab layout based on whether AI analysis is available.
        
        Args:
            has_analysis: Whether to include analysis tabs
            
        Returns:
            Tuple of tab objects
        """
        if has_analysis:
            return st.tabs(["📄 Generated PDF", "🔍 AI Analysis", "🧠 AI Reasoning", "✏️ Edit Customized JSON"])
        else:
            # Return a tuple which can be unpacked as a single item
            return (st.tabs(["📄 Generated PDF"])[0],)

