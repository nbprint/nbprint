from __future__ import annotations

from IPython.display import HTML, Image
from pathlib import Path
from pydantic import Field, FilePath, field_validator

from .base import Content


class ContentImage(Content):
    """Class to represent image content inside a cell."""

    path: FilePath | None = Field(default=None)
    content: bytes = Field(default=b"")
    tags: list[str] = Field(default=["nbprint:content", "nbprint:content:image"])

    @field_validator("path", mode="before")
    @classmethod
    def convert_path_from_obj(cls, v) -> Path:
        """Helper method to convert string to resolved path."""
        if isinstance(v, str):
            v = Path(v).resolve()
        return v

    @field_validator("content", mode="before")
    @classmethod
    def convert_content_from_obj(cls, v) -> bytes:
        """Helper method to read image content from string or path into bytes."""
        if v is None:
            return b""
        if v and isinstance(v, str):
            v = Path(v).resolve()
        if v and isinstance(v, Path):
            v = v.read_bytes()
        return v

    def as_base64(self) -> str:
        """Helper methoid to convert image to base64 encoded binary."""
        img = Image(filename=self.path) if self.path else Image(data=self.content)
        return img._repr_png_()

    def __call__(self, *_, **__) -> HTML:
        """Generate IPython HTML for object."""
        return HTML(f"""<img src="data:image/png;base64,{self.as_base64()}">""")

    def __repr__(self) -> str:
        """Helper override to avoid verbose repr."""
        return f"Image(path='{self.path}', content=[{len(self.content)} bytes])"
