# import json
# from typing import Dict, Any, Optional

# import streamlit as st

# from config.settings import settings
# from src.core.cv_generator import CVGenerator
# from src.core.ai_agent import CVAgent
# from src.core.data_processor import DataProcessor
# from src.ui.components import UIComponents
# from src.utils.exceptions import CVGeneratorException
# from src.utils.logger import setup_logger

# logger = setup_logger(__name__)


# class MainPage:
#     """Main page controller for the CV Generator application."""
    
#     def __init__(self):
#         """Initialize the main page."""
#         self.ui = UIComponents()
    
#     def render(self):
#         """Render the complete main page."""
#         # Page header
#         st.title("🤖 AI-Powered CV Generator")
#         st.markdown("Generate standard or AI-tailored CVs from your data.")
        
#         # Check prerequisites
#         if not self._check_prerequisites():
#             return
        
#         # Create sidebar configuration
#         lang_choice, uploaded_file, mode = self.ui.create_sidebar_config()
        
#         # --- State Invalidation Logic ---
#         # Check if settings have changed since the last PDF was generated
#         self._invalidate_stale_results(lang_choice, uploaded_file, mode)
#         # ------------------------------------

#         # Load CV data
#         cv_data = self._load_cv_data(lang_choice, uploaded_file)
#         if not cv_data:
#             st.warning("⚠️ No CV data loaded. Upload a JSON file or ensure the `data/` directory is correctly set up.")
#             st.stop()
        
#         # Render based on mode
#         if mode == "Standard":
#             self._render_standard_mode(lang_choice, cv_data, uploaded_file)
#         elif mode == "AI-Customized":
#             self._render_ai_mode(lang_choice, cv_data, uploaded_file)
        
#         # Display results if available
#         self._render_results()
        
#         # Instructions section
#         self._render_instructions()
    
#     def _check_prerequisites(self) -> bool:
#         """Check if essential prerequisites are met."""
#         if not settings.OPENAI_API_KEY:
#             st.error("❌ OpenAI API key not found. Please create a `.env` file with `OPENAI_API_KEY=your_key_here`")
#             return False
#         return True

#     def _invalidate_stale_results(self, lang_choice: str, uploaded_file, mode: str):
#         """Clear previous results if the configuration has changed."""
#         # Create a unique identifier for the current configuration
#         file_id = uploaded_file.file_id if uploaded_file else None
#         current_config = (lang_choice, file_id, mode)

#         # Get the config from the last generation, if it exists
#         last_config = st.session_state.get('last_generation_config')

#         # If the config has changed, clear out the old results
#         if last_config and last_config != current_config:
#             logger.info("Configuration changed. Clearing previous results.")
#             for key in ['pdf_bytes', 'filename', 'analysis_result', 'customized_data', 'last_generation_config']:
#                 if key in st.session_state:
#                     del st.session_state[key]

#     def _load_cv_data(self, lang_choice: str, uploaded_file) -> Dict[str, Any]:
#         """Load CV data from file or directory."""
#         try:
#             data_processor = DataProcessor(lang=lang_choice)
            
#             if uploaded_file:
#                 return data_processor.load_from_file(uploaded_file.getvalue())
#             else:
#                 return data_processor.load_data_from_directory()
                
#         except Exception as e:
#             self.ui.display_error_message(e)
#             return {}
    
#     def _render_standard_mode(self, lang_choice: str, cv_data: Dict[str, Any], uploaded_file):
#         """Render the standard CV generation mode."""
#         st.header("📄 Standard CV Generation")
        
#         with st.expander("View Loaded Data"):
#             st.json(cv_data)
        
#         if st.button("🚀 Generate Standard CV", type="primary", use_container_width=True):
#             self._generate_standard_cv(lang_choice, cv_data, uploaded_file)
    
#     def _render_ai_mode(self, lang_choice: str, cv_data: Dict[str, Any], uploaded_file):
#         """Render the AI-customized CV generation mode."""
#         st.header("🎯 Job-Tailored CV Generation")
        
#         job_description = self.ui.display_job_input()
        
#         if st.button("🤖 Generate AI-Customized CV", type="primary", use_container_width=True):
#             if not job_description.strip():
#                 st.info("👆 Please enter a job description for AI customization.")
#             else:
#                 self._generate_ai_customized_cv(lang_choice, cv_data, job_description, uploaded_file)
    
