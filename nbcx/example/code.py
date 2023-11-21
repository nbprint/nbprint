from nbcx import NBCXContentDynamic, table


class ExampleCodeBlock(NBCXContentDynamic):
    def __call__(self, ctx=None, *args, **kwargs):
        return table(
            ctx.df[["A", "B", "C", "D"]].head(20),
            "Sample Table",
            "This is where authors provide additional information about the data, including whatever notes are needed.",
        )
