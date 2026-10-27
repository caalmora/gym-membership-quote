"""Pruebas unitarias de la calculadora de membresías."""

from decimal import Decimal

import pytest

from gym_quote import calculate_quote, main


@pytest.mark.parametrize(
    ("plan", "extras", "members", "expected"),
    [
        ("BASIC", [], 1, 30),
        ("STANDARD", [], 1, 45),
        ("PREMIUM", [], 1, 70),
        ("STANDARD", ["PERSONAL_TRAINING"], 1, 70),
        ("BASIC", ["GROUP_CLASSES"], 2, 81),
        ("BASIC", ["GROUP_CLASSES"], 3, 122),
        ("STANDARD", ["GROUP_CLASSES", "PERSONAL_TRAINING"], 4, 286),
        ("PREMIUM", ["GROUP_CLASSES", "SPA"], 2, 215),
        ("PREMIUM", ["SPA", "SPECIALIZED_PROGRAM"], 3, 412),
        (
            "PREMIUM",
            ["SPA", "SPECIALIZED_PROGRAM", "PERSONAL_TRAINING"],
            4,
            626,
        ),
    ],
)
def test_acceptance_examples(plan, extras, members, expected):
    """Comprueba los ejemplos de aceptación del proyecto."""
    quote = calculate_quote(plan, extras, members)
    assert quote.valid is True
    assert quote.total == expected


def test_extra_prices_are_included_in_subtotal():
    """Comprueba que el subtotal incluya los precios de los extras."""
    quote = calculate_quote(
        "STANDARD", ["GROUP_CLASSES", "PERSONAL_TRAINING"], 1
    )
    assert quote.subtotal == Decimal("85")


def test_member_discount_applies_to_two_or_more_members():
    """Comprueba el descuento por cantidad de miembros."""
    quote = calculate_quote("BASIC", [], 2)
    assert quote.member_discount == Decimal("6.00")
    assert quote.total == 54


def test_threshold_discount_of_20_applies_after_member_discount():
    """Comprueba el descuento por umbral después del descuento por miembros."""
    quote = calculate_quote("BASIC", ["GROUP_CLASSES"], 2)
    assert quote.threshold_discount == Decimal("0")

    quote = calculate_quote(
        "STANDARD", ["GROUP_CLASSES", "PERSONAL_TRAINING"], 4
    )
    assert quote.threshold_discount == Decimal("20")


def test_threshold_discount_of_50_applies_above_400():
    """Comprueba el descuento de 50 para importes superiores a 400."""
    quote = calculate_quote("PREMIUM", [], 7)
    assert quote.threshold_discount == Decimal("50")


def test_only_one_threshold_discount_is_applied():
    """Comprueba que no se acumulen los descuentos por umbral."""
    quote = calculate_quote("PREMIUM", [], 7)
    assert quote.threshold_discount == Decimal("50")


def test_premium_extra_adds_15_percent_after_discounts():
    """Comprueba el recargo del 15 por ciento por un extra premium."""
    quote = calculate_quote("PREMIUM", ["SPA"], 1)
    assert quote.surcharge == Decimal("15.00")
    assert quote.total == 115


@pytest.mark.parametrize(
    ("plan", "extras", "members"),
    [
        ("GOLD", [], 1),
        ("BASIC", ["SPA"], 1),
        ("STANDARD", ["SPECIALIZED_PROGRAM"], 1),
        ("BASIC", ["UNKNOWN_EXTRA"], 1),
        ("BASIC", [], 0),
        ("BASIC", [], -1),
        ("BASIC", ["GROUP_CLASSES", "GROUP_CLASSES"], 1),
    ],
)
def test_invalid_inputs_return_minus_one(plan, extras, members):
    """Comprueba que los datos inválidos produzcan -1."""
    quote = calculate_quote(plan, extras, members)
    assert quote.valid is False
    assert quote.total == -1


def test_rounding_uses_half_up_only_at_the_end():
    """Comprueba el redondeo final del total."""
    quote = calculate_quote("BASIC", ["GROUP_CLASSES"], 3)
    assert quote.total == 122


def test_calculation_function_does_not_perform_console_input(monkeypatch):
    """Comprueba que el cálculo no solicite entradas por consola."""

    def fail_if_input_is_called(*args, **kwargs):
        raise AssertionError("calculate_quote must not request console input")

    monkeypatch.setattr("builtins.input", fail_if_input_is_called)
    quote = calculate_quote("BASIC", [], 1)
    assert quote.total == 30


def test_console_cancellation_displays_minus_one(monkeypatch, capsys):
    """Comprueba que cancelar la cotización muestre -1."""
    answers = iter(["BASIC", "ninguno", "1", "n"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))

    main()

    output = capsys.readouterr().out
    assert "Cotización cancelada" in output
    assert "Total: -1" in output



# Verificación de integración continua mediante GitHub Actions.
