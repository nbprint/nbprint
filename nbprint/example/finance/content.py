from IPython.display import HTML

from nbprint import Content
from nbprint.utils.ipython import DisplayList


class ExampleFinanceTitleContent(Content):
    title: str = ""
    sep: str = "|"
    subtitle: str = ""
    date: str = ""

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"""
        <div class="nbprint-row">
            <h1>{self.title} {self.sep} </h1>
            <h3 class="pl5">{self.subtitle}</h3>
        </div>
        <div class="nbprint-row">
            <h5>{self.date}</h5>
        </div>
        """)


class ExampleFinanceStockHeadlineContent(Content):
    company_name: str = ""
    sep: str = "|"
    region: str = ""
    byline: str = ""

    def __call__(self, ctx=None, *args, **kwargs):
        return DisplayList(
            HTML(f"<h3>{self.company_name} {self.sep} {self.region}</h3>"),
            HTML(f"<h1>{self.byline}</h1>"),
        )
