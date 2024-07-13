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
