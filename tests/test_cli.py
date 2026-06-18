import pytest
from pathlib import Path
from cli import parse_args, load_urls_from_file

def test_parse_args_file_mode():
    args = parse_args(["--urls-file", "urls.txt"])
    assert args.urls_file == "urls.txt"
    assert args.interactive is False

def test_parse_args_interactive_mode():
    args = parse_args(["--interactive"])
    assert args.interactive is True

def test_load_urls_from_file(tmp_path):
    urls_file = tmp_path / "urls.txt"
    urls_file.write_text("https://example.com/1\nhttps://example.com/2\n# comment\n")

    urls = load_urls_from_file(str(urls_file))

    assert len(urls) == 2
    assert "https://example.com/1" in urls

def test_load_urls_from_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_urls_from_file("nonexistent.txt")