#     def _generate_standard_cv(self, lang_choice: str, cv_data: Dict[str, Any], uploaded_file):
#         """Generate standard CV without AI customization."""
#         try:
#             generator = CVGenerator(lang=lang_choice)
            
#             with self.ui.display_loading_state("Generating PDF..."):
#                 pdf_bytes = generator.generate_pdf_bytes(cv_data)
            
#             if pdf_bytes:
#                 st.success("✅ CV Generated Successfully!")
                
#                 st.session_state.pdf_bytes = pdf_bytes
#                 st.session_state.filename = f"CV_Standard_{lang_choice.upper()}.pdf"
#                 st.session_state.analysis_result = None
#                 st.session_state.customized_data = None
                
#                 # Store the configuration that produced this result
#                 file_id = uploaded_file.file_id if uploaded_file else None
#                 st.session_state.last_generation_config = (lang_choice, file_id, "Standard")
                
#             else:
#                 st.error("❌ Failed to generate PDF.")
                
#         except CVGeneratorException as e:
#             self.ui.display_error_message(e)
#         except Exception as e:
#             self.ui.display_error_message(e, show_traceback=True)
    
#     def _generate_ai_customized_cv(self, lang_choice: str, cv_data: Dict[str, Any], 
#                                  job_description: str, uploaded_file):
#         """Generate AI-customized CV based on job description."""
#         try:
#             agent = CVAgent()
            
#             with self.ui.display_loading_state("AI is analyzing job description and customizing your CV..."):
#                 result = agent.analyze_job_description(job_description, cv_data, lang_choice)
            
#             if result:
#                 st.success("✅ AI Analysis Complete!")
#                 customized_data = result['customized_data']
                
#                 generator = CVGenerator(lang=lang_choice)
                
#                 with self.ui.display_loading_state("Generating customized PDF..."):
#                     pdf_bytes = generator.generate_pdf_bytes(customized_data)
                
#                 if pdf_bytes:
#                     st.session_state.pdf_bytes = pdf_bytes
#                     st.session_state.filename = f"CV_Customized_{lang_choice.upper()}.pdf"
#                     st.session_state.analysis_result = result
#                     st.session_state.customized_data = customized_data

#                     # Store the configuration that produced this result
#                     file_id = uploaded_file.file_id if uploaded_file else None
#                     st.session_state.last_generation_config = (lang_choice, file_id, "AI-Customized")
                    
#                 else:
#                     st.error("❌ Failed to generate customized PDF.")
                    
#         except CVGeneratorException as e:
#             self.ui.display_error_message(e)
#         except Exception as e:
#             self.ui.display_error_message(e, show_traceback=True)
    
#     def _render_results(self):
#         """Render the results section if PDF is available."""
#         if 'pdf_bytes' not in st.session_state or not st.session_state.pdf_bytes:
#             return
        
#         st.header("🎉 Your CV is Ready!")
        
#         analysis_result = st.session_state.get('analysis_result')
        
#         if analysis_result:
#             tab1, tab2, tab3 = self.ui.create_tabs_layout(has_analysis=True)
#         else:
#             tab1, = self.ui.create_tabs_layout(has_analysis=False)
        
#         with tab1:
#             st.subheader("Preview & Download")
            
#             self.ui.create_download_section(
#                 pdf_bytes=st.session_state.pdf_bytes,
#                 filename=st.session_state.filename,
#                 customized_data=st.session_state.get('customized_data'),
#                 lang_choice=self._get_current_language()
#             )
            
#             self.ui.display_pdf_preview(st.session_state.pdf_bytes)
        
#         if analysis_result:
#             with tab2:
#                 self.ui.display_analysis_results(analysis_result)
            
#             with tab3:
#                 self.ui.display_reasoning_details(analysis_result)
    
#     def _render_instructions(self):
#         """Render the instructions section."""
#         with st.expander("📋 Instructions", expanded=False):
#             st.markdown(self._get_instructions_text())
    
#     def _get_current_language(self) -> str:
#         """Get current language from the last successful generation config."""
#         if 'last_generation_config' in st.session_state:
#             return st.session_state.last_generation_config[0]
#         return settings.DEFAULT_LANGUAGE
    
#     def _get_instructions_text(self) -> str:
#         """Get the instructions text."""
#         return """
# ### Setup Requirements:

