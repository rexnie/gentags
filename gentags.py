#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Generate cscope database and ctags files for code navigation
# author: Rex.Nie niedao516@126.com

import os
import argparse
import logging
import subprocess
import sys

def init_logger(name="gentags_logger"):
    """Initialize and configure logger."""
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

# create global logger
logger = init_logger()

def configure_logger(verbose):
    """Configure the logger for the script."""
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


def write_config(config_file, dirs, depth, exclude, types):
    """Write the configuration to a file."""
    if not dirs:
        logger.error("No valid directories to scan")
        raise ValueError("No valid directories to scan.")

    logger.info("Generating config file...")
    with open(config_file, "w") as f:
        # write global configuration
        f.write("[global]\n")
        f.write(f"filetype = {' '.join(types)}\n")
        f.write(f"depth = {depth}\n\n")
        
        # write directories configuration
        f.write("[dirs]\n")
        for directory in dirs:
            f.write(f"path = {directory}\n")
        f.write("\n")
        
        # write exclude directories configuration
        if exclude:
            f.write("[exclude_dirs]\n")
            for ex_dir in exclude:
                f.write(f"path = {ex_dir}\n")
                
        logger.info(f"Config file generated: {config_file}")


def save_command(command_file, args):
    """Save the user's command to a file."""
    logger.info("Saving user command...")
    with open(command_file, "w") as f:
        f.write(" ".join(args) + "\n")
        logger.info(f"User command saved: {command_file}")


def generate_index(index_file, dirs, depth, exclude, types):
    """Generate the index file."""
    if not dirs:
        logger.error("No directories to scan. Index file generation aborted.")
        raise ValueError("No directories to scan.")

    logger.info("Generating index file...")
    files_set = set()

    for directory in dirs:
        for root, subdirs, files in os.walk(directory):
            logger.debug(f"dir walk: root={root}, subdirs={subdirs}, files={files}")
            # Adjust depth of traversal
            current_depth = root[len(directory):].count(os.sep)
            if current_depth >= depth:
                subdirs[:] = []

            # Exclude specified directories
            subdirs[:] = [d for d in subdirs if os.path.join(root, d) not in exclude]

            # Include files with specified extensions
            for file in files:
                if any(file.endswith(ext) for ext in types):
                    files_set.add(os.path.join(root, file))

    with open(index_file, "w") as f:
        for file_path in sorted(files_set):
            f.write(file_path + "\n")

    if not files_set:
        logger.warning(f"No source files found. Check your directories and filters.")
    else:
        logger.info(f"Index file generated: {index_file}")


def generate_cscope(index_file):
    """Generate the cscope database."""
    logger.info("Generating cscope database...")
    cmd = f"cscope -bkq -i {index_file}"
    logger.debug(f"Executing: {cmd}")
    subprocess.run(cmd, shell=True, check=True)
    logger.info("Cscope database generation completed.")


def generate_ctags(index_file):
    """Generate the ctags file."""
    logger.info("Generating tags file...")
    cmd = f"ctags -L {index_file}"
    logger.debug(f"Executing: {cmd}")
    subprocess.run(cmd, shell=True, check=True)
    logger.info("Tags file generation completed.")


FILE_EXTENSIONS = {
    'c_cpp': ['.c', '.h', '.cpp', '.hpp', '.cxx', '.hxx', '.cc', '.hh', '.C', '.H', '.S', '.s'],
    'python': ['.py', '.pyw', '.pyx', '.pxd', '.pxi'],
    'javascript': ['.js', '.jsx', '.mjs', '.cjs'],
    'typescript': ['.ts', '.tsx', '.mts', '.cts']
}


ALL_EXTENSIONS = [ext for exts in FILE_EXTENSIONS.values() for ext in exts]

def get_language_extensions(languages):
    """Get file extensions for specified languages."""
    if not languages:
        return ALL_EXTENSIONS
    extensions = []
    for lang in languages:
        if lang in FILE_EXTENSIONS:
            extensions.extend(FILE_EXTENSIONS[lang])
    return extensions

