"""
A tool to download website contents through Tor with German exit nodes.
"""

import os
import sys
import urllib.parse
from pathlib import Path
import re
from urllib.parse import urljoin, urlparse

import requests
import socks
from bs4 import BeautifulSoup
from stem import Signal
from stem.control import Controller
import urllib3

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Browser-like headers
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}

class TorDownloader:
    def __init__(self, verify_ssl=False):
        """Initialize the downloader using system Tor service."""
        self.verify_ssl = verify_ssl
        self.session = self.setup_session()
        
    def setup_session(self):
        """Create requests session with Tor SOCKS proxy."""
        session = requests.Session()
        session.proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        session.verify = self.verify_ssl
        session.headers.update(DEFAULT_HEADERS)
        return session

    def check_tor_connection(self):
        """Verify Tor connection is working."""
        try:
            response = self.session.get('https://check.torproject.org/', verify=self.verify_ssl)
            return 'Congratulations. This browser is configured to use Tor.' in response.text
        except Exception as e:
            print(f"Error checking Tor connection: {e}")
            print("Please ensure Tor service is running (sudo systemctl start tor)")
            return False

    def new_tor_identity(self):
        """Request new Tor identity if needed."""
        try:
            with Controller.from_port(port=9051) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
                print("Successfully obtained new Tor identity")
        except Exception as e:
            print(f"Could not obtain new Tor identity: {e}")

    def is_valid_url(self, url):
        """Check if URL is valid and belongs to the target domain."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def save_file(self, content, filepath):
        """Save content to file, creating directories if needed."""
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'wb') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving file {filepath}: {e}")
            return False

    def download_with_retry(self, url, referer=None, max_retries=3):
        """Download URL with retry logic and proper headers."""
        headers = self.session.headers.copy()
        if referer:
            headers['Referer'] = referer
            
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, headers=headers, timeout=30, verify=self.verify_ssl)
                response.raise_for_status()
                return response
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403 and attempt < max_retries - 1:
                    print(f"Received 403 for {url}, retrying with new Tor identity...")
                    self.new_tor_identity()
                    continue
                raise
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Error downloading {url}, retrying: {e}")
                    continue
                raise

    def download_website(self, url):
        """Download complete website content."""
        try:
            # Parse base URL and create output directory
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            base_url = f"{parsed_url.scheme}://{domain}"
            output_dir = Path(f"downloads/{domain}")
            
            # Set to keep track of downloaded URLs
            downloaded_urls = set()
            urls_to_download = {url}
            
            print(f"Starting download of {url} through Tor...")
            print("SSL verification is", "enabled" if self.verify_ssl else "disabled")
            
            while urls_to_download:
                current_url = urls_to_download.pop()
                if current_url in downloaded_urls:
                    continue
                    
                try:
                    # Download page
                    response = self.download_with_retry(current_url, referer=base_url)
                    
                    # Determine file path
                    rel_path = urlparse(current_url).path
                    if not rel_path or rel_path.endswith('/'):
                        rel_path += 'index.html'
                    elif '.' not in rel_path.split('/')[-1]:
                        rel_path += '/index.html'
                        
                    file_path = output_dir / rel_path.lstrip('/')
                    
                    # Save the file
                    if self.save_file(response.content, file_path):
                        downloaded_urls.add(current_url)
                        print(f"Downloaded: {current_url}")
                        
                        # If HTML, parse for more links
                        if 'text/html' in response.headers.get('content-type', '').lower():
                            soup = BeautifulSoup(response.text, 'html.parser')
                            
                            # Find all links
                            for tag in soup.find_all(['a', 'link', 'script', 'img']):
                                href = tag.get('href') or tag.get('src')
                                if href:
                                    absolute_url = urljoin(current_url, href)
                                    if (self.is_valid_url(absolute_url) and 
                                        urlparse(absolute_url).netloc == domain and 
                                        absolute_url not in downloaded_urls):
                                        urls_to_download.add(absolute_url)
                                        
                except Exception as e:
                    print(f"Error downloading {current_url}: {e}")
                    continue
                    
            print("\nDownload completed successfully!")
            return True
            
        except Exception as e:
            print(f"Error downloading website: {e}")
            return False

def main():
    """Main entry point."""
    print("Initializing Tor downloader...")
    
    # Ask about SSL verification
    verify_ssl = input("Verify SSL certificates? (y/N): ").strip().lower() == 'y'
    downloader = TorDownloader(verify_ssl=verify_ssl)
    
    try:
        # Check Tor connection
        print("Checking Tor connection...")
        if not downloader.check_tor_connection():
            print("ERROR: Could not connect to Tor. Please ensure Tor service is running.")
            print("On Manjaro/Arch: sudo systemctl start tor")
            sys.exit(1)
            
        # Get URL from user
        url = input("Enter the website URL to download: ").strip()
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Download website
        success = downloader.download_website(url)
        
        if success:
            print("\nWebsite downloaded successfully!")
        else:
            print("\nFailed to download website.")
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()

__version__ = "0.1.0"
__all__ = ["TorDownloader"]
