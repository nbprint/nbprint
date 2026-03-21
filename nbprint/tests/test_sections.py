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
    def test_page_no_size_or_orientation(self):
        """Base Page no longer has size/orientation (moved to PageGlobal)."""
        p = Page()
        assert not hasattr(p, "size")
        assert not hasattr(p, "orientation")

    def test_page_no_pages_field(self):
        """Base Page no longer has a pages dict (moved to PageGlobal)."""
        p = Page()
        assert not hasattr(p, "pages") or p.__class__.__name__ != "Page" or "pages" not in Page.model_fields


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
