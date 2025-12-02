# core/validators.py
from django.core.exceptions import ValidationError

def clean_rut(rut: str) -> str:
    """
    Normaliza el RUT:
    - Quita puntos y espacios
    - Pasa todo a mayúsculas
    - Asegura formato base: 12345678-K
    """
    if not rut:
        return ''

    rut = rut.replace('.', '').replace(' ', '').upper()

    # Separar cuerpo y dígito verificador
    if '-' in rut:
        body, dv = rut.split('-', 1)
    else:
        body, dv = rut[:-1], rut[-1]

    return f'{body}-{dv}'


def validate_rut(value: str):
    """
    Valida RUT chileno (módulo 11).
    Lanza ValidationError si el RUT es inválido.
    """
    if not value:
        return

    rut = clean_rut(value)

    # Separar
    try:
        body, dv = rut.split('-', 1)
    except ValueError:
        raise ValidationError('Formato de RUT inválido. Use 12345678-9')

    if not body.isdigit():
        raise ValidationError('El RUT debe contener solo números antes del guion.')

    # Cálculo dígito verificador
    reversed_digits = map(int, reversed(body))
    factors = [2, 3, 4, 5, 6, 7]
    s = 0
    factor_index = 0

    for d in reversed_digits:
        s += d * factors[factor_index]
        factor_index = (factor_index + 1) % len(factors)

    remainder = 11 - (s % 11)
    if remainder == 11:
        dv_expected = '0'
    elif remainder == 10:
        dv_expected = 'K'
    else:
        dv_expected = str(remainder)

    if dv.upper() != dv_expected:
        raise ValidationError('RUT inválido.')

    # Si quisieras normalizar siempre el formato, lo harías en el modelo o form, no aquí.