def main():
    parser = argparse.ArgumentParser(
        description="Generate cscope database and ctags files for code navigation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage - scan src and lib directories for C/C++ files
  %(prog)s -d src lib -t .c .h .cpp

  # Exclude specific directories
  %(prog)s -d src -e src/test src/deprecated

  # Set scan depth for directories
  %(prog)s -d src/core --depth 2 -d src/modules

  # Generate only index file
  %(prog)s -d src -i

  # Show current configuration
  %(prog)s -s

  # Clean generated files
  %(prog)s -c
        """
    )

    # Directory options
    dir_group = parser.add_argument_group('Directory options') 
    dir_group.add_argument('-d', '--dirs', nargs='*', help='Directories to scan')
    dir_group.add_argument('--depth', type=int, default=9999999,
                      help='Maximum directory depth for scanning (default: 9999999)')
    dir_group.add_argument('-e', '--exclude', nargs='*', default=[],
                      help='Directories to exclude from scanning')

    # File type options
    file_group = parser.add_argument_group('File type options')
    file_group.add_argument('-t', '--types', nargs='*', 
                      default=['c_cpp'],
                      choices=list(FILE_EXTENSIONS.keys()) + ['all'],
                      help='Programming languages to include (default: c_cpp). '
                           'Available options: ' + ', '.join(list(FILE_EXTENSIONS.keys())) + ', all')

    # Output options
    output_group = parser.add_argument_group('Output options')
    output_group.add_argument('-f', '--index-file', default='gentags.files',
                      help='Index file path (default: gentags.files)')
    output_group.add_argument('-o', '--config-file', default='gentags.conf',
                      help='Config file path (default: gentags.conf)')
    output_group.add_argument('-i', '--index-only', action='store_true',
                      help='Only generate index file without tags')

    # Utility options
    util_group = parser.add_argument_group('Utility options')
    util_group.add_argument('-c', '--clean', action='store_true',
                      help='Clean all generated files')
    util_group.add_argument('-s', '--show-config', action='store_true',
                      help='Show current configuration')
    util_group.add_argument('-v', '--verbose', action='store_true',
                      help='Enable verbose logging')

    args = parser.parse_args()

    if 'all' in args.types:
        args.types = ALL_EXTENSIONS
    else:
        args.types = get_language_extensions(args.types)

    # Remove trailing directory separators from exclude paths
    args.exclude = [os.path.normpath(path) for path in args.exclude]

    # Save the user's command
    save_command("gentags.cmd", sys.argv)

    # Configure logger
    configure_logger(args.verbose)

    # Handle --clean option
    if args.clean:
        logger.info("Cleaning generated files...")
        for file in [args.index_file, args.config_file, "gentags.cmd", "cscope.out", "cscope.in.out", "cscope.po.out", "tags"]:
            if os.path.exists(file):
                os.remove(file)
                logger.info(f"Removed: {file}")
        logger.info("Clean completed.")
        return

    # Handle --show-config option
    if args.show_config:
        logger.info("Current configuration:")
        logger.info(f"  Directories: {args.dirs}")
        logger.info(f"  Depth: {args.depth}")
        logger.info(f"  Exclude: {args.exclude}")
        logger.info(f"  File types: {args.types}")
        logger.info(f"  Index file: {args.index_file}")
        logger.info(f"  Config file: {args.config_file}")
        return

    # Generate configuration and index files
    write_config(args.config_file, args.dirs, args.depth, args.exclude, args.types)
    generate_index(args.index_file, args.dirs, args.depth, args.exclude, args.types)

    # Stop if only index file is needed
    if args.index_only:
        logger.info("Index file generation completed. Skipping cscope and ctags generation.")
        return

    # Generate cscope and ctags files
    try:
        generate_cscope(args.index_file)
        generate_ctags(args.index_file)
    except subprocess.CalledProcessError as e:
        logger.error(f"Command execution failed: {e}")
        return

    logger.info("All operations completed successfully!")


if __name__ == "__main__":
    main()