# 1. **HTML Template**: Your CV template file (`templates/cv_template.html`)
# 2. **Data Directory**: Contains JSON files with your CV data (`data/`)
# 3. **Profile Image**: Your profile picture (`profile.jpg` or `default_profile_pic.jpg`) - Optional
# 4. **Environment File**: Contains your OpenAI API key (`.env`)

# ### Environment Setup:

# Create a `.env` file with:
# ```
# OPENAI_API_KEY=your_openai_api_key_here
# ```

# ### Required JSON Files in data/ directory:

# For English CV:
# - `personal_en.json` - Personal information
# - `summary_en.json` - Professional summary
# - `skills_en.json` - Skills and competencies
# - `experience_en.json` - Work experience
# - `projects_en.json` - Projects
# - `education_en.json` - Educational background
# - `publications_en.json` - Publications
# - `teaching_en.json` - Teaching experience

# For Farsi CV:
# - Same files but with `_fa.json` suffix

# ### How to Use:

# **Standard Mode:**
# 1. Select your preferred language
# 2. Upload a comprehensive JSON file OR use files from `data/` directory
# 3. Click "Generate Standard CV" to create your PDF

# **AI-Customized Mode:**
# 1. Select your preferred language
# 2. Upload/use your CV data
# 3. Paste a job description in the text area
# 4. Click "Generate AI-Customized CV"
# 5. Review the AI analysis and reasoning
# 6. Download your tailored CV

# ### AI Features:

# - **Job Analysis**: Identifies key requirements and matching skills
# - **Content Optimization**: Reorders and emphasizes relevant experience
# - **Keyword Integration**: Naturally incorporates job-relevant terms
# - **Truthful Customization**: Never fabricates information, only optimizes existing content
# - **Detailed Reasoning**: Shows complete chain of thought for all decisions

# ### File Structure:

# ```
# cv-generator/
# ├── app.py                  # Main application entry point
# ├── templates/
# │   └── cv_template.html    # HTML template for CV
# ├── data/
# │   ├── personal_en.json    # Your personal data
# │   ├── summary_en.json     # Professional summary
# │   └── ...                 # Other CV sections
# ├── .env                    # Environment variables
# └── assets/
#     ├── profile.jpg
#     └── default_profile_pic.jpg
# ```
# """


# class DebugPage:
#     """Debug page for development and troubleshooting."""
    
#     def __init__(self):
#         """Initialize the debug page."""
#         self.ui = UIComponents()
    
#     def render(self):
#         """Render the debug page."""
#         st.title("🔧 Debug Information")
        
#         # Configuration info
#         st.subheader("Configuration")
#         config_info = {
#             'OPENAI_MODEL': settings.OPENAI_MODEL,
#             'OPENAI_BASE_URL': settings.OPENAI_BASE_URL,
#             'SUPPORTED_LANGUAGES': settings.SUPPORTED_LANGUAGES,
#             'CV_SECTIONS': settings.CV_SECTIONS,
#             'TEMPLATE_FILE': settings.TEMPLATE_FILE,
#             'DATA_DIRECTORY': settings.DATA_DIRECTORY,
#             'API_KEY_CONFIGURED': bool(settings.OPENAI_API_KEY)
#         }
#         st.json(config_info)
        
#         # File system info
#         st.subheader("File System")
#         file_status = self.ui.display_file_status()
#         st.json(file_status)
        
#         # Session state
#         st.subheader("Session State")
#         st.json({k: v for k, v in st.session_state.items()})
        
#         # Test components
#         st.subheader("Component Tests")
#         if st.button("Test Error Display"):
#             try:
#                 raise ValueError("This is a test error")
#             except Exception as e:
#                 self.ui.display_error_message(e, show_traceback=True)

import json
from typing import Dict, Any, Optional

import streamlit as st

