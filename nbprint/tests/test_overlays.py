"""Tests for cell-addressing overlays, layout-wrapping overlays, and
section-level default styles."""

from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

from nbprint import CellMatcher, LayoutOverlay, Overlay, Style
from nbprint.config.common import Font
from nbprint.config.content import ContentMarkdown
from nbprint.config.core.config import Configuration
from nbprint.config.core.content import ContentMarshall


class TestCellMatcher:
    """CellMatcher combines index, tag, cell_type, and section criteria."""

    def test_empty_matcher_matches_everything(self):
        m = CellMatcher()
        cell = new_code_cell(source="x = 1", metadata={"tags": []})
        assert m.matches(cell=cell, index=0, section="middlematter") is True
        assert m.matches(cell=cell, index=42, section="covermatter") is True

    def test_index_match(self):
        m = CellMatcher(index=2)
        cell = new_code_cell(source="x = 1", metadata={"tags": []})
        assert m.matches(cell=cell, index=2, section="middlematter") is True
        assert m.matches(cell=cell, index=3, section="middlematter") is False

    def test_tag_match(self):
        m = CellMatcher(tag="chart")
        cell_with = new_code_cell(source="plot()", metadata={"tags": ["chart", "foo"]})
        cell_without = new_code_cell(source="plot()", metadata={"tags": ["foo"]})
        assert m.matches(cell=cell_with, index=0, section="middlematter") is True
        assert m.matches(cell=cell_without, index=0, section="middlematter") is False

    def test_cell_type_match(self):
        m = CellMatcher(cell_type="markdown")
        md_cell = new_markdown_cell(source="# Hello", metadata={"tags": []})
        code_cell = new_code_cell(source="x = 1", metadata={"tags": []})
        assert m.matches(cell=md_cell, index=0, section="middlematter") is True
        assert m.matches(cell=code_cell, index=0, section="middlematter") is False

    def test_section_match(self):
        m = CellMatcher(section="covermatter")
        cell = new_markdown_cell(source="# Cover", metadata={"tags": []})
        assert m.matches(cell=cell, index=0, section="covermatter") is True
        assert m.matches(cell=cell, index=0, section="frontmatter") is False

    def test_compound_matcher_all_must_match(self):
        """All set fields must match (AND semantics)."""
        m = CellMatcher(index=0, cell_type="markdown", section="covermatter")
        cell = new_markdown_cell(source="# Cover", metadata={"tags": []})
        assert m.matches(cell=cell, index=0, section="covermatter") is True
        # Any single mismatch fails the match
        assert m.matches(cell=cell, index=1, section="covermatter") is False
        assert m.matches(cell=cell, index=0, section="frontmatter") is False


class TestOverlayApply:
    """Overlay.apply merges override fields into a Content."""

    def test_css_is_appended_when_existing(self):
        content = ContentMarkdown(content="# Hi", css="existing-css")
        Overlay(css="overlay-css").apply(content)
        assert "existing-css" in content.css
        assert "overlay-css" in content.css

    def test_css_replaces_when_empty(self):
        content = ContentMarkdown(content="# Hi")
        Overlay(css=":scope { color: red; }").apply(content)
        assert content.css == ":scope { color: red; }"

    def test_classname_stacks_as_list(self):
        content = ContentMarkdown(content="# Hi", classname="existing")
        Overlay(classname="overlay").apply(content)
        assert content.classname == ["existing", "overlay"]

    def test_classname_set_when_empty(self):
        content = ContentMarkdown(content="# Hi", classname="")
        Overlay(classname="overlay").apply(content)
        assert content.classname == "overlay"

    def test_attrs_merged(self):
        content = ContentMarkdown(content="# Hi", attrs={"a": "1"})
        Overlay(attrs={"b": "2"}).apply(content)
        assert content.attrs == {"a": "1", "b": "2"}

    def test_attrs_overlay_wins_on_collision(self):
        content = ContentMarkdown(content="# Hi", attrs={"a": "1"})
        Overlay(attrs={"a": "overlay-value"}).apply(content)
        assert content.attrs["a"] == "overlay-value"

    def test_style_merged_via_style_merge(self):
        """Overlay.style fields override existing content.style fields."""
        content = ContentMarkdown(
            content="# Hi",
            style=Style(font=Font(size=12)),
        )
        Overlay(style=Style(font=Font(size=24))).apply(content)
        assert content.style.font.size == 24

    def test_style_set_when_content_style_is_none(self):
        content = ContentMarkdown(content="# Hi")
        overlay_style = Style(font=Font(size=18))
        Overlay(style=overlay_style).apply(content)
        assert content.style is not None
        assert content.style.font.size == 18

    def test_ignore_set_when_provided(self):
        content = ContentMarkdown(content="# Hi", ignore=False)
        Overlay(ignore=True).apply(content)
        assert content.ignore is True

    def test_ignore_not_touched_when_none(self):
        content = ContentMarkdown(content="# Hi", ignore=True)
        Overlay().apply(content)
        assert content.ignore is True


