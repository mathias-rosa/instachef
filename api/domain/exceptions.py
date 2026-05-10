class InstachefError(Exception):
    """Base class for all application-level errors."""


class SourceError(InstachefError):
    """Base class for source ingestion errors."""


class InvalidSourceError(SourceError):
    """Raised when a source identifier or URL is invalid."""


class SourceFetchError(SourceError):
    """Raised when the source cannot be fetched from the provider."""


class SourceDownloadError(SourceError):
    """Raised when source download succeeds partially but artifacts are unusable."""


class ExtractionError(InstachefError):
    """Base class for extraction errors."""


class VideoReadError(ExtractionError):
    """Raised when the downloaded media cannot be read."""


class RecipeGenerationError(ExtractionError):
    """Raised when the LLM extraction call fails."""


class UnexpectedExtractionOutputError(ExtractionError):
    """Raised when extraction output is not the expected schema type."""


class NotARecipeError(ExtractionError):
    """Raised when the extracted content is not a valid recipe."""


class RepositoryError(InstachefError):
    """Base class for persistence errors."""


class RepositoryWriteError(RepositoryError):
    """Raised when persisting a recipe record fails."""


class RepositoryReadError(RepositoryError):
    """Raised when reading a recipe record fails."""
