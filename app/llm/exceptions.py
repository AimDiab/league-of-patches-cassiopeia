class LLMProviderError(Exception):
    """Base exception for all LLM provider errors."""


class LLMFetchError(LLMProviderError):
    """Raised when the provider could not retrieve the patch notes URL content."""


class LLMClassificationError(LLMProviderError):
    """Raised when the model call failed or its output did not validate."""
