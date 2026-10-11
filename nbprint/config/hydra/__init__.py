from collections.abc import Callable

__all__ = ("load_config",)


def __getattr__(name: str) -> Callable:
    # Deferred so lerna can locate this config package without importing ccflow
    if name == "load_config":
        from .loader import load_config

        return load_config
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
