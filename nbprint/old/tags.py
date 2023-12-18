from enum import Enum


class Tags(Enum):
    # Title Page
    TITLEPAGE = "nbprint_title"

    # Header
    LHEAD = "nbprint_lhead"
    CHEAD = "nbprint_chead"
    RHEAD = "nbprint_rhead"
    HEADER = "nbprint_chead"  # center by default

    # Footer
    LFOOT = "nbprint_lfoot"
    CFOOT = "nbprint_cfoot"
    RFOOT = "nbprint_rfoot"
    FOOTER = "nbprint_cfoot"  # center by default

    # Utilities
    NBCONVERT_IGNORE = "nbprint_ignore"
    PARAMETERS = "parameters"  # for Papermill
