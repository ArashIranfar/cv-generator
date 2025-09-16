import json
from typing import Dict, Any, Optional

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from config.settings import settings
from src.utils.exceptions import AIServiceError, ConfigurationError
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class CVAgent:
    """
    AI agent that analyzes job descriptions and customizes CV content accordingly.
    Uses OpenAI's API through LangChain for natural language processing.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the CV Agent with OpenAI API configuration.
        
        Args:
            api_key: OpenAI API key. If None, uses settings.OPENAI_API_KEY
            
        Raises:
            ConfigurationError: If API key is not provided or found in settings
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        
        if not self.api_key:
            raise ConfigurationError(
                "OpenAI API key not found. Please set OPENAI_API_KEY in your .env file"
            )
        
        self._setup_llm()
    
    def _setup_llm(self):
        """Initialize the Language Model client."""

        try:
            kwargs = {
                "openai_api_key": self.api_key,
                "model_name": settings.OPENAI_MODEL,
                "temperature": settings.OPENAI_TEMPERATURE,
            }

            # only add base_url if provided
            if getattr(settings, "OPENAI_BASE_URL", None):
                kwargs["base_url"] = settings.OPENAI_BASE_URL

            self.llm = ChatOpenAI(**kwargs)

            # self.llm = ChatOpenAI(
            #     openai_api_key=self.api_key,
            #     model_name=settings.OPENAI_MODEL,
            #     temperature=settings.OPENAI_TEMPERATURE,
            #     base_url= settings.OPENAI_BASE_URL
            # )
            logger.info(f"LLM initialized with model: {settings.OPENAI_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise ConfigurationError(f"LLM initialization failed: {e}")
    
    def analyze_job_description(self, job_description: str, 
                              original_data: Dict[str, Any], 
                              lang: str = 'en') -> Dict[str, Any]:
        """
        Analyze job description and customize CV data accordingly.
        
        Args:
            job_description: The job posting text
            original_data: Original CV data from JSON files
            lang: Language preference ('en' or 'fa')
            
        Returns:
            Dictionary containing analysis results and customized CV data
            
        Raises:
            AIServiceError: If API call fails or response is invalid
        """
        if not job_description.strip():
            raise ValueError("Job description cannot be empty")
        
        if not original_data:
            raise ValueError("Original CV data cannot be empty")
        
        logger.info(f"Starting job analysis for language: {lang}")
        logger.info(f"Job description length: {len(job_description)} characters")
        
        try:
            # Create system and human prompts
            system_prompt = self._create_system_prompt(lang)
            human_prompt = self._create_human_prompt(job_description, original_data)
            
            # Make API call
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            logger.info("Making API call to OpenAI...")
            response = self.llm.invoke(messages)
            
            # Parse and validate response
            result = self._parse_response(response.content)
            
            logger.info("AI analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error during AI analysis: {e}")
            raise AIServiceError(f"AI analysis failed: {e}")
    
    def _create_system_prompt(self, lang: str) -> str:
        """
        Create the system prompt for the AI agent.
        
        Args:
            lang: Language code
            
        Returns:
            System prompt string
        """
        language_name = settings.get_language_display_name(lang)
        
        return f"""You are a professional CV optimization expert. Your task is to analyze a job description and customize CV content to match the requirements while maintaining truthfulness.

IMPORTANT RULES:
1. NEVER fabricate experience, skills, or achievements
2. Only highlight, reorder, or rephrase existing content
3. Maintain all factual accuracy
4. Focus on relevant experience and skills
5. Use keywords from the job description where appropriate
6. Provide detailed reasoning for all changes

Language: {language_name}

You will receive:
1. A job description
2. Original CV data in JSON format

You must return a JSON response with this exact structure:
{{
    "analysis": {{
        "key_requirements": ["requirement1", "requirement2", ...],
        "matching_skills": ["skill1", "skill2", ...],
        "gaps_identified": ["gap1", "gap2", ...],
        "optimization_strategy": "detailed explanation of approach"
    }},
    "reasoning": {{
        "summary_changes": "explanation of summary modifications",
        "skills_prioritization": "explanation of skills reordering/emphasis",
        "experience_highlighting": "explanation of experience modifications",
        "projects_selection": "explanation of project selection/emphasis",
        "overall_strategy": "overall customization strategy"
    }},
    "customized_data": {{
        "personal": {{"original personal data - unchanged"}},
        "summary": {{"optimized summary section"}},
        "skills": {{"reordered/emphasized skills"}},
        "experience": {{"highlighted relevant experience"}},
        "projects": {{"selected/emphasized relevant projects"}},
        "education": {{"original education data - unchanged"}},
        "publications": {{"original publications - unchanged"}},
        "teaching": {{"original teaching - unchanged"}}
    }}
}}

Be thorough in your reasoning and explain every decision made."""
    
    def _create_human_prompt(self, job_description: str, 
                           original_data: Dict[str, Any]) -> str:
        """
        Create the human prompt with job description and CV data.
        
        Args:
            job_description: Job posting text
            original_data: Original CV data
            
        Returns:
            Human prompt string
        """
        return f"""
Job Description:
{job_description}

Original CV Data:
{json.dumps(original_data, indent=2, ensure_ascii=False)}

Please analyze this job description and customize the CV data accordingly. Provide detailed reasoning for all changes.
"""
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse and validate the AI response.
        
        Args:
            response_text: Raw response from AI
            
        Returns:
            Parsed and validated response dictionary
            
        Raises:
            AIServiceError: If response cannot be parsed or is invalid
        """
        try:
            # Clean the response (remove markdown formatting if present)
            clean_response = response_text.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:]
            if clean_response.endswith('```'):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()
            
            # Parse JSON
            result = json.loads(clean_response)
            
            # Validate required structure
            required_keys = ['analysis', 'reasoning', 'customized_data']
            for key in required_keys:
                if key not in result:
                    raise AIServiceError(f"Missing required key in AI response: {key}")
            
            # Validate analysis section
            analysis_keys = ['key_requirements', 'matching_skills', 'gaps_identified', 'optimization_strategy']
            for key in analysis_keys:
                if key not in result['analysis']:
                    logger.warning(f"Missing analysis key: {key}")
            
            # Validate reasoning section
            reasoning_keys = ['summary_changes', 'skills_prioritization', 'experience_highlighting', 'projects_selection', 'overall_strategy']
            for key in reasoning_keys:
                if key not in result['reasoning']:
                    logger.warning(f"Missing reasoning key: {key}")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.error(f"Raw response: {clean_response[:500]}...")
            raise AIServiceError(f"Failed to parse AI response as JSON: {e}")
        except Exception as e:
            logger.error(f"Response validation failed: {e}")
            raise AIServiceError(f"Invalid AI response format: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the configured AI model.
        
        Returns:
            Dictionary with model configuration information
        """
        return {
            'model_name': settings.OPENAI_MODEL,
            'temperature': settings.OPENAI_TEMPERATURE,
            'base_url': settings.OPENAI_BASE_URL,
            'api_key_configured': bool(self.api_key),
            'is_initialized': hasattr(self, 'llm')
        }