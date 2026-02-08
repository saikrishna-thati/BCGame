import re
import os
from pathlib import Path

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string to be safe for use as a filename.
    Removes characters that are unsafe or could lead to path traversal.
    """
    # Remove directory traversal
    filename = os.path.basename(filename)
    # Replace unsafe characters with underscore
    filename = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
    # Ensure it's not empty
    if not filename:
        return "untitled"
    return filename

def ensure_safe_path(base_dir: str, relative_path: str) -> str:
    """
    Ensure the path is strictly within the base directory.
    """
    base = Path(base_dir).resolve()
    target = (base / relative_path).resolve()

    if not str(target).startswith(str(base)):
        raise ValueError(f"Path traversal detected: {relative_path}")

    return str(target)
