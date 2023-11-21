from enum import Enum


class Tags(Enum):
    # Title Page
    TITLEPAGE = "nbcx_title"

    # Header
    LHEAD = "nbcx_lhead"
    CHEAD = "nbcx_chead"
    RHEAD = "nbcx_rhead"
    HEADER = "nbcx_chead"  # center by default

    # Footer
    LFOOT = "nbcx_lfoot"
    CFOOT = "nbcx_cfoot"
    RFOOT = "nbcx_rfoot"
    FOOTER = "nbcx_cfoot"  # center by default

    # Utilities
    NBCONVERT_IGNORE = "nbcx_ignore"
    PARAMETERS = "parameters"  # for Papermill
