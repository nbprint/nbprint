__all__ = (
    "NBPrintBadScopeError",
    "NBPrintConfigurationError",
    "NBPrintConfigurationError",
    "NBPrintGenerationError",
    "NBPrintGenerationError",
    "NBPrintNullCellError",
    "NBPrintPathOrModelMalformedError",
)


class NBPrintGenerationError(RuntimeError): ...


class NBPrintConfigurationError(RuntimeError): ...


class NBPrintNullCellError(NBPrintGenerationError):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("got null cell, investigate!", *args, **kwargs)


class NBPrintBadScopeError(NBPrintConfigurationError):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("Must set one of element, classname, id, or selector", *args, **kwargs)


class NBPrintPathOrModelMalformedError(NBPrintConfigurationError):
    def __init__(self, path_or_model, *args, **kwargs) -> None:
        super().__init__(f"Path or model malformed: {path_or_model} {type(path_or_model)}", *args, **kwargs)
