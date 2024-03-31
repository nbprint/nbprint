from IPython.display import HTML
from pydantic import Field
from typing import List

from ..base import Role
from .base import Content


class _ContentFlexLayout(Content):
    # component to split into certain number of columns
    # count: int = 1
    sizes: List[float] = [1.0]

    # override role
    role: Role = Role.LAYOUT

    classname: str = "nbprint-flex-layout"
    css: str = "div.nbprint-flex-layout { display: flex; }"
    esm: str = """
function render(meta, elem) {
    let data = JSON.parse(meta.data);
    if (data.sizes.length > 1 ) {
        data.sizes.forEach((size, index) => {
            const child = elem.children[index];
            if(child) {
                child.style.flex = `${size}`;
            }
        });
    }
}"""
    attrs: dict = Field(default_factory=dict)

    def __call__(self, ctx=None, *args, **kwargs):
        # return empty html just for placeholder
        return HTML("")


class ContentFlexColumnLayout(_ContentFlexLayout):
    classname: str = "nbprint-column-layout"
    css: str = ":scope { display: flex; flex-direction: column; }"


class ContentFlexRowLayout(_ContentFlexLayout):
    classname: str = "nbprint-row-layout"
    css: str = ":scope { display: flex; flex-direction: row; }"
