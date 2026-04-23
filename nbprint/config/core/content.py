from typing import Generator, Literal

from pydantic import Field, PrivateAttr, model_validator

from nbprint.config.base import BaseModel
from nbprint.config.common import Style
from nbprint.config.content import Content

__all__ = ("SECTION_GROUPS", "SECTION_ORDER", "ContentMarshall", "Section")


"""
We make the following structural assumptions about a book/report.
Hopefully it is general enough to cover most use cases.

prematter: content that is hidden and executed prior to the initial construction of the report outputs.
covermatter: content that appears on the cover page. for physical books, this corresponds to the front cover.
frontmatter:
    title: content that appears on the title page. for physical books, this corresponds to the first page inside the cover.
    copyright: content that appears on the copyright page. for physical books, this corresponds to the page after the title page.
    dedication: content that appears on the dedication page. for physical books,
        this corresponds to the page after the copyright page.
    table_of_contents: content that appears on the table of contents page. for physical books,
        this corresponds to the page after the dedication page.
    frontmatter: content that appears before the main body of the report/book. typically includes preface,
        foreword, introduction, etc.
middlematter:
    middlematter: content that forms the main body of the report/book. typically includes chapters/sections.
    middlematter_separators: if middlematter is a list of lists of content,
        we can treat the first content in each sublist as a separator (e.g., chapter title page).
endmatter:
    appendix: content that appears in the appendix. typically includes supplementary material, data, etc.
    index: content that appears in the index. typically includes an alphabetical list of topics covered in the report/book.
    endmatter: content that appears after the main body of the report/book. typically includes bibliography,
        glossary, colophon, etc.
rearmatter: content that appears on the back cover. for physical books, this corresponds to the back cover.
"""

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

# Map each section to its parent group
SECTION_GROUPS: dict[str, str] = {
    "prematter": "prematter",
    "covermatter": "covermatter",
    "title": "frontmatter",
    "copyright": "frontmatter",
    "dedication": "frontmatter",
    "table_of_contents": "frontmatter",
    "frontmatter": "frontmatter",
    "middlematter": "middlematter",
    "middlematter_separators": "middlematter",
    "appendix": "endmatter",
    "index": "endmatter",
    "endmatter": "endmatter",
    "rearmatter": "rearmatter",
}


class ContentMarshall(BaseModel):
    # Prematter
    prematter: list[Content] = Field(
        default_factory=list, description="Content that is hidden and executed prior to the initial construction of the report outputs."
    )

    # Covermatter
    covermatter: list[Content] = Field(default_factory=list, description="Content that appears on the cover page.")

    # Frontmatter
    frontmatter: list[Content] = Field(default_factory=list)
    title: list[Content] = Field(default_factory=list, description="Content that appears on the title page.")
    copyright: list[Content] = Field(default_factory=list, description="Content that appears on the copyright page.")
    dedication: list[Content] = Field(default_factory=list, description="Content that appears on the dedication page.")
    table_of_contents: list[Content] = Field(default_factory=list, description="Content that appears on the table of contents page.")

    # Middlematter
    middlematter: list[Content] = Field(default_factory=list, description="Content that forms the main body of the report/book.")
    middlematter_separators: list[Content] = Field(
        default_factory=list,
        description="If middlematter is a list of lists of content, we can treat the first content in each sublist as a separator (e.g., chapter title page).",
    )

    # Endmatter
    endmatter: list[Content] = Field(
        default_factory=list,
        description="Content that appears after the main body of the report/book. typically includes bibliography, glossary, colophon, etc.",
    )
    appendix: list[Content] = Field(
        default_factory=list, description="Content that appears in the appendix. typically includes supplementary material, data, etc."
    )
    index: list[Content] = Field(
        default_factory=list, description="Content that appears in the index. typically includes an alphabetical list of topics covered in the report/book."
    )

    # Rearmatter
    rearmatter: list[Content] = Field(
        default_factory=list, description="Content that appears on the back cover. for physical books, this corresponds to the back cover."
    )

    # Per-section default styles — applied to any cell in that section
    # whose own ``style`` field does not override the same property.
    section_styles: dict[Section, Style] = Field(
        default_factory=dict,
        description="Default Style per section; inherited by cells in that section unless overridden.",
    )

    _all: list[Content] = PrivateAttr(default_factory=list)
    _prematter: list[Content] = PrivateAttr(default_factory=list)
    _covermatter: list[Content] = PrivateAttr(default_factory=list)
    _frontmatter: list[Content] = PrivateAttr(default_factory=list)
    _middlematter: list[Content] = PrivateAttr(default_factory=list)
    _endmatter: list[Content] = PrivateAttr(default_factory=list)
    _rearmatter: list[Content] = PrivateAttr(default_factory=list)

    @model_validator(mode="after")
    def _setup_groups(self) -> "ContentMarshall":
        # Populate per-group aggregations
        self._prematter = self.prematter
        self._covermatter = self.covermatter
        self._frontmatter = self.title + self.copyright + self.dedication + self.table_of_contents + self.frontmatter
        self._middlematter = self.middlematter + self.middlematter_separators
        self._endmatter = self.appendix + self.index + self.endmatter
        self._rearmatter = self.rearmatter

        # Full document order
        self._all = self._prematter + self._covermatter + self._frontmatter + self._middlematter + self._endmatter + self._rearmatter
        return self

    def sections(self) -> Generator[tuple[str, str, list[Content]], None, None]:
        """Yield (section_name, group_name, contents) for non-empty sections in document order."""
        for section in SECTION_ORDER:
            contents = getattr(self, section)
            if contents:
                yield section, SECTION_GROUPS[section], contents

    # override indexing to return from _all
    def __getitem__(self, index: int) -> Content:
        return self._all[index]

    @property
    def all(self) -> list[Content]:
        return self._all
