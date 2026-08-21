from typing import TYPE_CHECKING, Iterator, Tuple

from nbformat import NotebookNode
from pydantic import Field, field_validator, model_validator

from nbprint.config.base import BaseModel, Role, _append_or_extend
from nbprint.config.common import PageOrientation, PageSize, Style
from nbprint.config.exceptions import NBPrintNullCellError

from .content import Section


def _iter_page_boxes(content) -> "Iterator":
    """Yield every ``ContentPageBox`` in a ``ContentMarshall``, including nested ones."""
    from nbprint.config.content.page_box import ContentPageBox

    from .content import SECTION_ORDER

    def walk(node) -> "Iterator":
        if isinstance(node, ContentPageBox):
            yield node
        children = getattr(node, "content", None)
        if isinstance(children, list):
            for child in children:
                yield from walk(child)

    for section in SECTION_ORDER:
        for item in getattr(content, section, None) or []:
            yield from walk(item)


PAGE_REGION_ATTRS = (
    "top",
    "top_left",
    "top_left_corner",
    "top_right",
    "top_right_corner",
    "bottom",
    "bottom_left",
    "bottom_left_corner",
    "bottom_right",
    "bottom_right_corner",
    "left",
    "left_top",
    "left_bottom",
    "right",
    "right_top",
    "right_bottom",
)

# The four edge regions whose CSS name is not their attribute name.
_REGION_CSS_NAMES = {
    "top": "top-center",
    "bottom": "bottom-center",
    "left": "left-center",
    "right": "right-center",
}


def _region_css_name(attr: str) -> str:
    return _REGION_CSS_NAMES.get(attr, attr.replace("_", "-"))


if TYPE_CHECKING:
    from .config import Configuration

_FIRST_PAGE_SUPPRESSION_MARKER = ".pagedjs_first_page .pagedjs_margin-"

__all__ = (
    "Page",
    "PageGlobal",
    "PageNumber",
    "PageRegion",
    "PageRegionContent",
    "RunningElement",
)


class PageRegionContent(BaseModel):
    content: str | None = ""

    # common
    tags: list[str] = Field(default_factory=list)
    role: Role = Role.PAGE
    ignore: bool = True

    def __str__(self) -> str:
        if self.content:
            return f"content: {self.content};"
        return ""

    @field_validator("tags", mode="after")
    @classmethod
    def _ensure_tags(cls, v: list[str]) -> list[str]:
        if "nbprint:page" not in v:
            v.append("nbprint:page")
        return v

    def region_css(self) -> str:
        """CSS this content needs *outside* its ``@page`` block.

        Most region content is self-contained: a string, a counter. Content
        sourced from the document body is not, because the source element has
        to be styled where it lives.
        """
        return ""


class PageNumber(PageRegionContent):
    content: str | None = "counter(page)"


class RunningElement(PageRegionContent):
    """Region content taken from an element that lives in the document body.

    Paged.js lifts an element out of the flow when it carries
    ``position: running(<name>)``, and a margin box pulls it back in with
    ``content: element(<name>)``. Nothing here was expressible before, so every
    consumer hand-rolled the pair -- and each one also had to rediscover that
    the source element must be hidden when the document is *not* paginated,
    since ``position: running()`` means nothing outside Paged.js and the element
    would otherwise render inline in the body.

    ``selector`` addresses the source element, e.g. ``.footer-logo``.
    """

    name: str
    selector: str

    @model_validator(mode="after")
    def _default_content_to_the_element(self) -> "RunningElement":
        if not self.content:
            self.content = f"element({self.name})"
        return self

    def region_css(self) -> str:
        # The `position: running()` rule has to be matchable against the parsed
        # content fragment, because that is where Paged.js hides the source
        # element (it sets an inline `display: none` on everything the rule
        # selects). The fragment holds the body's *children*, so any selector
        # rooted at `body` matches nothing there, the element is never hidden,
        # and it paints in the normal flow while its clone appears in the margin
        # box. For the same reason the rule must not force the element visible:
        # a `display: block !important` here would outrank the inline
        # `display: none` Paged.js relies on. Hiding for the unpaginated case is
        # left to a `body`-rooted rule, which is only ever matched against the
        # live document.
        return f"\n{self.selector} {{ position: running({self.name}); }}\nbody:not(.pagedjs) {self.selector} {{ display: none !important; }}"


