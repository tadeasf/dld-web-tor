# download-webpage-data

A Python tool to download website contents through Tor with German exit nodes.

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

## Usage

1. Ensure Tor service is running on your system
2. Run the tool:
```bash
python -m download_webpage_data
```

3. Enter the URL when prompted

## Features

- Routes all traffic through Tor
- Uses German exit nodes exclusively
- Downloads complete website contents
- Preserves website structure
- Handles errors gracefully

## Security Note

This tool is for legitimate use only. Ensure you have permission to download website contents before using this tool.

## License

MIT
