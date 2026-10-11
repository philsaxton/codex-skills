"""The receipt application's local tax dependency; rates use basis points."""

TAX_BASIS_POINTS = 825


def tax_cents(subtotal_cents, rounding):
    numerator = subtotal_cents * TAX_BASIS_POINTS
    if rounding == "half_up":
        return (numerator + 5000) // 10000
    if rounding == "down":
        return numerator // 10000
    raise ValueError("RECEIPT_ROUNDING must be half_up or down")
