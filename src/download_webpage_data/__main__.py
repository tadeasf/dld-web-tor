#!/usr/bin/env python3
"""Main entry point for the website downloader."""

import sys
import argparse
from typing import Optional

from .lib.downloader import TorDownloader
from .lib.exceptions import TorConnectionError, DownloadError

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Download website contents through Tor with German exit nodes."
    )
    parser.add_argument(
        "--url", "-u",
        help="URL to download (if not provided, will prompt)",
        type=str
    )
    parser.add_argument(
        "--verify-ssl",
        help="Verify SSL certificates",
        action="store_true",
        default=False
    )
    return parser.parse_args()

def get_url(url: Optional[str] = None) -> str:
    """Get URL from argument or prompt."""
    if url:
        return url
        
    url = input("Enter the website URL to download: ").strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

def main() -> int:
    """Main entry point."""
    args = parse_args()
    
    try:
        print("Initializing Tor downloader...")
        downloader = TorDownloader(verify_ssl=args.verify_ssl)
        
        # Check Tor connection
        print("Checking Tor connection...")
        if not downloader.check_tor_connection():
            print("ERROR: Could not connect to Tor. Please ensure Tor service is running.")
            print("On Manjaro/Arch: sudo systemctl start tor")
            return 1
            
        # Get and validate URL
        url = get_url(args.url)
        
        # Download website
        success = downloader.download_website(url)
        
        if success:
            print("\nWebsite downloaded successfully!")
            return 0
        else:
            print("\nFailed to download website.")
            return 1
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 130
    except TorConnectionError as e:
        print(f"\nTor connection error: {e}")
        return 1
    except DownloadError as e:
        print(f"\nDownload error: {e}")
        return 1
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 