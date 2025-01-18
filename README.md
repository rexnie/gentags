# gentags

A command-line tool for generating cscope database and ctags files to help with code navigation.

## Features

- Generate cscope database and ctags files for code navigation
- Support multiple programming languages (C/C++, Python, JavaScript, TypeScript)
- Configurable directory scanning depth
- Directory exclusion support
- Detailed logging and configuration options

## Installation

```bash
git clone https://github.com/yourusername/gentags.git
cd gentags
chmod +x gentags.py
```


## Usage

Basic usage:

```bash
./gentags.py -d <directory> [-t <language>]
```


Examples:

```bash
# Scan src and lib directories for C/C++ files
./gentags.py -d src lib -t c_cpp

# Scan for Python and JavaScript files
./gentags.py -d src -t python javascript

# Exclude test directories
./gentags.py -d src -e src/test src/deprecated

# Set scan depth
./gentags.py -d src/core --depth 2

# Generate only index file
./gentags.py -d src -i

# Show current configuration
./gentags.py -s

# Clean generated files
./gentags.py -c
```


## Options

- `-d, --dirs`: Directories to scan
- `-t, --types`: Programming languages to include (default: c_cpp)
  - Available options: c_cpp, python, javascript, typescript, all
- `-e, --exclude`: Directories to exclude from scanning
- `--depth`: Maximum directory depth for scanning (default: 9999999)
- `-i, --index-only`: Only generate index file without tags
- `-c, --clean`: Clean all generated files
- `-s, --show-config`: Show current configuration
- `-v, --verbose`: Enable verbose logging

## Requirements

- Python 3.6+
- cscope
- ctags

## License

reference ./LICENSE file

---
