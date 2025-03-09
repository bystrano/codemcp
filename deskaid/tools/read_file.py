#!/usr/bin/env python3

import os
from typing import Optional

from ..common import (
    MAX_LINE_LENGTH,
    MAX_LINES_TO_READ,
    MAX_OUTPUT_SIZE,
    is_image_file,
    normalize_file_path,
)


def read_file_content(
    file_path: str, offset: Optional[int] = None, limit: Optional[int] = None
) -> str:
    """Read a file's content with optional offset and limit.

    Args:
        file_path: The absolute path to the file to read
        offset: The line number to start reading from (1-indexed)
        limit: The number of lines to read

    Returns:
        The file content as a string, or an error message
    """
    try:
        # Normalize the file path
        full_file_path = normalize_file_path(file_path)

        # Validate the file path
        if not os.path.exists(full_file_path):
            # Try to find a similar file (stub - would need implementation)
            return f"Error: File does not exist: {file_path}"

        if os.path.isdir(full_file_path):
            return f"Error: Path is a directory, not a file: {file_path}"

        # Check file size before reading
        file_size = os.path.getsize(full_file_path)
        if file_size > MAX_OUTPUT_SIZE and not offset and not limit:
            return f"Error: File content ({file_size // 1024}KB) exceeds maximum allowed size ({MAX_OUTPUT_SIZE // 1024}KB). Please use offset and limit parameters to read specific portions of the file."

        # Handle text files
        with open(full_file_path, "r", encoding="utf-8", errors="replace") as f:
            # Get total line count
            all_lines = f.readlines()
            total_lines = len(all_lines)

            # Handle offset (convert from 1-indexed to 0-indexed)
            line_offset = 0 if offset is None else (offset - 1 if offset > 0 else 0)

            # Apply offset and limit
            if line_offset >= total_lines:
                return f"Error: Offset {offset} is beyond the end of the file (total lines: {total_lines})"

            max_lines = MAX_LINES_TO_READ if limit is None else limit
            selected_lines = all_lines[line_offset : line_offset + max_lines]

            # Process lines (truncate long lines)
            processed_lines = []
            for line in selected_lines:
                if len(line) > MAX_LINE_LENGTH:
                    processed_lines.append(
                        line[:MAX_LINE_LENGTH] + "... (line truncated)"
                    )
                else:
                    processed_lines.append(line)

            # Add line numbers (1-indexed)
            numbered_lines = []
            for i, line in enumerate(processed_lines):
                line_num = line_offset + i + 1  # 1-indexed line number
                numbered_lines.append(f"{line_num:6}\t{line.rstrip()}")

            content = "\n".join(numbered_lines)

            # Add a message if we truncated the file
            if line_offset + len(processed_lines) < total_lines:
                content += f"\n... (file truncated, showing {len(processed_lines)} of {total_lines} lines)"

            return content
    except Exception as e:
        return f"Error reading file: {str(e)}"
