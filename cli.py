"""CLI interface for GEO Auditor."""

import argparse
import asyncio
from pathlib import Path
from typing import List


def parse_args(argv=None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="eCommerce GEO Auditor - Audit product pages for AI agent optimization"
    )

    parser.add_argument(
        "--urls-file",
        help="Path to file with URLs (one per line)"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive URL input mode"
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config file"
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory"
    )

    return parser.parse_args(argv)


def interactive_url_input() -> List[str]:
    """Prompt user to enter URLs interactively."""
    print("Enter URLs to audit (one per line, empty line to finish):")
    urls = []

    while True:
        url = input("> ").strip()
        if not url:
            break
        urls.append(url)

    return urls


def load_urls_from_file(file_path: str) -> List[str]:
    """Load URLs from text file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"URLs file not found: {file_path}")

    urls = []
    for line in path.read_text().splitlines():
        url = line.strip()
        if url and not url.startswith("#"):
            urls.append(url)

    return urls


async def main():
    """Main CLI entry point."""
    args = parse_args()

    # Get URLs
    if args.interactive:
        urls = interactive_url_input()
    elif args.urls_file:
        urls = load_urls_from_file(args.urls_file)
    else:
        print("Error: Specify --urls-file or --interactive")
        return 1

    if not urls:
        print("No URLs provided")
        return 1

    print(f"\\nReady to audit {len(urls)} URLs")
    print("Implementation: Run audit pipeline here")

    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
