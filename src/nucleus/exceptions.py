class NucleusError(Exception):
    """Base exception class for Nucleus SDK."""
    pass

class NucleusAPIError(NucleusError):
    """Exception raised for errors in the API."""
    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response
        self.message = message

    def __str__(self):
        if self.status_code:
            return f"{self.message} (Status: {self.status_code})"
        return self.message

class NucleusAuthError(NucleusAPIError):
    """Exception raised for authentication errors."""
    pass

class NucleusValidationError(NucleusError):
    """Exception raised for validation errors."""
    pass

class NucleusNotFoundError(NucleusAPIError):
    """Exception raised when a resource is not found."""
    pass

class NucleusPermissionError(NucleusAPIError):
    """Exception raised for permission-related errors."""
    pass