from config.settings import settings
from src.core.cv_generator import CVGenerator
from src.core.ai_agent import CVAgent
from src.core.data_processor import DataProcessor
from src.ui.components import UIComponents
from src.utils.exceptions import CVGeneratorException, DataValidationError
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class MainPage:
    """Main page controller for the CV Generator application."""
    
    def __init__(self):
        """Initialize the main page."""
        self.ui = UIComponents()
    
    def render(self):
        """Render the complete main page."""
        # Page header
        st.title("🤖 AI-Powered CV Generator")
        st.markdown("Generate standard or AI-tailored CVs from your data.")
        
        # Check prerequisites
        if not self._check_prerequisites():
            return
        
        # Create sidebar configuration
        lang_choice, uploaded_file, mode = self.ui.create_sidebar_config()
        
        # --- State Invalidation Logic ---
        self._invalidate_stale_results(lang_choice, uploaded_file, mode)
        # ------------------------------------

        # Load CV data
        cv_data = self._load_cv_data(lang_choice, uploaded_file)
        if not cv_data:
            st.warning("⚠️ No CV data loaded. Upload a JSON file or ensure the `data/` directory is correctly set up.")
            st.stop()
        
        # Render based on mode
        if mode == "Standard":
            self._render_standard_mode(lang_choice, cv_data, uploaded_file)
        elif mode == "AI-Customized":
            self._render_ai_mode(lang_choice, cv_data, uploaded_file)
        
        # Display results if available
        self._render_results()
        
        # Instructions section
        self._render_instructions()
    
    def _check_prerequisites(self) -> bool:
        """Check if essential prerequisites are met."""
        if not settings.OPENAI_API_KEY:
            st.error("❌ OpenAI API key not found. Please create a `.env` file with `OPENAI_API_KEY=your_key_here`")
            return False
        return True

    def _invalidate_stale_results(self, lang_choice: str, uploaded_file, mode: str):
        """Clear previous results if the configuration has changed."""
        file_id = uploaded_file.file_id if uploaded_file else None
        current_config = (lang_choice, file_id, mode)

        last_config = st.session_state.get('last_generation_config')

        if last_config and last_config != current_config:
            logger.info("Configuration changed. Clearing previous results.")
            for key in ['pdf_bytes', 'filename', 'analysis_result', 'customized_data', 'last_generation_config']:
                if key in st.session_state:
                    del st.session_state[key]

    def _load_cv_data(self, lang_choice: str, uploaded_file) -> Dict[str, Any]:
        """Load CV data from file or directory."""
        try:
            data_processor = DataProcessor(lang=lang_choice)
            
            if uploaded_file:
                return data_processor.load_from_file(uploaded_file.getvalue())
            else:
                return data_processor.load_data_from_directory()
                
        except Exception as e:
            self.ui.display_error_message(e)
            return {}
    
    def _render_standard_mode(self, lang_choice: str, cv_data: Dict[str, Any], uploaded_file):
        """Render the standard CV generation mode."""
        st.header("📄 Standard CV Generation")
        
        with st.expander("View Loaded Data"):
            st.json(cv_data)
        
        if st.button("🚀 Generate Standard CV", type="primary", use_container_width=True):
            self._generate_standard_cv(lang_choice, cv_data, uploaded_file)
    
    def _render_ai_mode(self, lang_choice: str, cv_data: Dict[str, Any], uploaded_file):
        """Render the AI-customized CV generation mode."""
        st.header("🎯 Job-Tailored CV Generation")
        
        job_description = self.ui.display_job_input()
        
        if st.button("🤖 Generate AI-Customized CV", type="primary", use_container_width=True):
            if not job_description.strip():
                st.info("👆 Please enter a job description for AI customization.")
            else:
                self._generate_ai_customized_cv(lang_choice, cv_data, job_description, uploaded_file)
    
    def _generate_standard_cv(self, lang_choice: str, cv_data: Dict[str, Any], uploaded_file):
        """Generate standard CV without AI customization."""
        try:
            generator = CVGenerator(lang=lang_choice)
            
            with self.ui.display_loading_state("Generating PDF..."):
                pdf_bytes = generator.generate_pdf_bytes(cv_data)
            
            if pdf_bytes:
                st.success("✅ CV Generated Successfully!")
                
                st.session_state.pdf_bytes = pdf_bytes
                st.session_state.filename = f"CV_Standard_{lang_choice.upper()}.pdf"
                st.session_state.analysis_result = None
                st.session_state.customized_data = None
                
                file_id = uploaded_file.file_id if uploaded_file else None
                st.session_state.last_generation_config = (lang_choice, file_id, "Standard")
                
            else:
                st.error("❌ Failed to generate PDF.")
                
        except CVGeneratorException as e:
            self.ui.display_error_message(e)
        except Exception as e:
            self.ui.display_error_message(e, show_traceback=True)
    
    def _generate_ai_customized_cv(self, lang_choice: str, cv_data: Dict[str, Any], 
                                 job_description: str, uploaded_file):
        """Generate AI-customized CV based on job description."""
        try:
            agent = CVAgent()
            
            with self.ui.display_loading_state("AI is analyzing job description and customizing your CV..."):
                result = agent.analyze_job_description(job_description, cv_data, lang_choice)
            
            if result:
                st.success("✅ AI Analysis Complete!")
                customized_data = result['customized_data']
                
                generator = CVGenerator(lang=lang_choice)
                
                with self.ui.display_loading_state("Generating customized PDF..."):
                    pdf_bytes = generator.generate_pdf_bytes(customized_data)
                
                if pdf_bytes:
                    st.session_state.pdf_bytes = pdf_bytes
                    st.session_state.filename = f"CV_Customized_{lang_choice.upper()}.pdf"
                    st.session_state.analysis_result = result
                    st.session_state.customized_data = customized_data

                    file_id = uploaded_file.file_id if uploaded_file else None
                    st.session_state.last_generation_config = (lang_choice, file_id, "AI-Customized")
                    
                else:
                    st.error("❌ Failed to generate customized PDF.")
                    
        except CVGeneratorException as e:
            self.ui.display_error_message(e)
        except Exception as e:
            self.ui.display_error_message(e, show_traceback=True)
    
    def _render_results(self):
        """Render the results section if PDF is available."""
        if 'pdf_bytes' not in st.session_state or not st.session_state.pdf_bytes:
            return
        
        st.header("🎉 Your CV is Ready!")
        
        analysis_result = st.session_state.get('analysis_result')
        
        if analysis_result:
            tab1, tab2, tab3, tab4 = self.ui.create_tabs_layout(has_analysis=True)
        else:
            tab1, = self.ui.create_tabs_layout(has_analysis=False)
        
        with tab1:
            st.subheader("Preview & Download")
            
            self.ui.create_download_section(
                pdf_bytes=st.session_state.pdf_bytes,
                filename=st.session_state.filename,
                customized_data=st.session_state.get('customized_data'),
                lang_choice=self._get_current_language()
            )
            
            self.ui.display_pdf_preview(st.session_state.pdf_bytes)
        
        if analysis_result:
            with tab2:
                self.ui.display_analysis_results(analysis_result)
            
            with tab3:
                self.ui.display_reasoning_details(analysis_result)

            with tab4:
                self._render_json_editor_tab()

    def _render_json_editor_tab(self):
        """Render a user-friendly JSON editor tab."""
        st.subheader("Edit & Regenerate Customized Data")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.info("💡 **Tip:** You can manually edit the AI-generated JSON here. Make changes and click regenerate.")
        with col2:
            st.warning("⚠️ **Warning:** Be careful not to break the JSON structure. Use the guide for reference.")

        with st.expander("📘 View Required JSON Schema Guide"):
            st.code("""
{
  "personal": { "name": "...", "email": {...}, ... },
  "summary": { "title": "...", "text": "..." },
  "skills": { "title": "...", "categories": [ { "name": "...", "items": ["..."] } ] },
  "experience": { "title": "...", "jobs": [ { "title": "...", ... } ] },
  "projects": { "title": "...", "items": [ { "name": "...", ... } ] },
  "education": { "title": "...", "degrees": [ { "degree": "...", ... } ] },
  "publications": { "title": "...", "items": ["..."] },
  "teaching": { "title": "...", "university_teaching": {...}, ... }
}
            """, language="json")

        st.markdown("---")

        customized_data = st.session_state.get('customized_data', {})
        
        edited_json_str = st.text_area(
            "Customized CV JSON Editor",
            value=json.dumps(customized_data, indent=2, ensure_ascii=False),
            height=400,
            key="json_editor"
        )
        
        if st.button("🔄 Regenerate PDF with My Edits", use_container_width=True, type="primary"):
            try:
                new_data = json.loads(edited_json_str)
                if not isinstance(new_data, dict):
                    raise DataValidationError("Edited content must be a valid JSON object.")

                st.session_state.customized_data = new_data
                
                lang = self._get_current_language()
                generator = CVGenerator(lang=lang)
                
                with self.ui.display_loading_state("Regenerating PDF with your edits..."):
                    pdf_bytes = generator.generate_pdf_bytes(new_data)
                
                if pdf_bytes:
                    st.session_state.pdf_bytes = pdf_bytes
                    st.success("✅ PDF regenerated successfully with your changes!")
                else:
                    st.error("❌ Failed to regenerate PDF.")

            except json.JSONDecodeError:
                st.error("❌ Invalid JSON format. Please check your edits for syntax errors.")
            except Exception as e:
                self.ui.display_error_message(e)
    
    def _render_instructions(self):
        """Render the instructions section."""
        with st.expander("📋 Instructions", expanded=False):
            st.markdown(self._get_instructions_text())
    
    def _get_current_language(self) -> str:
        """Get current language from the last successful generation config."""
        if 'last_generation_config' in st.session_state:
            return st.session_state.last_generation_config[0]
        return settings.DEFAULT_LANGUAGE
    
    def _get_instructions_text(self) -> str:
        """Get the instructions text."""
        return """
### Setup Requirements:

1. **HTML Template**: Your CV template file (`templates/cv_template.html`)
2. **Data Directory**: Contains JSON files with your CV data (`data/`)
3. **Profile Image**: Your profile picture (`profile.jpg` or `default_profile_pic.jpg`) - Optional
4. **Environment File**: Contains your OpenAI API key (`.env`)

### Environment Setup:

Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Required JSON Files in data/ directory:

For English CV:
- `personal_en.json` - Personal information
- `summary_en.json` - Professional summary
- `skills_en.json` - Skills and competencies
- `experience_en.json` - Work experience
- `projects_en.json` - Projects
- `education_en.json` - Educational background
- `publications_en.json` - Publications
- `teaching_en.json` - Teaching experience

For Farsi CV:
- Same files but with `_fa.json` suffix

### How to Use:

**Standard Mode:**
1. Select your preferred language
2. Upload a comprehensive JSON file OR use files from `data/` directory
3. Click "Generate Standard CV" to create your PDF

**AI-Customized Mode:**
1. Select your preferred language
2. Upload/use your CV data
3. Paste a job description in the text area
4. Click "Generate AI-Customized CV"
5. Review the AI analysis and reasoning
6. Download your tailored CV

### AI Features:

- **Job Analysis**: Identifies key requirements and matching skills
- **Content Optimization**: Reorders and emphasizes relevant experience
- **Keyword Integration**: Naturally incorporates job-relevant terms
- **Truthful Customization**: Never fabricates information, only optimizes existing content
- **Detailed Reasoning**: Shows complete chain of thought for all decisions

### File Structure:

```
cv-generator/
├── app.py                  # Main application entry point
├── templates/
│   └── cv_template.html    # HTML template for CV
├── data/
│   ├── personal_en.json    # Your personal data
│   ├── summary_en.json     # Professional summary
│   └── ...                 # Other CV sections
├── .env                    # Environment variables
└── assets/
    ├── profile.jpg
    └── default_profile_pic.jpg
```
"""


