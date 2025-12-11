"""
Exceptions for SPED parsing errors.
"""


class SPEDError(Exception):
    """Base exception for all SPED parsing errors."""

    pass


class SPEDParseError(SPEDError):
    """Error parsing SPED file content."""

    pass


class SPEDValidationError(SPEDError):
    """Invalid SPED file structure or content."""

    pass


class SPEDEncodingError(SPEDError):
    """Error decoding file with expected encoding."""

    pass


class SPEDFileNotFoundError(SPEDError):
    """SPED file not found at specified path."""

    pass


class SPEDEmptyFileError(SPEDError):
    """SPED file is empty or has no valid records."""

    pass