class PageRegion(BaseModel):
    _region: str = ""
    content: PageRegionContent | None = Field(default_factory=PageNumber)
    style: Style | None = None

    css: str = ""

    # common
    tags: list[str] = Field(default_factory=list)
    role: Role = Role.PAGE
    ignore: bool = True

    @field_validator("tags", mode="after")
    @classmethod
    def _ensure_tags(cls, v: list[str]) -> list[str]:
        if "nbprint:page" not in v:
            v.append("nbprint:page")
        return v

    def generate(self, metadata: dict, config: "Configuration", parent: "BaseModel", attr: str, **_) -> NotebookNode:
        cell = super().generate(metadata=metadata, config=config, parent=parent, attr=attr)
        cell.metadata.tags.append(f"nbprint:page:{attr}")
        return cell


class Page(BaseModel):
    top: PageRegion | None = None
    top_left: PageRegion | None = None
    top_left_corner: PageRegion | None = None
    top_right: PageRegion | None = None
    top_right_corner: PageRegion | None = None
    bottom: PageRegion | None = None
    bottom_left: PageRegion | None = None
    bottom_left_corner: PageRegion | None = None
    bottom_right: PageRegion | None = None
    bottom_right_corner: PageRegion | None = None
    left: PageRegion | None = None
    left_top: PageRegion | None = None
    left_bottom: PageRegion | None = None
    right: PageRegion | None = None
    right_top: PageRegion | None = None
    right_bottom: PageRegion | None = None

    counter_reset: bool = False
    counter_style: str | None = None

    # The first page of a report is nearly always a cover, and a running footer
    # or header across a cover looks like a mistake. Suppressing it is otherwise
    # a hand-written rule against Paged.js' internal margin-box class names.
    suppress_first_page_regions: bool = False

    size: PageSize | Tuple[float, float] | None = Field(default=PageSize.letter)
    orientation: PageOrientation | None = Field(default=PageOrientation.portrait)

    css: str = ""

    @model_validator(mode="after")
    def _assemble_page_css(self) -> "Page":
        """Collect the CSS that has to sit outside any ``@page`` block or ``@scope``.

        Two things land here rather than on the region itself. A region's CSS is
        emitted as *cell* CSS, which the template wraps in ``@scope``, so a rule
        addressing ``body`` or an element elsewhere in the document can never
        match from there. And ``Configuration.page`` is typed as ``Page``, so a
        consumer subclassing ``Page`` never reaches ``PageGlobal.render`` --
        anything emitted only from there would silently do nothing for them.
        """
        for attr in PAGE_REGION_ATTRS:
            region = getattr(self, attr, None)
            if region is None or region.content is None:
                continue

            # A region handed over as a field default -- `bottom_left: PageRegion
            # = Field(default=Footer())` on a Page subclass -- never passes
            # through the `mode="before"` validator that names it and attaches
            # its margin-box rule, because Pydantic does not validate defaults.
            # Without that rule the box is never declared, so nothing consumes
            # the region's content: a running element in particular is then left
            # in the flow with no margin box to be lifted into. This validator
            # does run for defaults, so it is the one place that can repair them.
            region_name = _region_css_name(attr)
            if not region._region:
                region._region = region_name
            if f"@{region_name} {{" not in region.css:
                region.css += f"@page {{ @{region_name} {{ {region.content} }} }}"

            extra = region.content.region_css()
            if extra and extra not in self.css:
                self.css += extra

        if self.suppress_first_page_regions and _FIRST_PAGE_SUPPRESSION_MARKER not in self.css:
            selectors = ", ".join(f".pagedjs_first_page .pagedjs_margin-{edge}" for edge in ("top", "bottom", "left", "right"))
            self.css += f"\n{selectors} {{ display: none !important; }}"
        return self

    @classmethod
    def convert_region_from_obj(cls, v, region) -> PageRegion:
        ret = BaseModel._to_type(v, PageRegion)
        ret._region = region
        base_css_scope = "@page {{ @{region} {{ {content} }} }}".format(region=region, content=str(ret.content or ""))
        ret.css += base_css_scope
        return ret

    @field_validator("top", mode="before")
    @classmethod
    def convert_top_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "top-center")

    @field_validator("top_left", mode="before")
    @classmethod
    def convert_top_left_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "top-left")

    @field_validator("top_left_corner", mode="before")
    @classmethod
    def convert_top_left_corner_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "top-left-corner")

    @field_validator("top_right", mode="before")
    @classmethod
    def convert_top_right_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "top-right")

    @field_validator("top_right_corner", mode="before")
    @classmethod
    def convert_top_right_corner_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "top-right-corner")

    @field_validator("bottom", mode="before")
    @classmethod
    def convert_bottom_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "bottom-center")

    @field_validator("bottom_left", mode="before")
    @classmethod
    def convert_bottom_left_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "bottom-left")

    @field_validator("bottom_left_corner", mode="before")
    @classmethod
    def convert_bottom_left_corner_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "bottom-left-corner")

    @field_validator("bottom_right", mode="before")
    @classmethod
    def convert_bottom_right_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "bottom-right")

    @field_validator("bottom_right_corner", mode="before")
    @classmethod
    def convert_bottom_right_corner_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "bottom-right-corner")

    @field_validator("left", mode="before")
    @classmethod
    def convert_left_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "left-center")

    @field_validator("left_top", mode="before")
    @classmethod
    def convert_left_top_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "left-top")

    @field_validator("left_bottom", mode="before")
    @classmethod
    def convert_left_bottom_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "left-bottom")

    @field_validator("right", mode="before")
    @classmethod
    def convert_right_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "right-center")

    @field_validator("right_top", mode="before")
    @classmethod
    def convert_right_top_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "right-top")

    @field_validator("right_bottom", mode="before")
    @classmethod
    def convert_right_bottom_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "right-bottom")

    def generate(self, metadata: dict, config: "Configuration", parent: "BaseModel", attr: str = "page", **_) -> NotebookNode | list[NotebookNode] | None:
        cells = []

        # parent and config should be equal for the global page layout
        assert parent == config

        main_cell = super()._base_generate(metadata=metadata, config=config, parent=config, attr=attr or "page")
        main_cell.metadata.tags.append("nbprint:page")
        main_cell.metadata.nbprint.role = "page"
        main_cell.metadata.nbprint.ignore = True
        cells.append(main_cell)

        for set_attr in PAGE_REGION_ATTRS:
            if getattr(self, set_attr) is not None:
                # pass in `self` as `parent here`
                _append_or_extend(cells, getattr(self, set_attr).generate(metadata=metadata, config=config, parent=self, attr=set_attr))

        for cell in cells:
            if cell is None:
                raise NBPrintNullCellError
        return cells