class TestOverlayIngestion:
    """Overlays supplied in values are merged during _process_cells."""

    def test_overlay_applies_by_index(self):
        nb = new_notebook()
        nb.cells = [
            new_markdown_cell(source="# One", metadata={"tags": []}),
            new_markdown_cell(source="# Two", metadata={"tags": []}),
        ]
        values = {
            "content": ContentMarshall(),
            "overlays": [Overlay(match=CellMatcher(index=0), css=":scope { text-align: center; }")],
        }
        Configuration._process_cells(values, nb)

        first = values["content"].middlematter[0]
        second = values["content"].middlematter[1]
        assert first.css == ":scope { text-align: center; }"
        assert second.css in ("", None)

    def test_overlay_applies_by_tag(self):
        nb = new_notebook()
        nb.cells = [
            new_code_cell(source="plot()", metadata={"tags": ["chart"]}),
            new_code_cell(source="print('hi')", metadata={"tags": []}),
        ]
        values = {
            "content": ContentMarshall(),
            "overlays": [Overlay(match=CellMatcher(tag="chart"), classname="charted")],
        }
        Configuration._process_cells(values, nb)

        charted = values["content"].middlematter[0]
        plain = values["content"].middlematter[1]
        assert charted.classname == "charted"
        assert plain.classname == ""

    def test_overlay_applies_by_cell_type(self):
        nb = new_notebook()
        nb.cells = [
            new_code_cell(source="x = 1", metadata={"tags": []}),
            new_markdown_cell(source="# Heading", metadata={"tags": []}),
        ]
        values = {
            "content": ContentMarshall(),
            "overlays": [Overlay(match=CellMatcher(cell_type="markdown"), classname="prose")],
        }
        Configuration._process_cells(values, nb)

        assert values["content"].middlematter[0].classname == ""
        assert values["content"].middlematter[1].classname == "prose"

    def test_overlay_applies_by_section(self):
        """section matcher targets cells after routing."""
        nb = new_notebook()
        nb.cells = [
            new_markdown_cell(source="# Cover", metadata={"tags": ["nbprint:section:covermatter"]}),
            new_markdown_cell(source="Body", metadata={"tags": []}),
        ]
        values = {
            "content": ContentMarshall(),
            "overlays": [Overlay(match=CellMatcher(section="covermatter"), css="cover-css")],
        }
        Configuration._process_cells(values, nb)

        cover = values["content"].covermatter[0]
        body = values["content"].middlematter[0]
        assert cover.css == "cover-css"
        assert body.css in ("", None)

    def test_overlay_from_dict_spec(self):
        """Dict-shaped overlay specs are validated into Overlay instances."""
        nb = new_notebook()
        nb.cells = [new_markdown_cell(source="# Hi", metadata={"tags": []})]
        values = {
            "content": ContentMarshall(),
            "overlays": [
                {"match": {"index": 0}, "css": "inline-overlay-css"},
            ],
        }
        Configuration._process_cells(values, nb)
        assert values["content"].middlematter[0].css == "inline-overlay-css"

    def test_multiple_overlays_stack_in_order(self):
        """Later overlays layer on top of earlier ones."""
        nb = new_notebook()
        nb.cells = [new_markdown_cell(source="# Hi", metadata={"tags": []})]
        values = {
            "content": ContentMarshall(),
            "overlays": [
                Overlay(css="first"),
                Overlay(css="second"),
            ],
        }
        Configuration._process_cells(values, nb)
        css = values["content"].middlematter[0].css
        assert "first" in css
        assert "second" in css
        assert css.index("first") < css.index("second")

    def test_empty_matcher_matches_all_cells(self):
        nb = new_notebook()
        nb.cells = [
            new_markdown_cell(source="one", metadata={"tags": []}),
            new_markdown_cell(source="two", metadata={"tags": []}),
            new_markdown_cell(source="three", metadata={"tags": []}),
        ]
        values = {
            "content": ContentMarshall(),
            "overlays": [Overlay(classname="all")],
        }
        Configuration._process_cells(values, nb)
        for content in values["content"].middlematter:
            assert content.classname == "all"


