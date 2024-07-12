from nbprint.config.base import BaseModel

__all__ = ("_BaseCss",)


class _BaseCss(BaseModel):
    important: bool = False
