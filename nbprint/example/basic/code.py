from nbprint import Content

__all__ = ("ExampleCodeBlock",)


class ExampleCodeBlock(Content):
    def __call__(self, ctx=None, *args, **kwargs):
        from great_tables import GT

        return (
            GT(ctx.df)
            .tab_header(title="Sample Table")
            .tab_source_note("This is where authors provide additional information about the data, including whatever notes are needed.")
            .fmt_number(decimals=2)
        )
