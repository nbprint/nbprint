"""Tests for the ingestion-time diagnostics that flag inert authoring.

An overlay that matches nothing, or a reserved-namespace tag nbprint does not
consume, both render exactly like a correct document minus the formatting.
These warnings are the only signal an author gets.
"""

import logging

from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

from nbprint import CellMatcher, LayoutOverlay, Overlay, PageBoxOverlay
from nbprint.config.core.config import Configuration
from nbprint.config.core.content import ContentMarshall
from nbprint.config.overlay import describe_matcher


def ingest(caplog, *, cells, **values):
    """Run cell ingestion and return the warnings it emitted."""
    nb = new_notebook()
    nb.cells = cells
    values.setdefault("content", ContentMarshall())
    with caplog.at_level(logging.WARNING):
        Configuration._process_cells(values, nb)
    return [r.getMessage() for r in caplog.records if r.levelno >= logging.WARNING]


class TestOverlayMatchedNothing:
    def test_formatting_overlay_matching_no_cells_warns(self, caplog):
        warnings = ingest(
            caplog,
            cells=[new_markdown_cell(source="A", metadata={"tags": ["present"]})],
            overlays=[Overlay(match=CellMatcher(tag="absent"), css=":scope { color: red; }")],
        )
        assert any("matched no cells" in w and "'absent'" in w for w in warnings)

    def test_formatting_overlay_that_matches_is_quiet(self, caplog):
        warnings = ingest(
            caplog,
            cells=[new_markdown_cell(source="A", metadata={"tags": ["present"]})],
            overlays=[Overlay(match=CellMatcher(tag="present"), css=":scope { color: red; }")],
        )
        assert not any("matched no cells" in w for w in warnings)

    def test_layout_overlay_matching_no_cells_warns(self, caplog):
        warnings = ingest(
            caplog,
            cells=[new_markdown_cell(source="A", metadata={"tags": ["present"]})],
            layout_overlays=[LayoutOverlay(match=CellMatcher(tag="absent"), layout="row")],
        )
        assert any("layout overlay" in w and "matched no cells" in w for w in warnings)

    def test_page_box_overlay_matching_no_cells_warns(self, caplog):
        warnings = ingest(
            caplog,
            cells=[new_markdown_cell(source="A", metadata={"tags": ["present"]})],
            layout_overlays=[PageBoxOverlay(match=CellMatcher(tag="absent"), layout="columns-2")],
        )
        assert any("layout overlay" in w and "matched no cells" in w for w in warnings)

    def test_layout_overlay_that_matches_is_quiet(self, caplog):
        warnings = ingest(
            caplog,
            cells=[
                new_markdown_cell(source="A", metadata={"tags": ["pair"]}),
                new_markdown_cell(source="B", metadata={"tags": ["pair"]}),
            ],
            layout_overlays=[LayoutOverlay(match=CellMatcher(tag="pair"), layout="row")],
        )
        assert not any("matched no cells" in w for w in warnings)

    def test_only_the_unmatched_overlay_is_reported(self, caplog):
        warnings = ingest(
            caplog,
            cells=[new_markdown_cell(source="A", metadata={"tags": ["present"]})],
            overlays=[
                Overlay(match=CellMatcher(tag="present"), css=":scope { color: red; }"),
                Overlay(match=CellMatcher(tag="absent"), css=":scope { color: blue; }"),
            ],
        )
        reported = [w for w in warnings if "matched no cells" in w]
        assert len(reported) == 1
        assert "'absent'" in reported[0]


class TestReservedTags:
    def test_unknown_section_tag_warns(self, caplog):
        warnings = ingest(
            caplog,
            cells=[new_markdown_cell(source="A", metadata={"tags": ["nbprint:section:frontmater"]})],
        )
        assert any("frontmater" in w and "not a section" in w for w in warnings)

    def test_known_section_tag_is_quiet(self, caplog):
        warnings = ingest(
            caplog,
            cells=[new_markdown_cell(source="A", metadata={"tags": ["nbprint:section:frontmatter"]})],
        )
        assert not any("not a section" in w for w in warnings)

    def test_unconsumed_reserved_tag_warns(self, caplog):
        warnings = ingest(
            caplog,
            cells=[new_code_cell(source="x = 1", metadata={"tags": ["nbprint:pagebox"]})],
        )
        assert any("nbprint:pagebox" in w and "does not consume" in w for w in warnings)

    def test_plain_tags_are_never_flagged(self, caplog):
        warnings = ingest(
            caplog,
            cells=[new_code_cell(source="x = 1", metadata={"tags": ["pair-ic", "chart"]})],
        )
        assert not any("does not consume" in w for w in warnings)

    def test_recognised_reserved_prefixes_are_quiet(self, caplog):
        warnings = ingest(
            caplog,
            cells=[
                new_code_cell(source="x = 1", metadata={"tags": ["nbprint:content:cover"]}),
                new_code_cell(source="y = 2", metadata={"tags": ["nbprint:page"]}),
                new_code_cell(source="z = 3", metadata={"tags": ["nbprint:output:pdf"]}),
            ],
        )
        assert not any("does not consume" in w for w in warnings)


class TestDescribeMatcher:
    def test_lists_only_the_criteria_that_are_set(self):
        assert describe_matcher(CellMatcher(tag="ic", cell_type="code")) == "tag='ic', cell_type='code'"

    def test_empty_matcher_is_described_as_matching_everything(self):
        assert describe_matcher(CellMatcher()) == "<matches every cell>"
