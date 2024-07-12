from IPython.display import HTML
from pydantic import Field

from nbprint.config.base import Role

from .base import Content

__all__ = (
    "ContentLayout",
    "ContentInlineLayout",
    "ContentFlexColumnLayout",
    "ContentFlexRowLayout",
)


class _ContentFlexLayout(Content):
    """Private class to represent a generic flex layout."""

    # component to split into certain number of columns
    # count: int = 1
    sizes: list[float] = Field(default_factory=list)

    # override role
    role: Role = Role.LAYOUT

    css: str = ":scope { display: flex; }"
    esm: str = """
function render(meta, elem) {
    let data = JSON.parse(meta.data);

    if (data.sizes.length <= 0 )
        return;

    let size_index = 0;

    Array.from(elem.children).forEach((child) => {
        let size = data.sizes[size_index];

        if (!size)
            return;

        // TODO these are hacks to determin
        // if it should be included
        let output_children = (child.querySelector(".jp-OutputArea-output") || {}).children || [];
        if (Array.from(child.classList).includes("nbprint")) {
            child.style.flex = `${size}`;
            size_index += 1;
        } else if (Array.from(output_children).length > 0) {
            child.style.flex = `${size}`;
            size_index += 1;
        } else {
            child.style.flex = "0";
        }
    });
}
"""
    attrs: dict = Field(default_factory=dict)

    def __call__(self, *_, **__) -> HTML:
        """Generate IPython HTML for object."""
        # return empty html just for placeholder
        return HTML("")


class ContentLayout(Content):
    """Class to represent a generic layout, does no html or css configuration."""

    # override role
    role: Role = Role.LAYOUT

    def __call__(self, *_, **__) -> HTML:
        """Generate IPython HTML for object."""
        # return empty html just for placeholder
        return HTML("")


class ContentInlineLayout(Content):
    """Class to represent a div with block display and inline layout."""

    # override role
    role: Role = Role.LAYOUT

    css: str = ":scope { display: block; }"
    esm: str = """
function render(meta, elem) {
    let data = JSON.parse(meta.data);

    Array.from(elem.children).forEach((child) => {
        // TODO these are hacks to determin
        // if it should be included
        let output_children = (child.querySelector(".jp-OutputArea-output") || {}).children || [];
        if (Array.from(child.classList).includes("nbprint")) {
            child.style.display = "inline-block";
            child.style.float = "left";
        } else if (Array.from(output_children).length > 0) {
            child.style.display = "inline-block";
            child.style.float = "left";
        }
    });
}
"""
    attrs: dict = Field(default_factory=dict)

    def __call__(self, *_, **__) -> HTML:
        """Generate IPython HTML for object."""
        return HTML("")


class ContentFlexColumnLayout(_ContentFlexLayout):
    """Class to represent a div with flex column layout."""

    css: str = """
:scope { display: flex; flex-direction: column; break-inside: auto; }
"""


class ContentFlexRowLayout(_ContentFlexLayout):
    """Class to represent a div with flex row layout."""

    css: str = """
:scope { display: flex; flex-direction: row; break-inside: auto; }
"""
