from nbprint import (
    Border,
    BorderLineStyle,
    BorderStyle,
    Element,
    Font,
    FontFamily,
    FontStyle,
    FontWeight,
    Padding,
    Scope,
    Spacing,
    Style,
    TextTransform,
)


class TestStyles:
    def test_basic_style_scope(self):
        s = Style(
            scope=Scope(
                element="div",
                classname="row",
            ),
            spacing=Spacing(padding=Padding(bottom=10)),
        )

        assert str(s) == "div.row {\npadding-bottom: 10px;\n}"

    def test_basic_style_text_padding_border(self):
        s = Style(
            scope=Scope(
                element="h1",
            ),
            font=Font(
                family=FontFamily.sans_serif,
                size=25,
            ),
            spacing=Spacing(padding=Padding(right=15)),
            border=Border(
                right=BorderStyle(
                    width=2,
                    style=BorderLineStyle.solid,
                    color="black",
                )
            ),
        )
        assert str(s) == "h1 {\npadding-right: 15px;\nfont-family: sans-serif;\nfont-size: 25px;\nborder-right: 2px solid black;\n}"

    def test_basic_style_text_padding_border2(self):
        s = Style(
            scope=Scope(
                element=Element.h2,
            ),
            font=Font(
                family=FontFamily.sans_serif,
                size=12,
                transform=TextTransform.uppercase,
                weight=FontWeight.bold,
            ),
            spacing=Spacing(padding=Padding(left=15)),
        )

        assert str(s) == "h2 {\npadding-left: 15px;\nfont-family: sans-serif;\nfont-size: 12px;\ntext-transform: uppercase;\nfont-weight: bold;\n}"

    def test_basic_style_text_padding_border3(self):
        s = Style(
            scope=Scope(
                element=Element.span,
            ),
            font=Font(size=15, style=FontStyle.italic, color="grey"),
        )

        assert str(s) == "span {\nfont-size: 15px;\nfont-style: italic;\ncolor: grey;\n}"

    def test_style_without_scope(self):
        """Style without a scope renders just the CSS properties."""
        s = Style(
            font=Font(size=14, weight=FontWeight.bold),
            spacing=Spacing(padding=Padding(top=5)),
        )
        result = str(s)
        assert "padding-top: 5px" in result
        assert "font-size: 14px" in result
        assert "font-weight: bold" in result
        # No selector wrapping
        assert "{" not in result

    def test_style_to_css_properties(self):
        s = Style(
            scope=Scope(element="div"),
            font=Font(size=10),
            border=Border(top=BorderStyle(width=1, style=BorderLineStyle.solid, color="red")),
        )
        props = s.to_css_properties()
        assert "font-size: 10px" in props
        assert "border-top:" in props
        # No selector in properties-only output
        assert "div" not in props

    def test_style_merge(self):
        base = Style(
            font=Font(size=12, weight=FontWeight.normal),
            spacing=Spacing(padding=Padding(left=10)),
        )
        override = Style(
            font=Font(size=18, weight=FontWeight.bold),
        )
        merged = base.merge(override)
        assert merged.font.size == 18
        assert merged.font.weight == FontWeight.bold
        # spacing preserved from base
        assert merged.spacing.padding.left == 10

    def test_style_merge_does_not_mutate(self):
        base = Style(font=Font(size=12))
        override = Style(font=Font(size=24))
        merged = base.merge(override)
        assert base.font.size == 12
        assert merged.font.size == 24


class TestDisplay:
    def test_display_flex(self):
        from nbprint import Display, DisplayKind, FlexDirection, FlexOptions, Justify

        d = Display(
            display=DisplayKind.flex,
            flex_options=FlexOptions(flex_direction=FlexDirection.row, justify=Justify.space_between),
        )
        result = str(d)
        assert "display: flex;" in result
        assert "flex-direction: row;" in result
        assert "justify-content: space-between;" in result

    def test_display_none(self):
        from nbprint import Display, DisplayKind

        d = Display(display=DisplayKind.none)
        assert str(d) == "display: none;"

    def test_flex_options_partial(self):
        from nbprint import FlexDirection, FlexOptions

        f = FlexOptions(flex_direction=FlexDirection.column)
        assert str(f) == "flex-direction: column;"

    def test_display_empty(self):
        from nbprint import Display

        d = Display()
        assert str(d) == ""


class TestContentStyleWiring:
    """Test that Content.style is merged into CSS during generation."""

    def test_style_merged_into_css(self):
        from nbprint.config.content import ContentCode

        c = ContentCode(
            content="x = 1",
            style=Style(font=Font(size=16, weight=FontWeight.bold)),
        )
        # Simulate render (which is called during generate)
        c._merge_style_css()
        assert ":scope {" in c.css
        assert "font-size: 16px" in c.css
        assert "font-weight: bold" in c.css

    def test_style_appended_to_existing_css(self):
        from nbprint.config.content import ContentCode

        c = ContentCode(
            content="x = 1",
            css=".custom { color: blue; }",
            style=Style(spacing=Spacing(padding=Padding(bottom=20))),
        )
        c._merge_style_css()
        assert ".custom { color: blue; }" in c.css
        assert "padding-bottom: 20px" in c.css

    def test_no_style_leaves_css_unchanged(self):
        from nbprint.config.content import ContentCode

        c = ContentCode(content="x = 1", css="existing")
        c._merge_style_css()
        assert c.css == "existing"

    def test_style_generates_into_cell_metadata(self):
        """Full generate() path: style ends up in cell.metadata.nbprint.css."""
        from nbprint.config.core.config import Configuration

        config = Configuration(
            name="test-style",
            outputs={"_target_": "nbprint.NBConvertOutputs", "naming": "{{name}}", "root": ".pytest_cache/test_style"},
            content={"middlematter": [{"_target_": "nbprint.ContentMarkdown", "content": "hello", "style": {"font": {"size": 20}}}]},
        )
        nb = config.generate()
        # Find the markdown cell
        md_cells = [c for c in nb.cells if c.cell_type == "markdown"]
        assert len(md_cells) == 1
        assert "font-size: 20px" in md_cells[0].metadata.nbprint.css


class TestTextComponentWiring:
    """Test that TextComponent formatting fields are rendered to CSS."""

    def test_text_component_alignment(self):
        from nbprint.config.content.common import TextComponent

        tc = TextComponent(
            text="Hello",
            horizontal_alignment="center",
            font_weight="bold",
        )
        tc.render()
        assert "text-align: center;" in tc.css
        assert "font-weight: bold;" in tc.css

    def test_text_component_all_fields(self):
        from nbprint.config.content.common import TextComponent

        tc = TextComponent(
            text="Test",
            horizontal_alignment="right",
            vertical_alignment="top",
            font_weight="bold",
            font_style="italic",
            text_decoration="underline",
        )
        tc.render()
        assert "text-align: right;" in tc.css
        assert "vertical-align: top;" in tc.css
        assert "font-weight: bold;" in tc.css
        assert "font-style: italic;" in tc.css
        assert "text-decoration: underline;" in tc.css

    def test_text_component_no_fields_no_css(self):
        from nbprint.config.content.common import TextComponent

        tc = TextComponent(text="Plain")
        tc.render()
        assert tc.css == ""

    def test_text_component_with_style_combines(self):
        """TextComponent formatting and style both contribute to CSS."""
        from nbprint.config.content.common import TextComponent

        tc = TextComponent(
            text="Both",
            font_weight="bold",
            style=Style(spacing=Spacing(padding=Padding(left=10))),
        )
        tc.render()
        assert "font-weight: bold;" in tc.css
        assert "padding-left: 10px" in tc.css