class DebugPage:
    """Debug page for development and troubleshooting."""
    
    def __init__(self):
        """Initialize the debug page."""
        self.ui = UIComponents()
    
    def render(self):
        """Render the debug page."""
        st.title("🔧 Debug Information")
        
        # Configuration info
        st.subheader("Configuration")
        config_info = {
            'OPENAI_MODEL': settings.OPENAI_MODEL,
            'OPENAI_BASE_URL': settings.OPENAI_BASE_URL,
            'SUPPORTED_LANGUAGES': settings.SUPPORTED_LANGUAGES,
            'CV_SECTIONS': settings.CV_SECTIONS,
            'TEMPLATE_FILE': settings.TEMPLATE_FILE,
            'DATA_DIRECTORY': settings.DATA_DIRECTORY,
            'API_KEY_CONFIGURED': bool(settings.OPENAI_API_KEY)
        }
        st.json(config_info)
        
        # File system info
        st.subheader("File System")
        file_status = self.ui.display_file_status()
        st.json(file_status)
        
        # Session state
        st.subheader("Session State")
        st.json({k: v for k, v in st.session_state.items()})
        
        # Test components
        st.subheader("Component Tests")
        if st.button("Test Error Display"):
            try:
                raise ValueError("This is a test error")
            except Exception as e:
                self.ui.display_error_message(e, show_traceback=True)

