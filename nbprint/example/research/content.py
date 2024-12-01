from IPython.display import HTML

from nbprint import Content, ContentFlexColumnLayout, ContentFlexRowLayout, Role

__all__ = (
    "ExampleResearchAuthor",
    "ExampleResearchAuthors",
    "ExampleResearchBody",
    "ExampleResearchHeader",
    "ExampleResearchSectionText",
    "ExampleResearchSectionTitle",
    "ExampleResearchTitle",
)


class ExampleResearchHeader(ContentFlexColumnLayout):
    role: Role = Role.LAYOUT
    css: str = """
:scope {
  padding-top: 50px;
  display: flex;
  flex-direction: column;
  padding-bottom: 50px;
}
"""

    def __call__(self, ctx=None, *args, **kwargs):
        # return empty html just for placeholder
        return HTML("")


class ExampleResearchTitle(Content):
    title: str

    css: str = """
:scope {
}

h1 {
  font-family: serif;
  font-weight: bold !important;
  font-size: 25px !important;
  margin: auto !important;
}
    """

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"""
        <div class="row">
            <h1>{self.title}</h1>
        </div>
        """)


class ExampleResearchAuthor(Content):
    name: str
    email: str

    css: str = """
:scope {
  text-align: center;
}
div.column > span:nth-child(1) {
  font-size: 16px;
  font-family: serif !important;
}
div.column > span:nth-child(2) {
  font-size: 12px;
  font-family: sans-serif !important;
}
    """

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"""
        <div class="column">
            <span>{self.name}</span>
            <span>{self.email}</span>
        </div>
        """)


class ExampleResearchAuthors(ContentFlexRowLayout): ...


class ExampleResearchBody(Content):
    role: Role = Role.LAYOUT
    css: str = """
:scope {
  column-count: 2;
  -webkit-column-count: 2;
  column-gap: 1cm;
}
"""

    def __call__(self, ctx=None, *args, **kwargs):
        # return empty html just for placeholder
        return HTML("")


class ExampleResearchSectionTitle(Content):
    title: str

    css: str = """
  h1 {
    padding-bottom: 10px;
  }
  """

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"<h1>{self.title}</h1>")


class ExampleResearchSectionText(Content):
    text: str

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"<p>{self.text}</p>")
