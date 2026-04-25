"""Shared layout-preset CSS used by :class:`ContentPageBox` and the
flex/inline layout containers.

Single source of truth so a tweak to the bare ``display: flex`` rule
(for example) flows to every container that uses it. The page-box
preset CSS in 9.4 reuses these constants verbatim.
"""

from __future__ import annotations

from typing import Callable, Literal

__all__ = (
    "FLEX_COLUMN_CSS",
    "FLEX_ROW_CSS",
    "INLINE_CSS",
    "PAGE_BOX_BASE_CSS",
    "PAGE_BOX_PRESET_BUILDERS",
    "PageBoxLayout",
    "build_page_box_css",
)


# A preset builder takes optional gap/padding/align/justify and returns
# a CSS fragment to append after :scope { ... base ... }.
_Builder = Callable[..., str]


PageBoxLayout = Literal[
    "flow",
    "columns-2",
    "columns-3",
    "grid-2x2",
    "grid-3x2",
    "grid-3x3",
    "grid",
    "flex-row",
    "flex-column",
    "inline",
    "masonry",
    "custom",
]


# ── Bare display rules used by the flex/inline layout containers and
# reused by the page-box presets below. Keeping them here means a
# change to "display: flex" propagates to every consumer. ────────────
FLEX_ROW_CSS = "display: flex; flex-direction: row; break-inside: auto;"
FLEX_COLUMN_CSS = "display: flex; flex-direction: column; break-inside: auto;"
INLINE_CSS = "display: block;"


# Base page-box CSS: at-least-one-page guarantee, hard breaks, and a
# vertical fill so empty pages still render. Preset CSS is appended
# after this base; user-supplied ``css`` (when not the default)
# fully replaces both.
PAGE_BOX_BASE_CSS = (
    ":scope {\n"
    "  break-before: page;\n"
    "  break-after: page;\n"
    "  break-inside: auto;\n"
    "  display: block;\n"
    "  min-height: var(--pagedjs-pagebox-min-height, 100%);\n"
    "}\n"
)


def _join_rules(rules: list[str]) -> str:
    return " ".join(rule for rule in rules if rule)


def _scope_block(rules: list[str]) -> str:
    body = _join_rules(rules)
    return f":scope {{ {body} }}\n" if body else ""


def _columns_builder(count: int) -> _Builder:
    def build(*, gap: str | None, padding: str | None, **_) -> str:
        rules = [f"column-count: {count};", "column-fill: balance;"]
        if gap is not None:
            rules.append(f"column-gap: {gap};")
        if padding is not None:
            rules.append(f"padding: {padding};")
        return _scope_block(rules)

    return build


def _grid_builder(template: str | None) -> _Builder:
    def build(*, gap: str | None, padding: str | None, align: str | None, justify: str | None) -> str:
        rules = ["display: grid;", "grid-auto-flow: row dense;"]
        if template is not None:
            rules.append(f"grid-template-columns: {template};")
        if gap is not None:
            rules.append(f"gap: {gap};")
        if padding is not None:
            rules.append(f"padding: {padding};")
        if align is not None:
            rules.append(f"align-items: {align};")
        if justify is not None:
            rules.append(f"justify-items: {justify};")
        return _scope_block(rules)

    return build


def _grid_areas_builder() -> _Builder:
    """Bare ``display: grid`` for named-area / custom grid templates.

    The actual ``grid-template`` value is supplied separately by the
    page-box (Phase 9.5 will set ``grid_template`` on the box).
    """

    def build(*, gap: str | None, padding: str | None, align: str | None, justify: str | None) -> str:
        rules = ["display: grid;", "grid-auto-flow: row dense;"]
        if gap is not None:
            rules.append(f"gap: {gap};")
        if padding is not None:
            rules.append(f"padding: {padding};")
        if align is not None:
            rules.append(f"align-items: {align};")
        if justify is not None:
            rules.append(f"justify-items: {justify};")
        return _scope_block(rules)

    return build


def _flex_builder(direction_css: str) -> _Builder:
    def build(*, gap: str | None, padding: str | None, align: str | None, justify: str | None) -> str:
        rules = [direction_css]
        if gap is not None:
            rules.append(f"gap: {gap};")
        if padding is not None:
            rules.append(f"padding: {padding};")
        if align is not None:
            rules.append(f"align-items: {align};")
        if justify is not None:
            rules.append(f"justify-content: {justify};")
        return _scope_block(rules)

    return build


def _inline_builder() -> _Builder:
    def build(*, gap: str | None, padding: str | None, **_) -> str:
        rules = [INLINE_CSS]
        if padding is not None:
            rules.append(f"padding: {padding};")
        scope = _scope_block(rules)
        if gap is not None:
            # column-gap doesn't apply to inline-block layouts; emit a
            # margin-left on adjacent siblings as the closest equivalent.
            scope += f":scope > * + * {{ margin-left: {gap}; }}\n"
        return scope

    return build


def _masonry_builder() -> _Builder:
    def build(*, gap: str | None, padding: str | None, **_) -> str:
        # Native CSS masonry where supported; the JS polyfill in
        # measure.js (Phase 9.17) handles browsers without support.
        rules = [
            "display: grid;",
            "grid-template-rows: masonry;",
            "grid-auto-flow: row;",
        ]
        if gap is not None:
            rules.append(f"gap: {gap};")
        if padding is not None:
            rules.append(f"padding: {padding};")
        return _scope_block(rules)

    return build


def _flow_builder() -> _Builder:
    def build(*, gap: str | None, padding: str | None, **_) -> str:
        rules = []
        if padding is not None:
            rules.append(f"padding: {padding};")
        scope = _scope_block(rules)
        if gap is not None:
            # In flow mode, "gap" is a margin between consecutive
            # block children — the closest equivalent in normal flow.
            scope += f":scope > * + * {{ margin-top: {gap}; }}\n"
        return scope

    return build


# Preset name → builder callable. Builders take ``gap``, ``padding``,
# ``align``, ``justify`` keyword args (any may be ``None``) and return
# a string of CSS rules to be appended to ``:scope { ... }``.
PAGE_BOX_PRESET_BUILDERS = {
    "flow": _flow_builder(),
    "columns-2": _columns_builder(2),
    "columns-3": _columns_builder(3),
    "grid-2x2": _grid_builder("repeat(2, 1fr)"),
    "grid-3x2": _grid_builder("repeat(3, 1fr)"),
    "grid-3x3": _grid_builder("repeat(3, 1fr)"),
    "grid": _grid_areas_builder(),
    "flex-row": _flex_builder(FLEX_ROW_CSS),
    "flex-column": _flex_builder(FLEX_COLUMN_CSS),
    "inline": _inline_builder(),
    "masonry": _masonry_builder(),
    # ``custom`` deliberately omitted — caller handles it (no preset
    # CSS appended; user owns ``:scope``).
}


def build_page_box_css(
    layout: PageBoxLayout,
    *,
    gap: str | None,
    padding: str | None,
    align: str | None,
    justify: str | None,
) -> str:
    """Build the CSS for a :class:`ContentPageBox` with the given layout.

    For ``layout="custom"`` returns only the base CSS — the user owns
    ``:scope`` styling. For the ``flow`` preset, returns the base plus
    any margin/padding rules. For all other presets, returns the base
    plus a second ``:scope { ... }`` block carrying the preset rules.
    """
    if layout == "custom":
        return PAGE_BOX_BASE_CSS

    builder = PAGE_BOX_PRESET_BUILDERS[layout]
    preset_css = builder(gap=gap, padding=padding, align=align, justify=justify)
    return PAGE_BOX_BASE_CSS + preset_css
