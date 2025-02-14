class TorConnectionError(Exception):
    """Raised when there are issues with Tor connection."""
    pass

class TorIdentityError(Exception):
    """Raised when unable to get new Tor identity."""
    pass

class DownloadError(Exception):
    """Raised when there are issues downloading content."""
    pass

class FileSystemError(Exception):
    """Raised when there are issues with file operations."""
    pass 