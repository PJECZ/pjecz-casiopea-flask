"""
Generadores de contraseñas
"""

import random
import re
import string

PASSWORD_REGEXP = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,24}$"


def generar_contrasena(largo=16):
    """Generar contraseña con minúsculas, mayúsculas, dígitos y signos"""
    minusculas = string.ascii_lowercase
    mayusculas = string.ascii_uppercase
    digitos = string.digits
    todos = minusculas + mayusculas + digitos
    contrasena = ""
    while re.match(PASSWORD_REGEXP, contrasena) is None:
        temp = random.sample(todos, largo)
        contrasena = "".join(temp)
    return contrasena