class TestSectionStyleDefaults:
    """Section-level default Style inherited by cells in that section."""

    def test_section_styles_field_default(self):
        """section_styles defaults to empty dict."""
        cm = ContentMarshall()
        assert cm.section_styles == {}

    def test_section_styles_accepts_per_section_style(self):
        style = Style(font=Font(size=18))
        cm = ContentMarshall(section_styles={"covermatter": style})
        assert cm.section_styles["covermatter"] is style

    def test_section_default_applied_when_content_has_no_style(self):
        """Content.style is set to the section default when content has no style."""
        cover = ContentMarkdown(content="# Cover")
        cm = ContentMarshall(
            covermatter=[cover],
            section_styles={"covermatter": Style(font=Font(size=28))},
        )
        # Generate triggers the merge
        config = Configuration(
            name="test-section-styles",
            outputs={"_target_": "nbprint.NBConvertOutputs", "naming": "{{name}}", "root": ".pytest_cache/test_section_styles"},
            content=cm,
        )
        config.generate()
        assert cover.style is not None
        assert cover.style.font.size == 28

    def test_content_style_overrides_section_default(self):
        """Explicit Content.style fields override section defaults; unset
        fields inherit from the section default."""
        cover = ContentMarkdown(content="# Cover", style=Style(font=Font(size=48)))
        cm = ContentMarshall(
            covermatter=[cover],
            section_styles={"covermatter": Style(font=Font(size=28))},
        )
        config = Configuration(
            name="test-section-styles-override",
            outputs={"_target_": "nbprint.NBConvertOutputs", "naming": "{{name}}", "root": ".pytest_cache/test_section_styles_override"},
            content=cm,
        )
        config.generate()
        # Content's own value wins
        assert cover.style.font.size == 48

    def test_section_default_does_not_leak_into_other_sections(self):
        """A section default applies only to its own section."""
        cover = ContentMarkdown(content="# Cover")
        body = ContentMarkdown(content="Body")
        cm = ContentMarshall(
            covermatter=[cover],
            middlematter=[body],
            section_styles={"covermatter": Style(font=Font(size=28))},
        )
        config = Configuration(
            name="test-section-styles-isolation",
            outputs={"_target_": "nbprint.NBConvertOutputs", "naming": "{{name}}", "root": ".pytest_cache/test_section_styles_isolation"},
            content=cm,
        )
        config.generate()
        assert cover.style is not None
        assert cover.style.font.size == 28
        assert body.style is None


class TestOverlayAndSectionStylesTogether:
    """Overlays + section styles compose — overlays apply on ingestion,
    section defaults apply at generation time."""

    def test_overlay_and_section_style_both_applied(self):
        """Cell ingested via overlay gets overlay style; section default
        fills in unset fields at generate time."""
        nb = new_notebook()
        nb.cells = [
            new_markdown_cell(source="# Cover", metadata={"tags": ["nbprint:section:covermatter"]}),
        ]
        # Build a ContentMarshall with a section default first
        cm = ContentMarshall(section_styles={"covermatter": Style(font=Font(size=36))})
        values = {
            "content": cm,
            "overlays": [Overlay(match=CellMatcher(section="covermatter"), css="cover-overlay-css")],
        }
        Configuration._process_cells(values, nb)
        # Overlay applied during ingestion
        assert values["content"].covermatter[0].css == "cover-overlay-css"

        # Now run through generate() to apply section default
        config = Configuration(
            name="test-overlay-plus-section",
            outputs={"_target_": "nbprint.NBConvertOutputs", "naming": "{{name}}", "root": ".pytest_cache/test_overlay_section"},
            content=values["content"],
        )
        config.generate()
        cover = values["content"].covermatter[0]
        assert cover.style is not None
        assert cover.style.font.size == 36
        assert "cover-overlay-css" in cover.css


