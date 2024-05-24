from strenum import StrEnum

__all__ = (
    "PageSize",
    "PageOrientation",
)


class PageSize(StrEnum):
    A0 = "A0"  # 841 × 1189 mm
    A1 = "A1"  # 594 × 841 mm
    A2 = "A2"  # 420 × 594 mm
    A3 = "A3"  # 297 × 420 mm
    A4 = "A4"  # 210 × 297 mm
    A5 = "A5"  # 148 × 210 mm
    A6 = "A6"  # 105 × 148 mm
    A7 = "A7"  # 74 × 105 mm
    A10 = "A10"  # 26 × 37 mm
    B4 = "B4"  # 250 × 353 mm
    B5 = "B5"  # 176 × 250 mm
    letter = "letter"  # 8.5 × 11 in
    legal = "legal"  # 8.5 × 14 in
    ledger = "ledger"  # 11 × 17 in


class PageOrientation(StrEnum):
    portrait = "portrait"
    landscape = "landscape"
