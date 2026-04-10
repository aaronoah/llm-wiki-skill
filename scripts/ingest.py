#!/usr/bin/env python3
"""
LLM Wiki Skill - A CLI based agentic skill

This script creates data structures to help ingestion process
"""

from pathlib import Path
from data import WikiFileMetadata
from datetime import datetime
import hashlib
import sys


def collect_raw_file_metadata(wiki_dir: str | Path) -> list[WikiFileMetadata]:
    """Collect metadata for Markdown files under ``raw/``.

    Args:
        wiki_dir: Path to the wiki root directory.

    Returns:
        A sorted list of ``WikiFileMetadata`` entries for Markdown files found
        anywhere under the wiki's ``raw/`` directory.
    """
    raw_root = Path(wiki_dir).expanduser().resolve()
    raw_metadata: list[WikiFileMetadata] = []

    for path in sorted(raw_root.rglob("*")):
        if not path.is_file():
            continue
        raw_metadata.append(
            WikiFileMetadata(
                file_name=path.name,
                mtime=path.stat().st_mtime,
                checksum=hashlib.sha256(path.read_bytes()).hexdigest(),
            )
        )

    return raw_metadata


def parse_iso_to_mtime(iso_str: str) -> float:
    return datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S").timestamp()


def format_mtime_iso(mtime: float) -> str:
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%dT%H:%M:%S")


if __name__ == "__main__":
    option = sys.argv[1]

    match option:
        case "--collect":
            wiki_dir = sys.argv[2]
            print(collect_raw_file_metadata(wiki_dir=wiki_dir))
        case "--iso-to-mtime":
            iso_str = sys.argv[2]
            print(parse_iso_to_mtime(iso_str=iso_str))