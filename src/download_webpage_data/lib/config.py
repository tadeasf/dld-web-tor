# Browser-like headers for requests
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}

# Tor proxy configuration
TOR_PROXY = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

# Download settings
DOWNLOAD_TIMEOUT = 30
MAX_RETRIES = 3
DOWNLOAD_DIR = "downloads"

# File types and extensions
HTML_CONTENT_TYPE = 'text/html'
DEFAULT_INDEX = 'index.html'

# Tags to search for when parsing HTML
LINK_TAGS = ['a', 'link', 'script', 'img']
LINK_ATTRS = ['href', 'src'] 