from strenum import StrEnum

__all__ = (
    "PageOrientation",
    "PageSize",
)


class PageSize(StrEnum):
    A0 = "A0"  # 841 x 1189 mm
    A1 = "A1"  # 594 x 841 mm
    A2 = "A2"  # 420 x 594 mm
    A3 = "A3"  # 297 x 420 mm
    A4 = "A4"  # 210 x 297 mm
    A5 = "A5"  # 148 x 210 mm
    A6 = "A6"  # 105 x 148 mm
    A7 = "A7"  # 74 x 105 mm
    A10 = "A10"  # 26 x 37 mm
    B4 = "B4"  # 250 x 353 mm
    B5 = "B5"  # 176 x 250 mm
    letter = "letter"  # 8.5 x 11 in
    legal = "legal"  # 8.5 x 14 in
    ledger = "ledger"  # 11 x 17 in


class PageOrientation(StrEnum):
    portrait = "portrait"
    landscape = "landscape"
