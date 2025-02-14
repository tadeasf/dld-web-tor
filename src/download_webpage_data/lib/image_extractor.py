"""Module for extracting images from downloaded websites."""

import os
from pathlib import Path
import shutil
from typing import List, Set, Dict
import mimetypes
from bs4 import BeautifulSoup

from . import config
from .exceptions import FileSystemError

class ImageExtractor:
    """Extract images from downloaded websites."""
    
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico'}
    
    def __init__(self, base_dir: Path = None):
        """Initialize the image extractor."""
        self.base_dir = Path(base_dir or config.DOWNLOAD_DIR)
        self.images_dir = Path('images')
        
    def list_websites(self) -> List[str]:
        """List all downloaded websites."""
        if not self.base_dir.exists():
            return []
            
        return [d.name for d in self.base_dir.iterdir() if d.is_dir()]
        
    def _is_image_file(self, path: Path) -> bool:
        """Check if file is an image based on extension or mime type."""
        ext = path.suffix.lower()
        if ext in self.IMAGE_EXTENSIONS:
            return True
            
        mime_type, _ = mimetypes.guess_type(str(path))
        return mime_type and mime_type.startswith('image/')
        
    def _find_image_files(self, website_dir: Path) -> Set[Path]:
        """Find all image files in the website directory."""
        image_files = set()
        
        for path in website_dir.rglob('*'):
            if path.is_file() and self._is_image_file(path):
                image_files.add(path)
                
        return image_files
        
    def _find_html_images(self, website_dir: Path) -> Dict[str, Path]:
        """Find all image references in HTML files."""
        image_refs = {}
        
        for html_file in website_dir.rglob('*.html'):
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
                    
                for img in soup.find_all('img'):
                    src = img.get('src')
                    if src:
                        # Convert relative path to absolute
                        img_path = website_dir / src.lstrip('/')
                        if img_path.exists() and self._is_image_file(img_path):
                            image_refs[src] = img_path
            except Exception as e:
                print(f"Error processing {html_file}: {e}")
                continue
                
        return image_refs
        
    def extract_images(self, website: str) -> int:
        """Extract all images from a website directory."""
        website_dir = self.base_dir / website
        if not website_dir.exists():
            raise FileSystemError(f"Website directory not found: {website}")
            
        # Create images directory
        images_dir = self.images_dir / website
        images_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all image files
        image_files = self._find_image_files(website_dir)
        
        # Find images referenced in HTML
        html_images = self._find_html_images(website_dir)
        
        # Combine all unique image paths
        all_images = set(image_files) | set(html_images.values())
        
        # Copy images to output directory
        copied_count = 0
        for img_path in all_images:
            try:
                # Create a unique filename
                new_name = f"{img_path.stem}_{img_path.name}"
                dest_path = images_dir / new_name
                
                # Copy the file
                shutil.copy2(img_path, dest_path)
                copied_count += 1
                print(f"Copied: {img_path.name}")
                
            except Exception as e:
                print(f"Error copying {img_path}: {e}")
                continue
                
        return copied_count 