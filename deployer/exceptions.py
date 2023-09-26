class TagNotFoundError(Exception):
    """Raised when a tag is not found."""


class MissingGoogleArtifactRegistryHostError(Exception):
    """Raised when the Google Artifact Registry host is missing."""


class UnsupportedConfigFileError(Exception):
    """Raised when the config file is not supported."""
