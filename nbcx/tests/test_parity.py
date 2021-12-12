class TestParity:
    def test_parity(self):
        import nbcx.utils.html as html
        import nbcx.utils.latex as latex

        _OMIT = (
            "Box",
            "BytesIO",
            "convert_pandoc",
            "display",
            "dt",
            "du",
            "html",
            "HTML",
            "Image",
            "latex",
            "Latex",
            "Output",
            "plot",
        )

        html_exps = [x for x in dir(html) if not (x in _OMIT or x.startswith("_"))]
        latex_exps = [x for x in dir(latex) if not (x in _OMIT or x.startswith("_"))]

        print(html_exps)
        print(latex_exps)
        assert set(html_exps) == set(latex_exps)