class PageGlobal(Page):
    pages: dict[Section, "Page"] | None = Field(default_factory=dict)

    css: str = ""

    def render(self, config: "Configuration" = None, **_) -> None:
        if "@page { size:" not in self.css:
            if isinstance(self.size, tuple):
                self.css += f"\n@page {{ size: {self.size[0]}in {self.size[1]}in; }}"
            else:
                self.css += f"\n@page {{ size: {self.size.value} {self.orientation.value}; }}"

        # Generate per-section named page CSS
        for section_name, section_page in (self.pages or {}).items():
            marker = f"@page {section_name}"
            if marker in self.css:
                continue
            inner_rules = []
            for region_attr in PAGE_REGION_ATTRS:
                region = getattr(section_page, region_attr, None)
                if region is not None and region.content:
                    inner_rules.append(f"@{region._region} {{ {region.content} }}")
            if section_page.counter_reset:
                inner_rules.append("counter-reset: page 1;")
            if section_page.counter_style:
                inner_rules.append(f"@bottom-center {{ content: counter(page, {section_page.counter_style}); }}")
            if section_page.css:
                inner_rules.append(section_page.css)
            if inner_rules:
                self.css += f"\n@page {section_name} {{ {' '.join(inner_rules)} }}"
            self.css += f'\n[data-nbprint-section="{section_name}"] {{ page: {section_name}; }}'

        self._render_page_box_rules(config)

    def _render_page_box_rules(self, config: "Configuration" = None) -> None:
        """Emit a named ``@page`` rule for every page-box carrying per-page overrides.

        A page-box cannot emit this itself: cell CSS is wrapped in ``@scope`` by the template, and an
        ``@page`` rule inside a scope does nothing. The page model is the one place that emits unscoped
        CSS, and it renders before content, so it reaches into the already-built content tree the same way
        the per-section rules above work off ``pages``.
        """
        content = getattr(config, "content", None) if config is not None else None
        if content is None:
            return
        for box in _iter_page_boxes(content):
            if not (box.page_size or box.page_orientation or box.page_margins):
                continue
            name = f"nbprint-page-box-{box._id}"
            if f"@page {name}" in self.css:
                continue
            size = box.page_size or self.size
            orientation = box.page_orientation or self.orientation
            rules = [f"size: {size[0]}in {size[1]}in;" if isinstance(size, tuple) else f"size: {size.value} {orientation.value};"]
            if box.page_margins:
                rules.append(f"margin: {box.page_margins};")
            self.css += f"\n@page {name} {{ {' '.join(rules)} }}"
            self.css += f'\n[data-nbprint-page-box="{box._id}"] {{ page: {name}; }}'

    @field_validator("pages", mode="before")
    @classmethod
    def convert_pages_from_obj(cls, v) -> "Page":
        if v is None:
            return []
        if isinstance(v, dict):
            for k, element in v.items():
                if isinstance(element, str):
                    v[k] = Page(type_=element)
                elif isinstance(element, dict):
                    v[k] = BaseModel._to_type(element)
                elif element is None:
                    v[k] = Page()
        return v
