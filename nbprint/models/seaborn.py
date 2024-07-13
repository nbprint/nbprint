from typing import List, Literal, Union

from IPython.display import HTML
from pydantic import Field

from nbprint import Content

__all__ = ("SeabornDisplayConfiguration",)


class SeabornDisplayConfiguration(Content):
    style: Literal["white", "dark", "whitegrid", "darkgrid", "ticks"] = Field(default="whitegrid")
    context: Literal["paper", "notebook", "talk", "poster"] = Field(default="notebook")
    palette: Union[str, List[str]] = Field(default="tab10")

    def __call__(self, ctx=None, *args, **kwargs):
        import seaborn as sns

        sns.set_theme(self.context, self.style, self.palette)
        return HTML("")
