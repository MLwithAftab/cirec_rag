import os
from pathlib import Path
from typing import List

def ensure_directories(paths: List[str]):
    """Create directories if they don't exist"""
    for path in paths:
        os.makedirs(path, exist_ok=True)

def get_file_extension(filename: str) -> str:
    """Get file extension"""
    return Path(filename).suffix.lower()

def is_allowed_file(filename: str) -> bool:
    """Check if file type is allowed"""
    allowed_extensions = {'.pdf', '.docx', '.doc', '.xlsx', '.xls'}
    return get_file_extension(filename) in allowed_extensions