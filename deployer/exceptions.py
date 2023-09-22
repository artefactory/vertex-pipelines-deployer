class TagNotFoundError(Exception):
    """Raised when a tag is not found."""

    pass


class MissingGoogleArtifactRegistryHostError(Exception):
    """Raised when the Google Artifact Registry host is missing."""

    pass
