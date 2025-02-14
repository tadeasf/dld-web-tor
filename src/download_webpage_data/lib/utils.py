from pathlib import Path
from urllib.parse import urlparse, urljoin
from typing import Optional, Set

from .exceptions import FileSystemError

def is_valid_url(url: str) -> bool:
    """Check if URL is valid and has proper scheme and netloc."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_domain(url: str) -> str:
    """Extract domain from URL."""
    return urlparse(url).netloc

def get_base_url(url: str) -> str:
    """Get base URL from full URL."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

def get_file_path(url: str, base_dir: Path, default_index: str = 'index.html') -> Path:
    """Determine file path from URL and base directory."""
    rel_path = urlparse(url).path
    if not rel_path or rel_path.endswith('/'):
        rel_path += default_index
    elif '.' not in rel_path.split('/')[-1]:
        rel_path += f"/{default_index}"
    
    return base_dir / rel_path.lstrip('/')

def save_content(content: bytes, filepath: Path) -> bool:
    """Save content to file, creating directories if needed."""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(content)
        return True
    except Exception as e:
        raise FileSystemError(f"Error saving file {filepath}: {e}")

def get_absolute_url(base_url: str, href: Optional[str]) -> Optional[str]:
    """Convert relative URL to absolute URL."""
    if not href:
        return None
    try:
        return urljoin(base_url, href)
    except:
        return None

def should_download_url(url: str, domain: str, downloaded_urls: Set[str]) -> bool:
    """Check if URL should be downloaded."""
    return (is_valid_url(url) and 
            urlparse(url).netloc == domain and 
            url not in downloaded_urls) 