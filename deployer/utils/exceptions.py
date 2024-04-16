class TagNotFoundError(Exception):
    """Raised when a tag is not found."""


class MissingGoogleArtifactRegistryHostError(Exception):
    """Raised when the Google Artifact Registry host is missing."""


class UnsupportedConfigFileError(Exception):
    """Raised when the config file is not supported."""


class BadConfigError(ValueError):
    """Raised when a config is invalid."""


class InvalidPyProjectTOMLError(Exception):
    """Raised when the configuration is invalid."""


class TemplateFileCreationError(Exception):
    """Exception raised when a file cannot be created from a template."""
