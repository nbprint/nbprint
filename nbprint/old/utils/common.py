import os
from functools import lru_cache


@lru_cache(None)
def in_nbconvert():
    """helper function to check if running in nbprint context"""
    return True if (os.environ.get("NBPRINT_NBCONVERT", "") or os.environ.get("NBPRINT_CONTEXT", "")) else False


@lru_cache(None)
def nbconvert_context():
    """get context in which nbprint is running, either 'pdf' or 'html'"""
    if in_nbconvert():
        if os.environ.get("NBPRINT_CONTEXT", "") == "html":
            return "html"
        return "pdf"
    return ""
