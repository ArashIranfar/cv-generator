class CVGeneratorException(Exception):
    """Base exception for CV Generator application."""
    pass


class TemplateNotFoundError(CVGeneratorException):
    """Raised when the HTML template file is not found."""
    pass


class DataValidationError(CVGeneratorException):
    """Raised when CV data validation fails."""
    pass


class AIServiceError(CVGeneratorException):
    """Raised when AI service calls fail."""
    pass


class PDFGenerationError(CVGeneratorException):
    """Raised when PDF generation fails."""
    pass


class FileLoadError(CVGeneratorException):
    """Raised when file loading fails."""
    pass


class ConfigurationError(CVGeneratorException):
    """Raised when configuration is invalid."""
    pass