from pathlib import Path
from typing import Optional

from IPython.display import HTML, Image
from pydantic import Field, FilePath, field_validator

from .base import Content


class ContentImage(Content):
    path: Optional[FilePath] = None
    content: Optional[bytes] = b""
    tags: list[str] = Field(default=["nbprint:content", "nbprint:content:image"])

    @field_validator("path", mode="before")
    @classmethod
    def convert_path_from_obj(cls, v) -> Path:
        if isinstance(v, str):
            v = Path(v).resolve()
        return v

    @field_validator("content", mode="before")
    @classmethod
    def convert_content_from_obj(cls, v) -> bytes:
        if v is None:
            return b""
        if v and isinstance(v, str):
            v = Path(v).resolve()
        if v and isinstance(v, Path):
            v = v.read_bytes()
        return v

    def as_base64(self) -> str:
        img = Image(filename=self.path) if self.path else Image(data=self.content)
        return img._repr_png_()

    def __call__(self, **_) -> HTML:
        return HTML(f"""<img src="data:image/png;base64,{self.as_base64()}">""")

    def __repr__(self) -> str:
        return f"Image(path='{self.path}', content=[{len(self.content)} bytes])"
