from typing import Generator, Literal

from pydantic import Field, PrivateAttr, model_validator

from nbprint.config.base import BaseModel
from nbprint.config.common import Style
from nbprint.config.content import Content, ContentTableOfContents

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

    # Phase 8.2 — auto-generate a ``ContentTableOfContents`` into the
    # ``table_of_contents`` section when that section is left empty.  The
    # JS-side component (``createToc``) populates the rendered TOC from
    # middlematter headings at paged.js time.
    auto_table_of_contents: bool = Field(
        default=False,
        description=("If True and ``table_of_contents`` is empty, auto-inject a single ``ContentTableOfContents`` entry so the JS TOC generator runs."),
    )

    # Phase 8.1 — when ``middlematter`` is supplied as a list-of-lists, each
    # sublist is treated as a chapter with its first element promoted to
    # ``middlematter_separators``.  The resulting chapter sizes (items per
    # chapter *after* separator extraction) are stashed here so
    # ``_setup_groups`` can interleave separators with their chapter bodies
    # rather than appending all separators at the end.
    middlematter_chapter_sizes: list[int] | None = Field(
        default=None,
        description=("Per-chapter item counts for middlematter when supplied as a list-of-lists. Populated automatically; rarely set by hand."),
    )

    _all: list[Content] = PrivateAttr(default_factory=list)
    _prematter: list[Content] = PrivateAttr(default_factory=list)
    _covermatter: list[Content] = PrivateAttr(default_factory=list)
    _frontmatter: list[Content] = PrivateAttr(default_factory=list)
    _middlematter: list[Content] = PrivateAttr(default_factory=list)
    _endmatter: list[Content] = PrivateAttr(default_factory=list)
    _rearmatter: list[Content] = PrivateAttr(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _normalize_nested_middlematter(cls, values: object) -> object:
        """Split a list-of-lists ``middlematter`` into flat content + separators.

        Each sublist is treated as a chapter. Its first element becomes a
        chapter separator (landing in ``middlematter_separators``), and the
        remainder is flattened into ``middlematter``.  Per-chapter sizes are
        recorded in ``middlematter_chapter_sizes`` so the render order can
        interleave separators with their chapter bodies in ``_setup_groups``.
        """
        if not isinstance(values, dict):
            return values
        mid = values.get("middlematter")
        if not (mid and isinstance(mid, list) and all(isinstance(item, list) for item in mid)):
            return values

        separators: list = []
        flat: list = []
        chapter_sizes: list[int] = []
        for sublist in mid:
            if not sublist:
                chapter_sizes.append(0)
                continue
            separators.append(sublist[0])
            rest = list(sublist[1:])
            chapter_sizes.append(len(rest))
            flat.extend(rest)

        # Only auto-populate separators if the user didn't also pass them.
        if not values.get("middlematter_separators"):
            values["middlematter_separators"] = separators
        values["middlematter"] = flat
        values["middlematter_chapter_sizes"] = chapter_sizes
        return values

    @model_validator(mode="after")
    def _setup_groups(self) -> "ContentMarshall":
        # 8.2 — inject a TOC placeholder when requested and the section is empty
        if self.auto_table_of_contents and not self.table_of_contents:
            self.table_of_contents = [ContentTableOfContents()]

        # Populate per-group aggregations
        self._prematter = self.prematter
        self._covermatter = self.covermatter
        self._frontmatter = self.title + self.copyright + self.dedication + self.table_of_contents + self.frontmatter
        self._middlematter = self._compose_middlematter()
        self._endmatter = self.appendix + self.index + self.endmatter
        self._rearmatter = self.rearmatter

        # Full document order
        self._all = self._prematter + self._covermatter + self._frontmatter + self._middlematter + self._endmatter + self._rearmatter
        return self

    def _compose_middlematter(self) -> list[Content]:
        """Build middlematter in render order.

        * When ``middlematter_chapter_sizes`` is set (list-of-lists input),
          interleave separators with their chapter bodies:
          ``[sep0, *chap0, sep1, *chap1, ...]``.
        * Otherwise, preserve the legacy behavior of appending all separators
          after the flat middlematter body.
        """
        sizes = self.middlematter_chapter_sizes
        if not sizes:
            return self.middlematter + self.middlematter_separators

        out: list[Content] = []
        cursor = 0
        for i, size in enumerate(sizes):
            if i < len(self.middlematter_separators):
                out.append(self.middlematter_separators[i])
            out.extend(self.middlematter[cursor : cursor + size])
            cursor += size
        # Any trailing separators past the last chapter (unusual but allowed)
        if len(self.middlematter_separators) > len(sizes):
            out.extend(self.middlematter_separators[len(sizes) :])
        # Any middlematter items past declared chapter sizes
        if cursor < len(self.middlematter):
            out.extend(self.middlematter[cursor:])
        return out

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
