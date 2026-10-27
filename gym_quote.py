"""Calculadora de cotizaciones para membres?as de gimnasio."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable


PLAN_PRICES = {
    "BASIC": Decimal("30"),
    "STANDARD": Decimal("45"),
    "PREMIUM": Decimal("70"),
}

EXTRA_PRICES = {
    "GROUP_CLASSES": Decimal("15"),
    "PERSONAL_TRAINING": Decimal("25"),
    "SPA": Decimal("30"),
    "SPECIALIZED_PROGRAM": Decimal("40"),
}

PREMIUM_EXTRAS = {"SPA", "SPECIALIZED_PROGRAM"}


@dataclass(frozen=True)
class QuoteResult:
    """Resultado detallado de una cotizaci?n."""
    subtotal: Decimal
    member_discount: Decimal
    threshold_discount: Decimal
    surcharge: Decimal
    total: int
    valid: bool


def invalid_quote() -> QuoteResult:
    """Representa una cotización inválida o cancelada."""
    zero = Decimal("0")
    return QuoteResult(zero, zero, zero, zero, -1, False)


# pylint: disable=too-many-return-statements
def calculate_quote(
    plan: str,
    extras: Iterable[str],
    members: int,
) -> QuoteResult:
    """Calcula una cotización sin leer ni imprimir datos en consola."""
    if not isinstance(plan, str):
        return invalid_quote()

    plan = plan.strip().upper()
    if plan not in PLAN_PRICES:
        return invalid_quote()

    if isinstance(members, bool) or not isinstance(members, int) or members < 1:
        return invalid_quote()

    try:
        normalized_extras = [extra.strip().upper() for extra in extras]
    except (TypeError, AttributeError):
        return invalid_quote()

    if any(not extra for extra in normalized_extras):
        return invalid_quote()

    if len(normalized_extras) != len(set(normalized_extras)):
        return invalid_quote()

    if any(extra not in EXTRA_PRICES for extra in normalized_extras):
        return invalid_quote()

    if plan != "PREMIUM" and PREMIUM_EXTRAS.intersection(normalized_extras):
        return invalid_quote()

    price_per_member = PLAN_PRICES[plan] + sum(
        (EXTRA_PRICES[extra] for extra in normalized_extras),
        Decimal("0"),
    )
    subtotal = price_per_member * members

    # R4: descuento del 10 % si hay dos o más miembros.
    member_discount = (
        subtotal * Decimal("0.10") if members >= 2 else Decimal("0")
    )
    amount_after_member_discount = subtotal - member_discount

    # R5: aplicar solo uno de los descuentos por umbral.
    if amount_after_member_discount > Decimal("400"):
        threshold_discount = Decimal("50")
    elif amount_after_member_discount > Decimal("200"):
        threshold_discount = Decimal("20")
    else:
        threshold_discount = Decimal("0")

    amount_after_discounts = (
        amount_after_member_discount - threshold_discount
    )

    # R6: recargo del 15 % después de aplicar los descuentos.
    has_premium_extra = bool(
        PREMIUM_EXTRAS.intersection(normalized_extras)
    )
    surcharge = (
        amount_after_discounts * Decimal("0.15")
        if has_premium_extra
        else Decimal("0")
    )

    unrounded_total = amount_after_discounts + surcharge

    # R7: redondear una sola vez, al final, usando half-up.
    total = int(
        unrounded_total.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )

    return QuoteResult(
        subtotal=subtotal,
        member_discount=member_discount,
        threshold_discount=threshold_discount,
        surcharge=surcharge,
        total=total,
        valid=True,
    )


def main() -> None:
    """Interfaz de consola para solicitar y confirmar una cotización."""
    print("=== Cotizador de membresías de gimnasio ===")
    print("Planes disponibles: BASIC, STANDARD, PREMIUM")
    print("Extras: GROUP_CLASSES, PERSONAL_TRAINING, SPA, SPECIALIZED_PROGRAM")
    print("Escribe 'ninguno' si no deseas extras.")

    try:
        plan = input("Plan: ").strip()
        extras_text = input("Extras separados por comas: ").strip()
        members_text = input("Número de miembros: ").strip()

        if not members_text.isdigit():
            print("Cotización inválida. Total: -1")
            return

        members = int(members_text)
        extras = (
            []
            if extras_text.strip().lower() in {"", "ninguno"}
            else extras_text.split(",")
        )

        quote = calculate_quote(plan, extras, members)

        if not quote.valid:
            print("Cotización inválida. Verifica el plan, los extras y los miembros.")
            print("Total: -1")
            return

        print("\n--- Resumen de la cotización ---")
        print(f"Subtotal: {quote.subtotal:.2f}")
        print(f"Descuento por miembros: {quote.member_discount:.2f}")
        print(f"Descuento por umbral: {quote.threshold_discount:.2f}")
        print(f"Recargo por extras premium: {quote.surcharge:.2f}")
        print(f"Total: {quote.total}")

        confirmation = input("¿Confirmas la cotización? (s/n): ").strip().lower()
        if confirmation not in {"s", "si", "sí", "y", "yes"}:
            print("Cotización cancelada. Total: -1")

    except (EOFError, KeyboardInterrupt):
        print("\nCotización cancelada. Total: -1")


if __name__ == "__main__":
    main()
