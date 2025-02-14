#!/usr/bin/env python3
"""Command-line script to extract images from downloaded websites."""

import sys
from pathlib import Path

from .lib.image_extractor import ImageExtractor
from .lib.exceptions import FileSystemError

def select_website(websites: list) -> str:
    """Let user select a website from the list."""
    if not websites:
        print("No downloaded websites found.")
        sys.exit(1)
        
    print("\nAvailable websites:")
    for i, website in enumerate(websites, 1):
        print(f"{i}. {website}")
        
    while True:
        try:
            choice = input("\nSelect website number (or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                sys.exit(0)
                
            idx = int(choice) - 1
            if 0 <= idx < len(websites):
                return websites[idx]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a number or 'q' to quit.")

def main() -> int:
    """Main entry point."""
    try:
        # Initialize image extractor
        extractor = ImageExtractor()
        
        # Get list of websites
        websites = extractor.list_websites()
        
        # Let user select website
        website = select_website(websites)
        
        print(f"\nExtracting images from {website}...")
        
        # Extract images
        count = extractor.extract_images(website)
        
        print(f"\nExtracted {count} images to images/{website}/")
        return 0
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 130
    except FileSystemError as e:
        print(f"\nFile system error: {e}")
        return 1
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 