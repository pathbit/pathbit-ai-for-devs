FREE_SHIPPING_MINIMUM_CENTS = 10_000
STANDARD_SHIPPING_CENTS = 750


def shipping_cents(subtotal_cents: int) -> int:
    if subtotal_cents >= FREE_SHIPPING_MINIMUM_CENTS:
        return 0
    return STANDARD_SHIPPING_CENTS
