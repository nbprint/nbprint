from IPython.display import Image


def image(data=None, path=None, **kwargs) -> Image:
    """Display a image"""
    # measure in pixels for html, but cm for latex
    width = kwargs.get("width", "")
    height = kwargs.get("height", "")
    align = kwargs.pop("align", "left")
    metadata = kwargs.pop("metadata", {})

    if width:
        if isinstance(width, str) and not width.endswith("cm"):
            widthcm = width + "cm"
        elif not isinstance(width, str):
            # assume in pixels, get cm

            # TODO: assume 96 DPI
            widthcm = f"{int(width / 36)}cm"
        else:
            # assume already in cm, get pixels
            width, widthcm = float(width.replace("cm", "")), width

            # TODO: assume 96 DPI
            width = int(width * 36)
            kwargs["width"] = width
    else:
        widthcm = ""

    if height:
        if isinstance(height, str) and not height.endswith("cm"):
            heightcm = height + "cm"
        elif not isinstance(height, str):
            # assume in pixels, get cm

            # TODO: assume 96 DPI
            heightcm = f"{int(height / 36)}cm"

        else:
            # assume already in cm, get pixels
            height, heightcm = float(height.replace("cm", "")), height

            # TODO: assume 96 DPI
            height = int(height * 36)
            kwargs["height"] = height
    else:
        heightcm = ""

    metadata["widthcm"] = widthcm
    metadata["heightcm"] = heightcm
    metadata["align"] = align

    if path:
        return Image(filename=path, metadata=metadata, **kwargs)
    return Image(data=data, metadata=metadata, **kwargs)
