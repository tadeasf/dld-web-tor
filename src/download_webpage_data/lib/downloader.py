from pathlib import Path
from typing import Optional, Set
import urllib3

import requests
from bs4 import BeautifulSoup
from stem import Signal
from stem.control import Controller

from . import config
from . import utils
from .exceptions import TorConnectionError, TorIdentityError, DownloadError

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TorDownloader:
    def __init__(self, verify_ssl: bool = False):
        """Initialize the downloader using system Tor service."""
        self.verify_ssl = verify_ssl
        self.session = self._setup_session()
        
    def _setup_session(self) -> requests.Session:
        """Create requests session with Tor SOCKS proxy."""
        session = requests.Session()
        session.proxies = config.TOR_PROXY
        session.verify = self.verify_ssl
        session.headers.update(config.DEFAULT_HEADERS)
        return session

    def check_tor_connection(self) -> bool:
        """Verify Tor connection is working."""
        try:
            response = self.session.get('https://check.torproject.org/', verify=self.verify_ssl)
            return 'Congratulations. This browser is configured to use Tor.' in response.text
        except Exception as e:
            raise TorConnectionError(f"Error checking Tor connection: {e}")

    def new_tor_identity(self) -> None:
        """Request new Tor identity if needed."""
        try:
            with Controller.from_port(port=9051) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
                print("Successfully obtained new Tor identity")
        except Exception as e:
            raise TorIdentityError(f"Could not obtain new Tor identity: {e}")

    def _download_with_retry(self, url: str, referer: Optional[str] = None) -> requests.Response:
        """Download URL with retry logic and proper headers."""
        headers = self.session.headers.copy()
        if referer:
            headers['Referer'] = referer
            
        for attempt in range(config.MAX_RETRIES):
            try:
                response = self.session.get(
                    url, 
                    headers=headers, 
                    timeout=config.DOWNLOAD_TIMEOUT, 
                    verify=self.verify_ssl
                )
                response.raise_for_status()
                return response
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403 and attempt < config.MAX_RETRIES - 1:
                    print(f"Received 403 for {url}, retrying with new Tor identity...")
                    self.new_tor_identity()
                    continue
                raise DownloadError(f"HTTP error downloading {url}: {e}")
            except Exception as e:
                if attempt < config.MAX_RETRIES - 1:
                    print(f"Error downloading {url}, retrying: {e}")
                    continue
                raise DownloadError(f"Error downloading {url}: {e}")

    def _process_html(self, content: str, current_url: str, domain: str, downloaded_urls: Set[str]) -> Set[str]:
        """Process HTML content and extract URLs to download."""
        urls_to_download = set()
        soup = BeautifulSoup(content, 'html.parser')
        
        for tag in soup.find_all(config.LINK_TAGS):
            for attr in config.LINK_ATTRS:
                href = tag.get(attr)
                if not href:
                    continue
                    
                absolute_url = utils.get_absolute_url(current_url, href)
                if absolute_url and utils.should_download_url(absolute_url, domain, downloaded_urls):
                    urls_to_download.add(absolute_url)
                    
        return urls_to_download

    def download_website(self, url: str) -> bool:
        """Download complete website content."""
        try:
            domain = utils.get_domain(url)
            base_url = utils.get_base_url(url)
            output_dir = Path(config.DOWNLOAD_DIR) / domain
            
            downloaded_urls = set()
            urls_to_download = {url}
            
            print(f"Starting download of {url} through Tor...")
            print("SSL verification is", "enabled" if self.verify_ssl else "disabled")
            
            while urls_to_download:
                current_url = urls_to_download.pop()
                if current_url in downloaded_urls:
                    continue
                    
                try:
                    response = self._download_with_retry(current_url, referer=base_url)
                    file_path = utils.get_file_path(current_url, output_dir)
                    
                    if utils.save_content(response.content, file_path):
                        downloaded_urls.add(current_url)
                        print(f"Downloaded: {current_url}")
                        
                        if config.HTML_CONTENT_TYPE in response.headers.get('content-type', '').lower():
                            new_urls = self._process_html(
                                response.text, 
                                current_url, 
                                domain, 
                                downloaded_urls
                            )
                            urls_to_download.update(new_urls)
                            
                except Exception as e:
                    print(f"Error processing {current_url}: {e}")
                    continue
                    
            print("\nDownload completed successfully!")
            return True
            
        except Exception as e:
            print(f"Error downloading website: {e}")
            return False 