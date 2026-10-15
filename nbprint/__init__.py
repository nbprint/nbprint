__version__ = "0.13.0"

from typing import TYPE_CHECKING

from ._lazy import lazy_star_import as _lazy_star_import

if TYPE_CHECKING:
    from .cli import *
    from .config import *
    from .models import *
    from .utils import *

# Loaded on first attribute access so that importing ``nbprint.config.hydra``
# (e.g. via the lerna search path plugin) does not import the whole package.
__getattr__ = _lazy_star_import(__name__, ("cli", "config", "models", "utils"))
