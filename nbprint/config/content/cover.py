from pydantic import Field, field_validator

from .base import Content

# Default cover styling. A cover page is a centred column of title, subtitle and
# logo in every document that has one, so shipping it here saves each consumer
# reimplementing the same block. Tunables are custom properties rather than
# hardcoded values, so the common adjustments do not require replacing the whole
# rule; assigning ``css`` explicitly overrides it outright.
DEFAULT_COVER_CSS = """\
:scope div.jp-RenderedHTML {
  width: var(--nbprint-cover-width, 75%);
  margin: auto;
  display: flex;
  flex-direction: column;
  text-align: center;
}

:scope div.jp-RenderedHTML img {
  margin: auto;
  width: var(--nbprint-cover-logo-width, 200px);
}

:scope h1 {
  margin-bottom: var(--nbprint-cover-title-gap, 10px);
}

:scope h2,
:scope h3 {
  margin-top: var(--nbprint-cover-subtitle-gap, 5px);
  margin-bottom: var(--nbprint-cover-subtitle-gap, 5px);
}
"""


class ContentCover(Content):
    tags: list[str] = Field(default_factory=list)
    css: str = DEFAULT_COVER_CSS

    @field_validator("tags", mode="after")
    @classmethod
    def _ensure_tags(cls, v: list[str]) -> list[str]:
        if "nbprint:content:cover" not in v:
            v.append("nbprint:content:cover")
        return v
