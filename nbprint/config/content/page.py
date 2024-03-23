from IPython.display import HTML
from typing import List, Optional

from ..utils import Role
from .base import Content


class _ContentFlexLayout(Content):
    # component to split into certain number of columns
    # count: int = 1
    sizes: List[float] = [1.0]
    separator_size: Optional[str] = None
    separator_color: Optional[str] = None

    # override role
    role: Role = Role.LAYOUT

    classname: str = "nbprint-flex-layout"
    css: str = "div.nbprint-flex-layout { display: flex; }"
    esm: str = """
function render(meta, elem) {
    console.log(meta);
    console.log(elem);
    let data = JSON.parse(meta.data);
    if (data.sizes.length > 1 ) {
        const sum =
        data.sizes.forEach((size, index) => {
            console.log(size);
            console.log(index);
            const child = elem.children[index];
            console.log(child);
            if(child) {
                child.style.flex = `${size}`;
            }
        });
    }
}"""
    attrs: dict = {"test": "abcd"}

    def __call__(self, ctx=None, *args, **kwargs):
        # return empty html just for placeholder
        return HTML("")


class ContentFlexColumnLayout(_ContentFlexLayout):
    classname: str = "nbprint-column-layout"
    css: str = "div.nbprint-column-layout { display: flex; flex-direction: column; }"


class ContentFlexRowLayout(_ContentFlexLayout):
    classname: str = "nbprint-row-layout"
    css: str = "div.nbprint-row-layout { display: flex; flex-direction: row; }"
