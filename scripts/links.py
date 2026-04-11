#!/usr/bin/env python3
"""
LLM Wiki Skill - A CLI based agentic skill

This script reads, parses and extracts properties from the wiki trees so LLM can understand 
and reason quickly
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import sys
from data import WikiFileMetadata


WIKILINK_RE = re.compile(r"\[\[[^\[\]\n]+(?:\|[^\[\]\n]+)?\]\]")


def collect_wikilinks_by_file(wiki_dir: str | Path) -> dict[str, list[WikiFileMetadata]]:
    """Collect wikilink target metadata for every Markdown file.

    Each dictionary key is a source Markdown file name. Each value is the list
    of metadata objects for linked Markdown targets within the same wiki tree.
    If a wikilink target does not resolve to an existing Markdown file, its
    metadata entry is still returned with ``mtime`` and ``checksum`` set to
    ``None``.

    Args:
        wiki_dir: Path to the wiki root directory.

    Returns:
        A dictionary keyed by source file name, where each value is the list of
        ``WikiFileMetadata`` entries for linked target files.
    """
    root = Path(wiki_dir).expanduser().resolve()
    paths_by_name = {path.name: path for path in root.rglob("*.md") if path.is_file()}
    metadata_by_file: dict[str, list[WikiFileMetadata]] = {}

    for path in sorted(root.rglob("*.md")):
        if not path.is_file():
            continue

        source_file = path.name
        wikilinks = WIKILINK_RE.findall(path.read_text(encoding="utf-8"))
        linked_metadata: list[WikiFileMetadata] = []
        for wikilink in wikilinks:
            target = wikilink[2:-2].split("|", 1)[0].strip()
            target_file = target if target.endswith(".md") else f"{target}.md"
            target_path = paths_by_name.get(target_file)
            if target_path is None:
                linked_metadata.append(
                    WikiFileMetadata(
                        file_name=target_file,
                        mtime=None,
                        checksum=None,
                    )
                )
                continue

            linked_metadata.append(
                WikiFileMetadata(
                    file_name=target_path.name,
                    mtime=target_path.stat().st_mtime,
                    checksum=hashlib.sha256(target_path.read_bytes()).hexdigest(),
                )
            )

        metadata_by_file[source_file] = linked_metadata

    return metadata_by_file


def find_broken_wikilinks(
    links_by_file: dict[str, list[WikiFileMetadata]]
) -> dict[str, list[WikiFileMetadata]]:
    """Find wikilink targets that do not exist in the extracted file map.

    Args:
        links_by_file: Mapping of file names to linked target metadata, such as
            the output of ``collect_wikilinks_by_file``.

    Returns:
        A dictionary keyed by source file name. Each value is the list of
        linked metadata entries from that file that do not resolve to any
        existing key in ``links_by_file``.
    """
    existing_files = set(links_by_file)
    broken_by_file: dict[str, list[WikiFileMetadata]] = {}

    for source_file, linked_files in links_by_file.items():
        broken_links = [
            metadata
            for metadata in linked_files
            if metadata.file_name not in existing_files
        ]

        if broken_links:
            broken_by_file[source_file] = broken_links

    return broken_by_file


def find_orphan_pages(links_by_file: dict[str, list[WikiFileMetadata]]) -> list[str]:
    """Return files that are never linked to by any other file.

    A page is considered non-orphan when at least one metadata entry in another
    file resolves to its file name. Self-links do not count.

    Args:
        links_by_file: Mapping of file names to linked target metadata, such as
            the output of ``collect_wikilinks_by_file``.

    Returns:
        A sorted list of file names that have no inbound links from other files.
    """
    existing_files = set(links_by_file)
    linked_files: set[str] = set()

    for source_file, linked_metadata in links_by_file.items():
        for metadata in linked_metadata:
            if metadata.file_name in existing_files and metadata.file_name != source_file:
                linked_files.add(metadata.file_name)

    return sorted(existing_files - linked_files)


if __name__ == "__main__":
    option = sys.argv[1]

    match option:
        case "--orphan":
            wiki_dir = sys.argv[2]
            wikilinks_dict = collect_wikilinks_by_file(wiki_dir=wiki_dir)
            print(find_orphan_pages(links_by_file=wikilinks_dict))
        case "--broken":
            wiki_dir = sys.argv[2]
            wikilinks_dict = collect_wikilinks_by_file(wiki_dir=wiki_dir)
            print(find_broken_wikilinks(links_by_file=wikilinks_dict))