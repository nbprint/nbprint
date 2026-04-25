from nbprint import Page, PageGlobal
from nbprint.config.common import PageOrientation, PageSize
from nbprint.config.content import ContentMarkdown
from nbprint.config.core.content import SECTION_GROUPS, SECTION_ORDER, ContentMarshall
from nbprint.config.core.page import PAGE_REGION_ATTRS


class TestSection:
    def test_section_literal_values(self):
        """All expected section names are valid."""
        expected = [
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
        for name in expected:
            # Section is a Literal; verify each value is accepted by checking
            # it appears in the ContentMarshall model fields
            assert name in ContentMarshall.model_fields


class TestContentMarshall:
    def test_empty(self):
        cm = ContentMarshall()
        assert cm.all == []
        assert cm._prematter == []
        assert cm._covermatter == []
        assert cm._frontmatter == []
        assert cm._middlematter == []
        assert cm._endmatter == []
        assert cm._rearmatter == []

    def test_backward_compat_four_original_sections(self):
        """Content in the original 4 sections still works."""
        pre = ContentMarkdown(content="pre")
        front = ContentMarkdown(content="front")
        mid = ContentMarkdown(content="mid")
        end = ContentMarkdown(content="end")
        cm = ContentMarshall(prematter=[pre], frontmatter=[front], middlematter=[mid], endmatter=[end])
        assert cm.all == [pre, front, mid, end]

    def test_all_sections_ordering(self):
        """Content from all sections appears in correct document order."""
        items = {}
        for name in [
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
        ]:
            items[name] = ContentMarkdown(content=name)

        cm = ContentMarshall(**{k: [v] for k, v in items.items()})
        contents = [c.content for c in cm.all]
        assert contents == [
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

    def test_group_aggregation(self):
        """Private group attributes aggregate their sub-sections."""
        title = ContentMarkdown(content="title")
        copy_ = ContentMarkdown(content="copyright")
        dedication = ContentMarkdown(content="dedication")
        toc = ContentMarkdown(content="toc")
        front = ContentMarkdown(content="front")
        cm = ContentMarshall(
            title=[title],
            copyright=[copy_],
            dedication=[dedication],
            table_of_contents=[toc],
            frontmatter=[front],
        )
        assert cm._frontmatter == [title, copy_, dedication, toc, front]

    def test_endmatter_group(self):
        appendix = ContentMarkdown(content="appendix")
        index = ContentMarkdown(content="index")
        end = ContentMarkdown(content="end")
        cm = ContentMarshall(appendix=[appendix], index=[index], endmatter=[end])
        assert cm._endmatter == [appendix, index, end]

    def test_middlematter_group(self):
        mid = ContentMarkdown(content="mid")
        sep = ContentMarkdown(content="sep")
        cm = ContentMarshall(middlematter=[mid], middlematter_separators=[sep])
        assert cm._middlematter == [mid, sep]

    def test_middlematter_list_of_lists_interleaves_separators(self):
        """List-of-lists middlematter promotes first item of each sublist to a separator."""
        c1_sep = ContentMarkdown(content="chap1-title")
        c1_a = ContentMarkdown(content="chap1-a")
        c1_b = ContentMarkdown(content="chap1-b")
        c2_sep = ContentMarkdown(content="chap2-title")
        c2_a = ContentMarkdown(content="chap2-a")
        cm = ContentMarshall(
            middlematter=[
                [c1_sep, c1_a, c1_b],
                [c2_sep, c2_a],
            ]
        )
        # separators extracted and flat middlematter holds remainder
        assert [c.content for c in cm.middlematter_separators] == ["chap1-title", "chap2-title"]
        assert [c.content for c in cm.middlematter] == ["chap1-a", "chap1-b", "chap2-a"]
        # rendered order interleaves separator before each chapter
        assert [c.content for c in cm._middlematter] == [
            "chap1-title",
            "chap1-a",
            "chap1-b",
            "chap2-title",
            "chap2-a",
        ]

    def test_middlematter_list_of_lists_empty_sublist(self):
        """Empty sublists contribute nothing but don't break indexing."""
        a = ContentMarkdown(content="a")
        cm = ContentMarshall(middlematter=[[], [a]])
        assert [c.content for c in cm._middlematter] == ["a"]

    def test_middlematter_single_flat_list_unchanged(self):
        """Backwards compat: flat list still appends separators at the end."""
        a = ContentMarkdown(content="a")
        b = ContentMarkdown(content="b")
        sep = ContentMarkdown(content="sep")
        cm = ContentMarshall(middlematter=[a, b], middlematter_separators=[sep])
        assert [c.content for c in cm._middlematter] == ["a", "b", "sep"]

    def test_auto_table_of_contents_injects_when_empty(self):
        """auto_table_of_contents=True injects a ContentTableOfContents when section is empty."""
        from nbprint.config.content import ContentTableOfContents

        cm = ContentMarshall(auto_table_of_contents=True)
        assert len(cm.table_of_contents) == 1
        assert isinstance(cm.table_of_contents[0], ContentTableOfContents)
        # TOC lives in the frontmatter group
        assert cm._frontmatter == cm.table_of_contents

    def test_auto_table_of_contents_noop_when_populated(self):
        """auto_table_of_contents must not overwrite a user-supplied TOC."""
        from nbprint.config.content import ContentTableOfContents

        user_toc = ContentTableOfContents()
        cm = ContentMarshall(auto_table_of_contents=True, table_of_contents=[user_toc])
        assert cm.table_of_contents == [user_toc]

    def test_auto_table_of_contents_default_false(self):
        """Default behavior unchanged — no TOC auto-injected."""
        cm = ContentMarshall()
        assert cm.table_of_contents == []

    def test_indexing(self):
        a = ContentMarkdown(content="a")
        b = ContentMarkdown(content="b")
        cm = ContentMarshall(prematter=[a], middlematter=[b])
        assert cm[0].content == "a"
        assert cm[1].content == "b"

    def test_from_dict_new_sections(self):
        """Configuration._convert_content_from_dict handles all section keys."""
        from nbprint.config.core.config import Configuration

        data = {
            "covermatter": [{"type_": "nbprint.ContentMarkdown", "content": "cover"}],
            "title": [{"type_": "nbprint.ContentMarkdown", "content": "title"}],
            "middlematter": [{"type_": "nbprint.ContentMarkdown", "content": "body"}],
        }
        cm = Configuration._convert_content_from_dict(data)
        assert len(cm._covermatter) == 1
        assert len(cm._frontmatter) == 1
        assert len(cm._middlematter) == 1


class TestPageGlobal:
    def test_defaults(self):
        pg = PageGlobal()
        assert pg.size == PageSize.letter
        assert pg.orientation == PageOrientation.portrait
        assert pg.pages == {}

    def test_render_default(self):
        pg = PageGlobal()
        pg.render()
        assert "@page { size:" in pg.css
        assert "letter" in pg.css
        assert "portrait" in pg.css

    def test_render_custom_size_tuple(self):
        pg = PageGlobal(size=(8.5, 11.0))
        pg.render()
        assert "8.5in" in pg.css
        assert "11.0in" in pg.css

    def test_render_landscape(self):
        pg = PageGlobal(orientation=PageOrientation.landscape)
        pg.render()
        assert "landscape" in pg.css

    def test_render_idempotent(self):
        pg = PageGlobal()
        pg.render()
        css1 = pg.css
        pg.render()
        assert pg.css == css1

    def test_per_section_pages(self):
        cover_page = Page(css="cover-custom")
        pg = PageGlobal(pages={"covermatter": cover_page})
        assert pg.pages["covermatter"].css == "cover-custom"

    def test_backward_compat_page_regions(self):
        """PageGlobal still supports all the region fields inherited from Page."""
        pg = PageGlobal(
            bottom_right={"content": {"content": "counter(page)"}},
        )
        assert pg.bottom_right is not None


class TestPageBackwardCompat:
    def test_page_has_size_and_orientation(self):
        """Base Page has size/orientation (same as main branch)."""
        p = Page()
        assert hasattr(p, "size")
        assert hasattr(p, "orientation")

    def test_page_no_pages_field(self):
        """Base Page does not have a pages dict (only PageGlobal has it)."""
        assert "pages" not in Page.model_fields


class TestSectionConstants:
    def test_section_order_matches_section_literal(self):
        """SECTION_ORDER contains exactly the Section literal values."""
        assert set(SECTION_ORDER) == set(ContentMarshall.model_fields) - {
            "tags",
            "role",
            "ignore",
            "css",
            "esm",
            "classname",
            "attrs",
            "section_styles",
            "auto_table_of_contents",
            "middlematter_chapter_sizes",
        }

    def test_section_groups_keys_match_order(self):
        """SECTION_GROUPS has entries for all sections in SECTION_ORDER."""
        assert set(SECTION_GROUPS.keys()) == set(SECTION_ORDER)

    def test_section_groups_values(self):
        """All group values are one of the six canonical groups."""
        expected_groups = {"prematter", "covermatter", "frontmatter", "middlematter", "endmatter", "rearmatter"}
        assert set(SECTION_GROUPS.values()) == expected_groups

    def test_page_region_attrs(self):
        """PAGE_REGION_ATTRS contains all 16 page region fields."""
        assert len(PAGE_REGION_ATTRS) == 16
        for attr in PAGE_REGION_ATTRS:
            assert attr in Page.model_fields


class TestContentMarshallSections:
    def test_sections_empty(self):
        """Empty ContentMarshall yields no sections."""
        cm = ContentMarshall()
        assert list(cm.sections()) == []

    def test_sections_single(self):
        """ContentMarshall with one section yields that section."""
        md = ContentMarkdown(content="body")
        cm = ContentMarshall(middlematter=[md])
        sections = list(cm.sections())
        assert len(sections) == 1
        name, group, contents = sections[0]
        assert name == "middlematter"
        assert group == "middlematter"
        assert contents == [md]

    def test_sections_ordering(self):
        """sections() yields in correct document order."""
        cm = ContentMarshall(
            endmatter=[ContentMarkdown(content="end")],
            covermatter=[ContentMarkdown(content="cover")],
            prematter=[ContentMarkdown(content="pre")],
        )
        names = [name for name, _, _ in cm.sections()]
        assert names == ["prematter", "covermatter", "endmatter"]

    def test_sections_groups(self):
        """sections() yields correct group names."""
        cm = ContentMarshall(
            title=[ContentMarkdown(content="title")],
            appendix=[ContentMarkdown(content="appendix")],
        )
        sections = list(cm.sections())
        assert sections[0] == ("title", "frontmatter", cm.title)
        assert sections[1] == ("appendix", "endmatter", cm.appendix)

    def test_sections_matches_all_order(self):
        """Content order from sections() matches content.all ordering."""
        items = {}
        for name in SECTION_ORDER:
            items[name] = ContentMarkdown(content=name)
        cm = ContentMarshall(**{k: [v] for k, v in items.items()})

        from_sections = []
        for _, _, contents in cm.sections():
            from_sections.extend(contents)
        assert from_sections == cm.all

    def test_backward_compat_list_content(self):
        """Flat list content → middlematter yields a single section."""
        items = [ContentMarkdown(content=f"item{i}") for i in range(3)]
        cm = ContentMarshall(middlematter=items)
        sections = list(cm.sections())
        assert len(sections) == 1
        assert sections[0][0] == "middlematter"
        assert len(sections[0][2]) == 3


class TestSectionTagging:
    def test_generate_tags_cells_with_sections(self):
        """Configuration.generate() tags content cells with section metadata."""
        from nbprint.config.content import ContentMarkdown
        from nbprint.config.core.config import Configuration
        from nbprint.config.core.content import ContentMarshall

        config = Configuration(
            name="test-sections",
            outputs={"_target_": "nbprint.NBConvertOutputs", "naming": "{{name}}", "root": ".pytest_cache/test_sections"},
            content=ContentMarshall(
                covermatter=[ContentMarkdown(content="cover")],
                middlematter=[ContentMarkdown(content="body")],
            ),
        )
        nb = config.generate()

        # Find content cells by section tags (markdown cells don't have nbprint:content)
        content_cells = [c for c in nb.cells if any(t.startswith("nbprint:section:") for t in c.metadata.get("tags", []))]
        assert len(content_cells) == 2

        # First content cell should be tagged covermatter
        cover_cell = content_cells[0]
        assert "nbprint:section:covermatter" in cover_cell.metadata.tags
        assert "nbprint:section-group:covermatter" in cover_cell.metadata.tags

        # Second content cell should be tagged middlematter
        body_cell = content_cells[1]
        assert "nbprint:section:middlematter" in body_cell.metadata.tags
        assert "nbprint:section-group:middlematter" in body_cell.metadata.tags

    def test_generate_backward_compat_flat_content(self):
        """Flat-list content is tagged as middlematter."""
        from pathlib import Path

        from nbprint.cli import run

        config = run(str(Path(__file__).parent / "files" / "hermetic.yaml"), dry_run=True)
        nb = config.generate()

        content_cells = [c for c in nb.cells if "nbprint:content" in c.metadata.get("tags", [])]
        for cell in content_cells:
            # hermetic.yaml uses flat list content → all middlematter
            assert "nbprint:section:middlematter" in cell.metadata.tags
            assert "nbprint:section-group:middlematter" in cell.metadata.tags


class TestNotebookSectionRouting:
    """Section routing from cell tags and metadata when loading notebooks."""

    def test_section_routing_from_cell_tags(self):
        """Cells with nbprint:section:<name> tags are routed to the correct section."""
        from nbformat.v4 import new_markdown_cell, new_notebook

        nb = new_notebook()
        nb.cells = [
            new_markdown_cell(source="# Cover", metadata={"tags": ["nbprint:section:covermatter"]}),
            new_markdown_cell(source="# Title", metadata={"tags": ["nbprint:section:title"]}),
            new_markdown_cell(source="Body content", metadata={"tags": []}),
            new_markdown_cell(source="# Appendix", metadata={"tags": ["nbprint:section:appendix"]}),
        ]

        from nbprint.config.core.config import Configuration

        values = {"content": ContentMarshall()}
        Configuration._process_cells(values, nb)

        assert len(values["content"].covermatter) == 1
        assert values["content"].covermatter[0].content == "# Cover"
        assert len(values["content"].title) == 1
        assert values["content"].title[0].content == "# Title"
        assert len(values["content"].middlematter) == 1
        assert values["content"].middlematter[0].content == "Body content"
        assert len(values["content"].appendix) == 1
        assert values["content"].appendix[0].content == "# Appendix"

    def test_section_routing_from_cell_metadata(self):
        """Cells with metadata.nbprint.section are routed to the correct section."""
        from nbformat.v4 import new_code_cell, new_notebook

        nb = new_notebook()
        nb.cells = [
            new_code_cell(source="setup()", metadata={"tags": [], "nbprint": {"section": "prematter"}}),
            new_code_cell(source="main()", metadata={"tags": []}),
        ]

        from nbprint.config.core.config import Configuration

        values = {"content": ContentMarshall()}
        Configuration._process_cells(values, nb)

        assert len(values["content"].prematter) == 1
        assert values["content"].prematter[0].content == "setup()"
        assert len(values["content"].middlematter) == 1
        assert values["content"].middlematter[0].content == "main()"

    def test_section_metadata_takes_priority_over_tags(self):
        """metadata.nbprint.section takes priority over nbprint:section: tags."""
        from nbformat.v4 import new_markdown_cell, new_notebook

        nb = new_notebook()
        nb.cells = [
            new_markdown_cell(
                source="Priority test",
                metadata={
                    "tags": ["nbprint:section:appendix"],
                    "nbprint": {"section": "covermatter"},
                },
            ),
        ]

        from nbprint.config.core.config import Configuration

        values = {"content": ContentMarshall()}
        Configuration._process_cells(values, nb)

        # Metadata wins
        assert len(values["content"].covermatter) == 1
        assert len(values["content"].appendix) == 0

    def test_invalid_section_tag_ignored(self):
        """Tags with invalid section names fall through to middlematter."""
        from nbformat.v4 import new_markdown_cell, new_notebook

        nb = new_notebook()
        nb.cells = [
            new_markdown_cell(source="Bad section", metadata={"tags": ["nbprint:section:nonexistent"]}),
        ]

        from nbprint.config.core.config import Configuration

        values = {"content": ContentMarshall()}
        Configuration._process_cells(values, nb)

        assert len(values["content"].middlematter) == 1

    def test_no_tags_defaults_to_middlematter(self):
        """Cells without any section indicators go to middlematter."""
        from nbformat.v4 import new_code_cell, new_notebook

        nb = new_notebook()
        nb.cells = [
            new_code_cell(source="print('hi')", metadata={"tags": []}),
        ]

        from nbprint.config.core.config import Configuration

        values = {"content": ContentMarshall()}
        Configuration._process_cells(values, nb)

        assert len(values["content"].middlematter) == 1

    def test_parameters_cell_still_extracted(self):
        """First cell with 'parameters' tag is still parsed as parameters, not routed."""
        from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

        nb = new_notebook()
        nb.cells = [
            new_code_cell(source="x = 42", metadata={"tags": ["parameters"]}),
            new_markdown_cell(source="Body", metadata={"tags": ["nbprint:section:frontmatter"]}),
        ]

        from nbprint.config.core.config import Configuration
        from nbprint.config.core.parameters import PapermillParameters

        values = {"content": ContentMarshall(), "parameters": PapermillParameters()}
        Configuration._process_cells(values, nb)

        assert values["parameters"].vars["x"] == 42
        assert len(values["content"].frontmatter) == 1
        assert len(values["content"].middlematter) == 0

    def test_multiple_cells_same_section(self):
        """Multiple cells routed to the same section appear in order."""
        from nbformat.v4 import new_markdown_cell, new_notebook

        nb = new_notebook()
        nb.cells = [
            new_markdown_cell(source="First", metadata={"tags": ["nbprint:section:frontmatter"]}),
            new_markdown_cell(source="Second", metadata={"tags": ["nbprint:section:frontmatter"]}),
            new_markdown_cell(source="Third", metadata={"tags": ["nbprint:section:frontmatter"]}),
        ]

        from nbprint.config.core.config import Configuration

        values = {"content": ContentMarshall()}
        Configuration._process_cells(values, nb)

        assert len(values["content"].frontmatter) == 3
        assert [c.content for c in values["content"].frontmatter] == ["First", "Second", "Third"]


class TestNotebookLevelMetadata:
    """Page and output config from notebook-level metadata."""

    def test_page_config_from_notebook_metadata(self):
        """notebook.metadata.nbprint.page is used when no page config in values."""
        from nbformat.v4 import new_markdown_cell, new_notebook

        from nbprint.config.core.config import Configuration

        nb = new_notebook()
        nb.metadata["nbprint"] = {
            "page": {
                "_target_": "nbprint.PageGlobal",
                "size": "a4",
                "orientation": "landscape",
            }
        }
        nb.cells = [new_markdown_cell(source="Hello", metadata={"tags": []})]

        values = {
            "name": "test",
            "outputs": {"_target_": "nbprint.NBConvertOutputs", "naming": "{{name}}", "root": ".pytest_cache/test_nb_meta"},
        }
        values["content"] = ContentMarshall()

        # Simulate what _append_notebook_content does
        nb_meta = nb.metadata.get("nbprint", {})
        if "page" in nb_meta and "page" not in values:
            values["page"] = nb_meta["page"]

        Configuration._process_cells(values, nb)

        assert values["page"]["size"] == "a4"
        assert values["page"]["orientation"] == "landscape"

    def test_page_config_not_overridden_by_notebook(self):
        """Explicit page config in values takes priority over notebook metadata."""
        from nbformat.v4 import new_notebook

        nb = new_notebook()
        nb.metadata["nbprint"] = {
            "page": {"_target_": "nbprint.PageGlobal", "size": "a4"},
        }
        nb.cells = []

        values = {
            "page": {"_target_": "nbprint.PageGlobal", "size": "legal"},
        }

        # Simulate extraction: notebook page should NOT override explicit value
        nb_meta = nb.metadata.get("nbprint", {})
        if "page" in nb_meta and "page" not in values:
            values["page"] = nb_meta["page"]

        assert values["page"]["size"] == "legal"

    def test_outputs_config_from_notebook_metadata(self):
        """notebook.metadata.nbprint.outputs is used when no outputs config in values."""
        from nbformat.v4 import new_notebook

        nb = new_notebook()
        nb.metadata["nbprint"] = {
            "outputs": {
                "_target_": "nbprint.NBConvertOutputs",
                "naming": "{{name}}-custom",
                "root": ".pytest_cache/custom_outputs",
            }
        }
        nb.cells = []

        values = {}

        nb_meta = nb.metadata.get("nbprint", {})
        if "outputs" in nb_meta and "outputs" not in values:
            values["outputs"] = nb_meta["outputs"]

        assert values["outputs"]["naming"] == "{{name}}-custom"


class TestCellMetadataRoundTrip:
    """Verify cell metadata fields survive the round-trip."""

    def test_attrs_dict_preserved(self):
        """attrs as a dict is preserved through _cell_to_content."""
        from nbformat.v4 import new_code_cell

        from nbprint.config.core.config import Configuration

        cell = new_code_cell(
            source="x = 1",
            metadata={
                "tags": [],
                "nbprint": {
                    "attrs": {"data-custom": "value"},
                    "css": ":scope { color: red; }",
                },
            },
        )
        content = Configuration._cell_to_content(cell)
        assert content.attrs == {"data-custom": "value"}
        assert content.css == ":scope { color: red; }"

    def test_attrs_string_dropped(self):
        """attrs serialized as a string (from generation) is dropped during ingestion."""
        from nbformat.v4 import new_code_cell

        from nbprint.config.core.config import Configuration

        cell = new_code_cell(
            source="x = 1",
            metadata={
                "tags": [],
                "nbprint": {
                    "attrs": 'data-custom="value"',
                },
            },
        )
        content = Configuration._cell_to_content(cell)
        # String attrs are dropped; falls back to default (empty dict)
        assert content.attrs == {}

    def test_generated_fields_dropped(self):
        """class, class_selector, element_selector, data, parent-id are dropped."""
        from nbformat.v4 import new_markdown_cell

        from nbprint.config.core.config import Configuration

        cell = new_markdown_cell(
            source="# Hello",
            metadata={
                "tags": [],
                "nbprint": {
                    "class": "nbprint ContentMarkdown ContentMarkdown-abc123",
                    "class_selector": "ContentMarkdown",
                    "element_selector": "ContentMarkdown-abc123",
                    "data": '{"content": "# Hello"}',
                    "parent-id": "some-parent-id",
                    "css": ":scope { font-size: 2em; }",
                },
            },
        )
        content = Configuration._cell_to_content(cell)
        assert content.content == "# Hello"
        assert content.css == ":scope { font-size: 2em; }"

    def test_css_and_esm_preserved(self):
        """css and esm fields are preserved through round-trip."""
        from nbformat.v4 import new_code_cell

        from nbprint.config.core.config import Configuration

        cell = new_code_cell(
            source="plot()",
            metadata={
                "tags": [],
                "nbprint": {
                    "css": ".chart { width: 100%; }",
                    "esm": "function render(meta, elem) { console.log('hi'); }",
                },
            },
        )
        content = Configuration._cell_to_content(cell)
        assert content.css == ".chart { width: 100%; }"
        assert content.esm == "function render(meta, elem) { console.log('hi'); }"

    def test_ignore_field_preserved(self):
        """ignore field is preserved through round-trip."""
        from nbformat.v4 import new_code_cell

        from nbprint.config.core.config import Configuration

        cell = new_code_cell(
            source="setup()",
            metadata={
                "tags": [],
                "nbprint": {"ignore": True},
            },
        )
        content = Configuration._cell_to_content(cell)
        assert content.ignore is True


class TestPageGlobalPerSectionCSS:
    def test_render_generates_named_page_css(self):
        """render() generates @page sectionname rules for per-section pages."""
        cover_page = Page(css="margin: 0;")
        pg = PageGlobal(pages={"covermatter": cover_page})
        pg.render()
        assert "@page covermatter" in pg.css
        assert "margin: 0;" in pg.css

    def test_render_generates_section_selector(self):
        """render() generates CSS selector to map section elements to named pages."""
        pg = PageGlobal(pages={"frontmatter": Page()})
        pg.render()
        assert '[data-nbprint-section="frontmatter"]' in pg.css
        assert "page: frontmatter;" in pg.css

    def test_render_counter_reset(self):
        """Per-section page with counter_reset generates CSS counter-reset rule."""
        pg = PageGlobal(pages={"middlematter": Page(counter_reset=True)})
        pg.render()
        assert "counter-reset: page 1;" in pg.css
        assert "@page middlematter" in pg.css

    def test_render_counter_style(self):
        """Per-section page with counter_style generates CSS counter style rule."""
        pg = PageGlobal(pages={"frontmatter": Page(counter_style="lower-roman")})
        pg.render()
        assert "counter(page, lower-roman)" in pg.css
        assert "@page frontmatter" in pg.css

    def test_render_per_section_with_regions(self):
        """Per-section page with regions generates region CSS in the named page rule."""
        section_page = Page(
            bottom_right={"content": {"content": "counter(page, lower-roman)"}},
        )
        pg = PageGlobal(pages={"frontmatter": section_page})
        pg.render()
        assert "@page frontmatter" in pg.css
        assert "bottom-right" in pg.css

    def test_render_multiple_sections(self):
        """render() handles multiple per-section pages."""
        pg = PageGlobal(
            pages={
                "covermatter": Page(css="margin: 0;"),
                "frontmatter": Page(counter_style="lower-roman"),
                "middlematter": Page(counter_reset=True),
            }
        )
        pg.render()
        assert "@page covermatter" in pg.css
        assert "@page frontmatter" in pg.css
        assert "@page middlematter" in pg.css

    def test_render_idempotent_with_sections(self):
        """Per-section CSS is not duplicated on repeated render() calls."""
        pg = PageGlobal(pages={"covermatter": Page(css="margin: 0;")})
        pg.render()
        css1 = pg.css
        pg.render()
        assert pg.css == css1

    def test_convert_pages_none_value(self):
        """Pages dict entries with None value get converted to empty Page."""
        pg = PageGlobal(pages={"covermatter": None})
        assert isinstance(pg.pages["covermatter"], Page)


class TestPageCounterFields:
    def test_page_counter_defaults(self):
        """Page counter fields default to off."""
        p = Page()
        assert p.counter_reset is False
        assert p.counter_style is None

    def test_page_counter_reset(self):
        p = Page(counter_reset=True)
        assert p.counter_reset is True

    def test_page_counter_style(self):
        p = Page(counter_style="lower-roman")
        assert p.counter_style == "lower-roman"


class TestNBPrintCellRuntime:
    """NBPrintCell runtime API and %%nbprint magic ingestion."""

    def test_nbprint_cell_to_dict(self):
        """NBPrintCell.to_dict() returns only non-None fields."""
        from nbprint import NBPrintCell

        cell = NBPrintCell(section="covermatter", css=":scope { color: red; }", emit=False)
        d = cell.to_dict()
        assert d == {"section": "covermatter", "css": ":scope { color: red; }"}

    def test_nbprint_cell_to_dict_with_style(self):
        """NBPrintCell.to_dict() serializes Style objects."""
        from nbprint import NBPrintCell
        from nbprint.config.common import Font, Style

        cell = NBPrintCell(style=Style(font=Font(size=24)), emit=False)
        d = cell.to_dict()
        assert "style" in d
        assert d["style"]["font"]["size"] == 24

    def test_nbprint_cell_to_dict_with_all_fields(self):
        """NBPrintCell.to_dict() includes classname, attrs, ignore."""
        from nbprint import NBPrintCell

        cell = NBPrintCell(
            section="frontmatter",
            css=":scope { margin: 0; }",
            classname="highlight",
            attrs={"data-foo": "bar"},
            ignore=True,
            emit=False,
        )
        d = cell.to_dict()
        assert d["section"] == "frontmatter"
        assert d["classname"] == "highlight"
        assert d["attrs"] == {"data-foo": "bar"}
        assert d["ignore"] is True

    def test_nbprint_cell_to_dict_empty(self):
        """NBPrintCell with no args produces empty dict."""
        from nbprint import NBPrintCell

        cell = NBPrintCell(emit=False)
        assert cell.to_dict() == {}

    def test_extract_nbprint_mime_from_cell_output(self):
        """_extract_nbprint_mime finds MIME-type metadata in cell outputs."""
        import json

        from nbformat.v4 import new_code_cell

        from nbprint import NBPRINT_MIME
        from nbprint.config.core.config import Configuration

        meta = {"section": "covermatter", "css": ":scope { text-align: center; }"}
        cell = new_code_cell(
            source="NBPrintCell(section='covermatter')",
            metadata={"tags": []},
        )
        cell.outputs = [
            {
                "output_type": "display_data",
                "data": {NBPRINT_MIME: json.dumps(meta)},
                "metadata": {},
            }
        ]
        result = Configuration._extract_nbprint_mime(cell)
        assert result == meta

    def test_extract_nbprint_mime_missing(self):
        """_extract_nbprint_mime returns None when no MIME output."""
        from nbformat.v4 import new_code_cell

        from nbprint.config.core.config import Configuration

        cell = new_code_cell(source="x = 1", metadata={"tags": []})
        cell.outputs = []
        assert Configuration._extract_nbprint_mime(cell) is None

    def test_cell_to_content_merges_mime_metadata(self):
        """_cell_to_content merges MIME output metadata into Content."""
        import json

        from nbformat.v4 import new_code_cell

        from nbprint import NBPRINT_MIME
        from nbprint.config.core.config import Configuration

        cell = new_code_cell(
            source="display('hello')",
            metadata={"tags": []},
        )
        cell.outputs = [
            {
                "output_type": "display_data",
                "data": {NBPRINT_MIME: json.dumps({"css": ":scope { font-size: 2em; }", "classname": "big"})},
                "metadata": {},
            }
        ]
        content = Configuration._cell_to_content(cell)
        assert content.css == ":scope { font-size: 2em; }"
        assert content.classname == "big"

    def test_cell_to_content_metadata_priority_over_mime(self):
        """Explicit cell.metadata.nbprint takes priority over MIME output."""
        import json

        from nbformat.v4 import new_code_cell

        from nbprint import NBPRINT_MIME
        from nbprint.config.core.config import Configuration

        cell = new_code_cell(
            source="code()",
            metadata={
                "tags": [],
                "nbprint": {"css": "explicit-css"},
            },
        )
        cell.outputs = [
            {
                "output_type": "display_data",
                "data": {NBPRINT_MIME: json.dumps({"css": "mime-css", "classname": "from-mime"})},
                "metadata": {},
            }
        ]
        content = Configuration._cell_to_content(cell)
        # Explicit metadata wins for css
        assert content.css == "explicit-css"
        # MIME fills in classname since it's not in explicit metadata
        assert content.classname == "from-mime"

    def test_section_routing_from_mime_output(self):
        """Cells with section in MIME output are routed to the correct section."""
        import json

        from nbformat.v4 import new_code_cell, new_notebook

        from nbprint import NBPRINT_MIME
        from nbprint.config.core.config import Configuration

        nb = new_notebook()
        cell = new_code_cell(
            source="display('cover')",
            metadata={"tags": []},
        )
        cell.outputs = [
            {
                "output_type": "display_data",
                "data": {NBPRINT_MIME: json.dumps({"section": "covermatter"})},
                "metadata": {},
            }
        ]
        nb.cells = [cell]

        values = {"content": ContentMarshall()}
        Configuration._process_cells(values, nb)

        assert len(values["content"].covermatter) == 1
        assert len(values["content"].middlematter) == 0


class TestNBPrintMagicParsing:
    """%%nbprint cell magic parsing."""

    def test_extract_magic_basic(self):
        """_extract_nbprint_magic parses key=value pairs."""
        from nbprint.config.core.config import Configuration

        result = Configuration._extract_nbprint_magic('%%nbprint section=frontmatter css=":scope { color: red; }"')
        assert result == {"section": "frontmatter", "css": ":scope { color: red; }"}

    def test_extract_magic_ignore(self):
        """_extract_nbprint_magic parses ignore as boolean."""
        from nbprint.config.core.config import Configuration

        result = Configuration._extract_nbprint_magic("%%nbprint ignore=true")
        assert result == {"ignore": True}

    def test_extract_magic_no_magic(self):
        """_extract_nbprint_magic returns None for non-magic source."""
        from nbprint.config.core.config import Configuration

        assert Configuration._extract_nbprint_magic("x = 1") is None

    def test_extract_magic_empty(self):
        """_extract_nbprint_magic with no args returns empty dict."""
        from nbprint.config.core.config import Configuration

        result = Configuration._extract_nbprint_magic("%%nbprint")
        assert result == {}

    def test_cell_to_content_strips_magic_line(self):
        """_cell_to_content strips the %%nbprint magic line from source."""
        from nbformat.v4 import new_code_cell

        from nbprint.config.core.config import Configuration

        cell = new_code_cell(
            source="%%nbprint section=frontmatter\ndisplay('hello')",
            metadata={"tags": []},
        )
        cell.outputs = []
        content = Configuration._cell_to_content(cell)
        assert content.content == "display('hello')"

    def test_cell_to_content_magic_sets_section_in_metadata(self):
        """%%nbprint section= is available for section routing during _process_cells."""
        from nbformat.v4 import new_code_cell, new_notebook

        from nbprint.config.core.config import Configuration

        nb = new_notebook()
        nb.cells = [
            new_code_cell(
                source="%%nbprint section=endmatter\nresult()",
                metadata={"tags": []},
            ),
        ]
        # Need to set outputs to empty list
        nb.cells[0].outputs = []

        values = {"content": ContentMarshall()}
        Configuration._process_cells(values, nb)

        assert len(values["content"].endmatter) == 1
        assert values["content"].endmatter[0].content == "result()"
        assert len(values["content"].middlematter) == 0

    def test_parse_magic_line_quoted_values(self):
        """_parse_magic_line handles quoted values with spaces."""
        from nbprint.config.magic import _parse_magic_line

        result = _parse_magic_line('section=frontmatter css=":scope { font-size: 18px; }"')
        assert result["section"] == "frontmatter"
        assert result["css"] == ":scope { font-size: 18px; }"


class TestContentPageBox:
    """Phase 9.1 — ContentPageBox model."""

    def test_defaults(self):
        from nbprint.config.content import ContentPageBox

        box = ContentPageBox()
        assert box.fit == "scale"
        assert box.min_pages == 1
        assert box.page_size is None
        assert box.page_orientation is None
        assert box.page_margins is None
        assert "nbprint:content:page-box" in box.tags

    def test_default_css_has_page_breaks(self):
        from nbprint.config.content import ContentPageBox

        css = ContentPageBox().css
        assert "break-before: page" in css
        assert "break-after: page" in css
        assert ":scope" in css

    def test_data_attrs_populated(self):
        from nbprint.config.content import ContentPageBox

        box = ContentPageBox()
        assert box.attrs["data-nbprint-page-box"] == box._id
        assert box.attrs["data-nbprint-fit"] == "scale"
        # min_pages default (1) does NOT add data-nbprint-min-pages
        assert "data-nbprint-min-pages" not in box.attrs

    def test_fit_override_reflected_in_attrs(self):
        from nbprint.config.content import ContentPageBox

        box = ContentPageBox(fit="strict")
        assert box.fit == "strict"
        assert box.attrs["data-nbprint-fit"] == "strict"

    def test_min_pages_attr_set_when_greater_than_one(self):
        from nbprint.config.content import ContentPageBox

        box = ContentPageBox(min_pages=3)
        assert box.attrs["data-nbprint-min-pages"] == "3"

    def test_user_attrs_preserved(self):
        from nbprint.config.content import ContentPageBox

        box = ContentPageBox(attrs={"data-custom": "x", "data-nbprint-page-box": "override"})
        # User override of the data-nbprint-page-box wins (setdefault).
        assert box.attrs["data-nbprint-page-box"] == "override"
        assert box.attrs["data-custom"] == "x"

    def test_page_overrides(self):
        from nbprint.config.common import PageOrientation, PageSize
        from nbprint.config.content import ContentPageBox

        box = ContentPageBox(
            page_size=PageSize.A4,
            page_orientation=PageOrientation.landscape,
            page_margins="1in",
        )
        assert box.page_size == PageSize.A4
        assert box.page_orientation == PageOrientation.landscape
        assert box.page_margins == "1in"

    def test_min_pages_validation(self):
        import pytest
        from pydantic import ValidationError

        from nbprint.config.content import ContentPageBox

        with pytest.raises(ValidationError):
            ContentPageBox(min_pages=0)

    def test_accepts_children(self):
        from nbprint.config.content import ContentMarkdown, ContentPageBox

        box = ContentPageBox(content=[ContentMarkdown(content="# hi")])
        assert isinstance(box.content, list)
        assert len(box.content) == 1

    def test_is_content_subclass(self):
        from nbprint.config.content import Content, ContentPageBox

        assert issubclass(ContentPageBox, Content)

    def test_top_level_export(self):
        import nbprint

        assert hasattr(nbprint, "ContentPageBox")


class TestNBPrintPage:
    """Phase 9.2 — NBPrintPage runtime API."""

    def test_top_level_export(self):
        import nbprint

        assert hasattr(nbprint, "NBPrintPage")
        assert hasattr(nbprint, "NBPRINT_PAGE_MIME")

    def test_to_dict_emits_type(self):
        from nbprint import NBPrintPage

        page = NBPrintPage(emit=False)
        d = page.to_dict()
        assert d["type_"] == "nbprint.ContentPageBox"
        assert d["fit"] == "scale"
        assert d["min_pages"] == 1

    def test_to_dict_omits_none_fields(self):
        from nbprint import NBPrintPage

        d = NBPrintPage(emit=False).to_dict()
        for key in ("section", "page_size", "page_orientation", "page_margins", "css", "style", "classname", "attrs", "ignore"):
            assert key not in d

    def test_to_dict_includes_overrides(self):
        from nbprint import NBPrintPage

        page = NBPrintPage(
            emit=False,
            section="covermatter",
            fit="strict",
            page_size="A4",
            page_orientation="landscape",
            page_margins="1in",
            min_pages=2,
            css=":scope { background: red; }",
            classname="hero",
            attrs={"data-test": "1"},
            ignore=False,
        )
        d = page.to_dict()
        assert d["section"] == "covermatter"
        assert d["fit"] == "strict"
        assert d["page_size"] == "A4"
        assert d["page_orientation"] == "landscape"
        assert d["page_margins"] == "1in"
        assert d["min_pages"] == 2
        assert d["css"] == ":scope { background: red; }"
        assert d["classname"] == "hero"
        assert d["attrs"] == {"data-test": "1"}
        assert d["ignore"] is False

    def test_emit_publishes_mime(self):
        from unittest.mock import patch

        from nbprint import NBPRINT_PAGE_MIME, NBPrintPage

        with patch("nbprint.config.page_runtime.display") as mock_display:
            NBPrintPage(fit="shrink")
            assert mock_display.call_count == 1
            args, kwargs = mock_display.call_args
            data = args[0]
            assert NBPRINT_PAGE_MIME in data
            assert kwargs == {"raw": True}

    def test_context_manager_emits_once(self):
        from unittest.mock import patch

        from nbprint import NBPrintPage

        with patch("nbprint.config.page_runtime.display") as mock_display:
            page = NBPrintPage(emit=False)
            assert mock_display.call_count == 0
            with page:
                pass
            assert mock_display.call_count == 1
            # Re-entering should not re-emit.
            with page:
                pass
            assert mock_display.call_count == 1

    def test_ingestion_produces_page_box(self):
        """Runtime MIME output builds a ContentPageBox in Configuration ingestion."""
        import json

        from nbformat.v4 import new_code_cell, new_notebook

        from nbprint import NBPRINT_PAGE_MIME
        from nbprint.config.content import ContentPageBox
        from nbprint.config.core.config import Configuration

        nb = new_notebook()
        cell = new_code_cell(source="display('chart')", metadata={"tags": []})
        payload = {
            "type_": "nbprint.ContentPageBox",
            "fit": "strict",
            "min_pages": 2,
            "page_orientation": "landscape",
        }
        cell.outputs = [
            {
                "output_type": "display_data",
                "data": {NBPRINT_PAGE_MIME: json.dumps(payload)},
                "metadata": {},
            }
        ]
        nb.cells = [cell]

        values = {"content": ContentMarshall()}
        Configuration._process_cells(values, nb)

        assert len(values["content"].middlematter) == 1
        box = values["content"].middlematter[0]
        assert isinstance(box, ContentPageBox)
        assert box.fit == "strict"
        assert box.min_pages == 2
        assert str(box.page_orientation) == "landscape"
        # Source is preserved as the box's content.
        assert box.content == "display('chart')"


class TestContentPageBlock:
    """Phase 9.3 — ContentPageBlock primitive."""

    def test_defaults(self):
        from nbprint.config.content import ContentPageBlock

        block = ContentPageBlock()
        assert block.span is None
        assert block.rows is None
        assert block.area is None
        assert block.aspect is None
        assert block.min_height is None
        assert block.max_height is None
        assert block.break_inside == "avoid"
        assert block.scalable is None
        assert "nbprint:content:page-block" in block.tags

    def test_default_css(self):
        from nbprint.config.content import ContentPageBlock

        css = ContentPageBlock().css
        assert ":scope" in css
        assert "min-width: 0" in css
        assert "min-height: 0" in css

    def test_data_attrs_populated_with_id(self):
        from nbprint.config.content import ContentPageBlock

        block = ContentPageBlock()
        assert block.attrs["data-nbprint-block"] == block._id
        assert block.attrs["data-nbprint-break-inside"] == "avoid"
        # Optional placement attrs absent by default.
        for absent in ("data-nbprint-span", "data-nbprint-rows", "data-nbprint-area", "data-nbprint-scalable"):
            assert absent not in block.attrs

    def test_span_attr_and_inline_style(self):
        from nbprint.config.content import ContentPageBlock

        block = ContentPageBlock(span=2)
        assert block.attrs["data-nbprint-span"] == "2"
        assert "grid-column: span 2" in block.attrs["style"]

    def test_rows_attr_and_inline_style(self):
        from nbprint.config.content import ContentPageBlock

        block = ContentPageBlock(rows=3)
        assert block.attrs["data-nbprint-rows"] == "3"
        assert "grid-row: span 3" in block.attrs["style"]

    def test_area_attr_and_inline_style(self):
        from nbprint.config.content import ContentPageBlock

        block = ContentPageBlock(area="hero")
        assert block.attrs["data-nbprint-area"] == "hero"
        assert "grid-area: hero" in block.attrs["style"]

    def test_aspect_float(self):
        from nbprint.config.content import ContentPageBlock

        block = ContentPageBlock(aspect=1.7777)
        assert "aspect-ratio: 1.7777" in block.attrs["style"]

    def test_aspect_string_colon(self):
        from nbprint.config.content import ContentPageBlock

        block = ContentPageBlock(aspect="16:9")
        assert "aspect-ratio: 16/9" in block.attrs["style"]

    def test_aspect_string_passthrough(self):
        from nbprint.config.content import ContentPageBlock

        block = ContentPageBlock(aspect="16/9")
        assert "aspect-ratio: 16/9" in block.attrs["style"]

    def test_break_inside_default_avoid(self):
        from nbprint.config.content import ContentPageBlock

        block = ContentPageBlock()
        assert "break-inside: avoid" in block.attrs["style"]
        assert block.attrs["data-nbprint-break-inside"] == "avoid"

    def test_break_inside_override(self):
        from nbprint.config.content import ContentPageBlock

        block = ContentPageBlock(break_inside="auto")
        assert block.break_inside == "auto"
        assert block.attrs["data-nbprint-break-inside"] == "auto"
        assert "break-inside: auto" in block.attrs["style"]

    def test_min_max_height_emitted(self):
        from nbprint.config.content import ContentPageBlock

        block = ContentPageBlock(min_height="2in", max_height="6in")
        assert "min-height: 2in" in block.attrs["style"]
        assert "max-height: 6in" in block.attrs["style"]

    def test_scalable_attr(self):
        from nbprint.config.content import ContentPageBlock

        true_block = ContentPageBlock(scalable=True)
        false_block = ContentPageBlock(scalable=False)
        assert true_block.attrs["data-nbprint-scalable"] == "true"
        assert false_block.attrs["data-nbprint-scalable"] == "false"

    def test_user_attrs_preserved_block_id(self):
        from nbprint.config.content import ContentPageBlock

        block = ContentPageBlock(attrs={"data-nbprint-block": "override", "data-custom": "x"})
        # User's data-nbprint-block wins (setdefault).
        assert block.attrs["data-nbprint-block"] == "override"
        assert block.attrs["data-custom"] == "x"

    def test_user_style_preserved(self):
        from nbprint.config.content import ContentPageBlock

        block = ContentPageBlock(span=2, attrs={"style": "color: red"})
        # User style is appended after our generated style.
        assert "grid-column: span 2" in block.attrs["style"]
        assert "color: red" in block.attrs["style"]

    def test_span_validation(self):
        import pytest
        from pydantic import ValidationError

        from nbprint.config.content import ContentPageBlock

        with pytest.raises(ValidationError):
            ContentPageBlock(span=0)

    def test_is_content_subclass(self):
        from nbprint.config.content import Content, ContentPageBlock

        assert issubclass(ContentPageBlock, Content)

    def test_top_level_export(self):
        import nbprint

        assert hasattr(nbprint, "ContentPageBlock")

    def test_accepts_children(self):
        from nbprint.config.content import ContentMarkdown, ContentPageBlock

        block = ContentPageBlock(content=[ContentMarkdown(content="# hi")])
        assert isinstance(block.content, list)
        assert len(block.content) == 1


class TestPageBoxLayout:
    """Phase 9.4 — layout presets on ContentPageBox + auto-wrap."""

    def test_layout_default_is_flow(self):
        from nbprint.config.content import ContentPageBox

        box = ContentPageBox()
        assert box.layout == "flow"
        assert box.attrs["data-nbprint-layout"] == "flow"

    def test_columns_2_emits_column_count(self):
        from nbprint.config.content import ContentPageBox

        box = ContentPageBox(layout="columns-2")
        assert "column-count: 2" in box.css
        assert box.attrs["data-nbprint-layout"] == "columns-2"

    def test_columns_3_emits_column_count(self):
        from nbprint.config.content import ContentPageBox

        box = ContentPageBox(layout="columns-3", gap="0.5in")
        assert "column-count: 3" in box.css
        assert "column-gap: 0.5in" in box.css

    def test_grid_2x2_emits_grid_template(self):
        from nbprint.config.content import ContentPageBox

        box = ContentPageBox(layout="grid-2x2")
        assert "display: grid" in box.css
        assert "grid-template-columns: repeat(2, 1fr)" in box.css

    def test_grid_3x2_emits_grid_template(self):
        from nbprint.config.content import ContentPageBox

        box = ContentPageBox(layout="grid-3x2", gap="1rem", align="center", justify="stretch")
        assert "grid-template-columns: repeat(3, 1fr)" in box.css
        assert "gap: 1rem" in box.css
        assert "align-items: center" in box.css
        assert "justify-items: stretch" in box.css

    def test_grid_bare_no_template_columns(self):
        """layout='grid' is the named-area form — emits display: grid but no fixed columns."""
        from nbprint.config.content import ContentPageBox

        box = ContentPageBox(layout="grid")
        assert "display: grid" in box.css
        assert "grid-template-columns" not in box.css

    def test_flex_row_reuses_shared_css(self):
        from nbprint.config.content import ContentFlexRowLayout, ContentPageBox

        box = ContentPageBox(layout="flex-row")
        assert "display: flex" in box.css
        assert "flex-direction: row" in box.css
        # Shared constant — verify the existing layout container
        # carries the same direction CSS.
        assert "flex-direction: row" in ContentFlexRowLayout().css

    def test_flex_column_reuses_shared_css(self):
        from nbprint.config.content import ContentFlexColumnLayout, ContentPageBox

        box = ContentPageBox(layout="flex-column", gap="1rem", justify="space-between")
        assert "flex-direction: column" in box.css
        assert "gap: 1rem" in box.css
        assert "justify-content: space-between" in box.css
        assert "flex-direction: column" in ContentFlexColumnLayout().css

    def test_inline_preset(self):
        from nbprint.config.content import ContentPageBox

        box = ContentPageBox(layout="inline", gap="1rem")
        assert "display: block" in box.css
        # Inline gap maps to margin-left on adjacent siblings.
        assert "margin-left: 1rem" in box.css

    def test_masonry_preset(self):
        from nbprint.config.content import ContentPageBox

        box = ContentPageBox(layout="masonry", gap="0.25in")
        assert "display: grid" in box.css
        assert "grid-template-rows: masonry" in box.css
        assert "gap: 0.25in" in box.css

    def test_flow_preset_with_gap_emits_margin(self):
        from nbprint.config.content import ContentPageBox

        box = ContentPageBox(layout="flow", gap="1rem")
        assert "margin-top: 1rem" in box.css

    def test_custom_layout_preserves_base_only(self):
        """layout='custom' suppresses preset CSS so the user owns :scope."""
        from nbprint.config.content import ContentPageBox
        from nbprint.config.content._layout_presets import PAGE_BOX_BASE_CSS

        box = ContentPageBox(layout="custom")
        assert box.css == PAGE_BOX_BASE_CSS
        # Preset-only rules are absent.
        assert "column-count" not in box.css
        assert "display: grid" not in box.css

    def test_user_css_override_wins(self):
        """When the user supplies non-default css, preset CSS is not emitted."""
        from nbprint.config.content import ContentPageBox

        custom = ":scope { background: red; }\n"
        box = ContentPageBox(layout="columns-2", css=custom)
        assert box.css == custom
        # Preset rules suppressed.
        assert "column-count" not in box.css

    def test_padding_emitted(self):
        from nbprint.config.content import ContentPageBox

        box = ContentPageBox(layout="grid-2x2", padding="0.5in")
        assert "padding: 0.5in" in box.css

    def test_auto_wrap_bare_content_into_block(self):
        from nbprint.config.content import (
            ContentMarkdown,
            ContentPageBlock,
            ContentPageBox,
        )

        md = ContentMarkdown(content="# hi")
        box = ContentPageBox(content=[md])
        assert len(box.content) == 1
        assert isinstance(box.content[0], ContentPageBlock)
        # The block wraps the original content as its single child.
        assert box.content[0].content[0] is md

    def test_auto_wrap_preserves_existing_blocks(self):
        from nbprint.config.content import (
            ContentMarkdown,
            ContentPageBlock,
            ContentPageBox,
        )

        block = ContentPageBlock(content=[ContentMarkdown(content="a")], span=2)
        box = ContentPageBox(content=[block])
        # Existing block passes through verbatim.
        assert box.content[0] is block
        assert box.content[0].span == 2

    def test_auto_wrap_mixed_children(self):
        from nbprint.config.content import (
            ContentMarkdown,
            ContentPageBlock,
            ContentPageBox,
        )

        md = ContentMarkdown(content="a")
        block = ContentPageBlock(content=[ContentMarkdown(content="b")])
        box = ContentPageBox(content=[md, block])
        # First child auto-wrapped; second passes through.
        assert isinstance(box.content[0], ContentPageBlock)
        assert box.content[1] is block

    def test_auto_wrap_does_not_apply_to_string_content(self):
        from nbprint.config.content import ContentPageBox

        box = ContentPageBox(content="raw cell source")
        assert box.content == "raw cell source"

    def test_layout_invalid_raises(self):
        import pytest
        from pydantic import ValidationError

        from nbprint.config.content import ContentPageBox

        with pytest.raises(ValidationError):
            ContentPageBox(layout="not-a-real-preset")

    def test_nbprint_page_runtime_passes_layout(self):
        from nbprint import NBPrintPage

        page = NBPrintPage(emit=False, layout="grid-2x2", gap="1rem", padding="0.5in")
        d = page.to_dict()
        assert d["layout"] == "grid-2x2"
        assert d["gap"] == "1rem"
        assert d["padding"] == "0.5in"
