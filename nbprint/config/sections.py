from typing import Literal

__all__ = ("SECTION_ORDER", "Section")


Section = Literal[
    "prematter",
    "covermatter",
    "frontmatter",
    "title",
    "copyright",
    "dedication",
    "table_of_contents",
    "middlematter",
    "middlematter_separators",
    "endmatter",
    "appendix",
    "index",
    "rearmatter",
]


# Document order for section iteration
SECTION_ORDER: list[str] = [
    "prematter",
    "covermatter",
    "title",
    "copyright",
    "dedication",
    "table_of_contents",
    "frontmatter",
    "middlematter",
    "middlematter_separators",
    "appendix",
    "index",
    "endmatter",
    "rearmatter",
]
