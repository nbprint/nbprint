from nbprint._lazy import lazy_star_import as _lazy_star_import

__getattr__ = _lazy_star_import(
    __name__,
    ("base", "block_runtime", "cell", "common", "content", "core", "magic", "outputs", "overlay", "page_runtime"),
)
