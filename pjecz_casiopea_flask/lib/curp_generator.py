"""
Generador de CURP
"""

from datetime import date

import random
import string

CURP_REGEXP = r"^[A-Z]{4}\d{6}[A-Z]{6}[A-Z0-9]{2}$"


def generar_nacimiento_falso() -> date:
    """Generar una fecha de nacimiento falsa"""
    anio = date.today().year - random.randint(18, 70)
    mes = random.randint(1, 12)
    dia = random.randint(1, 28)
    return date(anio, mes, dia)


def generar_curp_falso(nombres: str, primer_apellido: str, segundo_apellido: str, nacimiento: date) -> str:
    """Generar un CURP falso"""
    listado = []
    listado.append(primer_apellido[0:2])
    if segundo_apellido == "":
        listado.append("X")
    else:
        listado.append(segundo_apellido[0])
    listado.append(nombres[0])
    listado.append(str(nacimiento.year)[2:4])
    listado.append(str(nacimiento.month).zfill(2))
    listado.append(str(nacimiento.day).zfill(2))
    mayusculas = string.ascii_uppercase
    digitos = string.digits
    listado.append("".join(random.sample(mayusculas, 6)))
    listado.append("".join(random.sample(mayusculas + digitos, 2)))
    return "".join(listado)
