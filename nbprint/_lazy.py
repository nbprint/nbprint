from importlib import import_module
from typing import Callable

__all__ = ("lazy_star_import",)


def lazy_star_import(package: str, submodules: tuple[str, ...]) -> Callable[[str], object]:
    """Return a module ``__getattr__`` that emulates ``from .submodule import *`` on first access."""

    def getattr_(name: str) -> object:
        namespace = vars(import_module(package))
        for submodule in submodules:
            module = import_module(f"{package}.{submodule}")
            exported = getattr(module, "__all__", None) or [n for n in vars(module) if not n.startswith("_")]
            namespace.update({n: getattr(module, n) for n in exported})
        if name in namespace:
            return namespace[name]
        msg = f"module {package!r} has no attribute {name!r}"
        raise AttributeError(msg)

    return getattr_