class TestConfigurationOverlaysField:
    """Configuration.overlays field is accepted and usable."""

    def test_configuration_accepts_overlays_field(self):
        config = Configuration(
            name="test-overlays-field",
            outputs={"_target_": "nbprint.NBConvertOutputs", "naming": "{{name}}", "root": ".pytest_cache/test_overlays_field"},
            overlays=[Overlay(match=CellMatcher(index=0), css="foo")],
        )
        assert len(config.overlays) == 1
        assert config.overlays[0].match.index == 0

    def test_configuration_overlays_from_dict(self):
        """Overlays specified as dicts are validated into Overlay instances."""
        config = Configuration(
            name="test-overlays-dict",
            outputs={"_target_": "nbprint.NBConvertOutputs", "naming": "{{name}}", "root": ".pytest_cache/test_overlays_dict"},
            overlays=[{"match": {"tag": "chart"}, "classname": "charted"}],
        )
        assert isinstance(config.overlays[0], Overlay)
        assert config.overlays[0].match.tag == "chart"


class TestLayoutOverlay:
    """LayoutOverlay wraps contiguous runs of matched cells in a flex layout."""

    def test_wraps_contiguous_run_by_tag(self):
        """Two adjacent cells tagged 'sbs' are wrapped in a row layout."""
        from nbprint.config.content.page import ContentFlexRowLayout

        nb = new_notebook()
        nb.cells = [
            new_markdown_cell(source="# Intro"),
            new_markdown_cell(source="Left", metadata={"tags": ["sbs"]}),
            new_markdown_cell(source="Right", metadata={"tags": ["sbs"]}),
            new_markdown_cell(source="After"),
        ]
        values = {
            "content": ContentMarshall(),
            "layout_overlays": [LayoutOverlay(match=CellMatcher(tag="sbs"), layout="row", sizes=[1, 1])],
        }
        Configuration._process_cells(values, nb)
        mm = values["content"].middlematter
        assert len(mm) == 3, [type(c).__name__ for c in mm]
        wrapper = mm[1]
        assert isinstance(wrapper, ContentFlexRowLayout)
        assert wrapper.sizes == [1, 1]
        assert len(wrapper.content) == 2

    def test_wraps_column_layout(self):
        """layout='column' produces a ContentFlexColumnLayout."""
        from nbprint.config.content.page import ContentFlexColumnLayout

        nb = new_notebook()
        nb.cells = [
            new_markdown_cell(source="A", metadata={"tags": ["col"]}),
            new_markdown_cell(source="B", metadata={"tags": ["col"]}),
        ]
        values = {
            "content": ContentMarshall(),
            "layout_overlays": [LayoutOverlay(match=CellMatcher(tag="col"), layout="column")],
        }
        Configuration._process_cells(values, nb)
        assert isinstance(values["content"].middlematter[0], ContentFlexColumnLayout)

    def test_index_range_matching(self):
        """index_range scopes the overlay to an inclusive [lo, hi] range."""
        from nbprint.config.content.page import ContentFlexRowLayout

        nb = new_notebook()
        nb.cells = [
            new_markdown_cell(source="0"),
            new_markdown_cell(source="1"),
            new_markdown_cell(source="2"),
            new_markdown_cell(source="3"),
        ]
        values = {
            "content": ContentMarshall(),
            "layout_overlays": [LayoutOverlay(index_range=(1, 2), layout="row")],
        }
        Configuration._process_cells(values, nb)
        mm = values["content"].middlematter
        # cells 1 and 2 get wrapped; cells 0 and 3 remain
        assert len(mm) == 3
        assert isinstance(mm[1], ContentFlexRowLayout)

    def test_non_contiguous_matches_form_separate_wrappers(self):
        """Two disjoint runs of matching cells produce two wrappers."""
        from nbprint.config.content.page import ContentFlexRowLayout

        nb = new_notebook()
        nb.cells = [
            new_markdown_cell(source="A", metadata={"tags": ["grp"]}),
            new_markdown_cell(source="B", metadata={"tags": ["grp"]}),
            new_markdown_cell(source="gap"),
            new_markdown_cell(source="C", metadata={"tags": ["grp"]}),
            new_markdown_cell(source="D", metadata={"tags": ["grp"]}),
        ]
        values = {
            "content": ContentMarshall(),
            "layout_overlays": [LayoutOverlay(match=CellMatcher(tag="grp"), layout="row")],
        }
        Configuration._process_cells(values, nb)
        mm = values["content"].middlematter
        wrappers = [c for c in mm if isinstance(c, ContentFlexRowLayout)]
        assert len(wrappers) == 2
        assert len(wrappers[0].content) == 2
        assert len(wrappers[1].content) == 2

    def test_layout_overlay_with_formatting(self):
        """Wrapper itself receives css/classname/attrs from the overlay."""
        nb = new_notebook()
        nb.cells = [
            new_markdown_cell(source="A", metadata={"tags": ["w"]}),
            new_markdown_cell(source="B", metadata={"tags": ["w"]}),
        ]
        values = {
            "content": ContentMarshall(),
            "layout_overlays": [
                LayoutOverlay(
                    match=CellMatcher(tag="w"),
                    layout="row",
                    css=":scope { gap: 20px; }",
                    classname="wrapper-cls",
                ),
            ],
        }
        Configuration._process_cells(values, nb)
        wrapper = values["content"].middlematter[0]
        assert "gap: 20px" in wrapper.css
        assert wrapper.classname in ("wrapper-cls", ["wrapper-cls"])

    def test_layout_overlay_from_dict_spec(self):
        """Layout overlays specified as dicts are validated correctly."""
        nb = new_notebook()
        nb.cells = [
            new_markdown_cell(source="A", metadata={"tags": ["d"]}),
            new_markdown_cell(source="B", metadata={"tags": ["d"]}),
        ]
        values = {
            "content": ContentMarshall(),
            "layout_overlays": [{"match": {"tag": "d"}, "layout": "row", "sizes": [2, 1]}],
        }
        Configuration._process_cells(values, nb)
        wrapper = values["content"].middlematter[0]
        assert wrapper.sizes == [2, 1]

    def test_configuration_accepts_layout_overlays_field(self):
        config = Configuration(
            name="test-layout-overlays-field",
            outputs={"_target_": "nbprint.NBConvertOutputs", "naming": "{{name}}", "root": ".pytest_cache/test_layout_overlays_field"},
            layout_overlays=[LayoutOverlay(match=CellMatcher(tag="x"), layout="column")],
        )
        assert len(config.layout_overlays) == 1
        assert config.layout_overlays[0].layout == "column"

    def test_formatting_and_layout_overlay_compose(self):
        """Formatting overlay applies to child cell; layout overlay wraps them."""
        from nbprint.config.content.page import ContentFlexRowLayout

        nb = new_notebook()
        nb.cells = [
            new_markdown_cell(source="A", metadata={"tags": ["w"]}),
            new_markdown_cell(source="B", metadata={"tags": ["w"]}),
        ]
        values = {
            "content": ContentMarshall(),
            "overlays": [Overlay(match=CellMatcher(tag="w"), classname="child")],
            "layout_overlays": [LayoutOverlay(match=CellMatcher(tag="w"), layout="row")],
        }
        Configuration._process_cells(values, nb)
        wrapper = values["content"].middlematter[0]
        assert isinstance(wrapper, ContentFlexRowLayout)
        # Children were first tagged with classname "child" by the formatting overlay
        for child in wrapper.content:
            assert child.classname == "child" or "child" in (child.classname or [])
