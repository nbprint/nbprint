from IPython.display import Markdown
from pydantic import Field

from nbprint.config.common import FontStyle, FontWeight, HorizontalAlignment, TextDecoration, VerticalAlignment

from .base import Content


class TextComponent(Content):
    text: str | None = ""
    horizontal_alignment: HorizontalAlignment | None = None
    vertical_alignment: VerticalAlignment | None = None
    font_weight: FontWeight | None = None
    font_style: FontStyle | None = None
    text_decoration: TextDecoration | None = None

    tags: list[str] = Field(default_factory=list)

    def render(self, **kwargs) -> None:
        # Build CSS from text formatting fields before the base render merges style
        parts = []
        if self.horizontal_alignment:
            parts.append(f"text-align: {self.horizontal_alignment};")
        if self.vertical_alignment:
            parts.append(f"vertical-align: {self.vertical_alignment};")
        if self.font_weight:
            parts.append(f"font-weight: {self.font_weight};")
        if self.font_style:
            parts.append(f"font-style: {self.font_style};")
        if self.text_decoration:
            parts.append(f"text-decoration: {self.text_decoration};")
        if parts:
            text_css = ":scope {\n" + "\n".join(parts) + "\n}"
            if self.css:
                self.css = f"{self.css}\n{text_css}"
            else:
                self.css = text_css
        super().render(**kwargs)

    def __call__(self, **_) -> Markdown:
        return Markdown(self.text)
