# download-webpage-data

A Python tool to download website contents through Tor with German exit nodes and extract images from downloaded websites.

## Prerequisites

- Python 3.8 or higher
- Tor service installed on your system
- `torrc` configuration file (will be created automatically)

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install .
```

## Features

### Website Downloader
- Routes all traffic through Tor
- Uses German exit nodes exclusively
- Downloads complete website contents
- Preserves website structure
- Handles errors gracefully
- Supports sites with invalid SSL certificates
- Retries failed downloads with new Tor identity

### Image Extractor
- Extracts all images from downloaded websites
- Supports multiple image formats (jpg, jpeg, png, gif, webp, svg, ico)
- Finds both direct image files and HTML-referenced images
- Preserves original filenames
- Creates organized output structure
- Handles duplicate files

## Usage

### Downloading Websites

1. Ensure Tor service is running on your system:
```bash
# On Manjaro/Arch:
sudo systemctl start tor
```

2. Download a website:
```bash
# Interactive mode
python -m download_webpage_data

# Direct URL mode
python -m download_webpage_data -u https://example.com

# With SSL verification
python -m download_webpage_data --verify-ssl -u https://example.com
```

### Extracting Images

1. After downloading one or more websites, run:
```bash
python -m download_webpage_data.extract_images
```

2. Select the website from the list
3. Images will be extracted to `images/<website>/` directory

## Command-line Options

### Website Downloader
- `-u, --url`: URL to download (if not provided, will prompt)
- `--verify-ssl`: Enable SSL certificate verification (disabled by default)

### Image Extractor
- Interactive menu to select from downloaded websites
- Press 'q' to quit at any time

## Directory Structure

```
.
├── downloads/           # Downloaded websites
│   └── example.com/    # Website content
└── images/             # Extracted images
    └── example.com/    # Images from website
```

## Security Note

This tool is for legitimate use only. Ensure you have permission to download website contents before using this tool.

## License

MIT
