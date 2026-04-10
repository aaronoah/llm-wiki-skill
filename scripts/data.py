#!/usr/bin/env python3
"""
LLM Wiki Skill - A CLI based agentic skill

This script contains all data classes that enable the function calls.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class WikiFileMetadata:
    """Metadata for a wiki file snapshot.

    Attributes:
        file_name: The Markdown file name.
        mtime: The file modification time as a Unix timestamp, if the file exists.
        checksum: The file content checksum, if the file exists.
    """

    file_name: str
    mtime: float | None
    checksum: str | None