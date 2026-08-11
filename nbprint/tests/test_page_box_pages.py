"""Per-page ``@page`` rules emitted for page boxes carrying page-level overrides."""

import pytest

from nbprint.config.content import ContentCode
from nbprint.config.content.page_box import ContentPageBox
from nbprint.config.core.content import ContentMarshall
from nbprint.config.core.page import PageGlobal


class _Config:
    """Stands in for a ``Configuration``; the page model only reads ``content``."""

    def __init__(self, content) -> None:
        self.content = content


def _rendered(*boxes, page: PageGlobal | None = None) -> str:
    content = ContentMarshall()
    content.middlematter = list(boxes)
    page = page or PageGlobal()
    page.render(config=_Config(content))
    return page.css


@pytest.fixture
def landscape_box():
    return ContentPageBox(page_orientation="landscape", content=[ContentCode(content="A")])


class TestPageBoxPageRules:
    def test_emits_a_named_rule_and_routes_the_box_to_it(self, landscape_box):
        css = _rendered(landscape_box)
        name = f"nbprint-page-box-{landscape_box._id}"
        assert f"@page {name} {{ size: letter landscape; }}" in css
        assert f'[data-nbprint-page-box="{landscape_box._id}"] {{ page: {name}; }}' in css

    def test_a_box_without_overrides_gets_no_rule(self):
        css = _rendered(ContentPageBox(layout="columns-2", content=[ContentCode(content="A")]))
        assert "nbprint-page-box-" not in css

    def test_margins_are_included(self):
        box = ContentPageBox(page_margins="0.5in 1in", content=[ContentCode(content="A")])
        assert "margin: 0.5in 1in;" in _rendered(box)

    def test_size_falls_back_to_the_document_default(self, landscape_box):
        """Orientation alone is meaningless without a size, so the global one is carried in."""
        assert "size: letter landscape;" in _rendered(landscape_box)

    def test_explicit_size_wins(self):
        box = ContentPageBox(page_size="A4", content=[ContentCode(content="A")])
        assert "size: A4 portrait;" in _rendered(box)

    def test_nested_boxes_are_found(self):
        inner = ContentPageBox(page_orientation="landscape", content=[ContentCode(content="A")])
        outer = ContentPageBox(content=[inner])
        assert f"@page nbprint-page-box-{inner._id}" in _rendered(outer)

    def test_rendering_twice_does_not_duplicate_rules(self, landscape_box):
        content = ContentMarshall()
        content.middlematter = [landscape_box]
        page = PageGlobal()
        config = _Config(content)
        page.render(config=config)
        page.render(config=config)
        assert page.css.count(f"@page nbprint-page-box-{landscape_box._id}") == 1

    def test_no_config_is_harmless(self):
        """``render`` is called without a config in standalone/test paths."""
        page = PageGlobal()
        page.render()
        assert "nbprint-page-box-" not in page.css

    def test_the_document_default_rule_still_comes_first(self, landscape_box):
        css = _rendered(landscape_box)
        assert css.index("@page { size:") < css.index("@page nbprint-page-box-")
