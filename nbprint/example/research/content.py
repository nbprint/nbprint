from IPython.display import HTML
from pydantic import validator
from typing import List

from nbprint import Content, Role


class ExampleResearchHeader(Content):
    role: Role = Role.LAYOUT
    css: str = """
:scope {
  display: flex;
  flex-direction: column;
}
"""

    def __call__(self, ctx=None, *args, **kwargs):
        # return empty html just for placeholder
        return HTML("")


class ExampleResearchTitle(Content):
    title: str

    css: str = """
:scope {
  margin-top: 50px;
  margin-bottom: 50px;
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


class ExampleResearchAuthors(Content):
    role: Role = Role.LAYOUT
    css: str = """
:scope {
  display: flex;
  flex-direction: row;
  margin: auto;
}
    """

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML("")


class ExampleResearchBody(Content):
    role: Role = Role.LAYOUT
    css: str = """
:scope {
  margin: auto;
  display: flex;
  flex-direction: column;
  width: 48%;
}
"""


class ExampleResearchAbstract(Content):
    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"""
            <h1>Abstract</h1>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
        """)


class ExampleResearchIntroduction(Content): ...


class ExampleResearchSecondSection(Content): ...


class ExampleResearchConclusion(Content): ...


class ExampleResearchReferences(Content): ...
