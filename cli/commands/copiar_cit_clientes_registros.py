"""
Copiar tabla cit_clientes_registros de la base de datos ANTERIOR a la NUEVA

AVISO: Solo se copian los registros que NO EXISTEN en la base de datos NUEVA
Lo que significa que NO SE ACTUALIZAN los que hayan sido modificados en la base de datos ANTERIOR

- copiar_cit_clientes_registros: Copiar tabla cit_clientes_registros de la base de datos ANTERIOR a la NUEVA
"""

import uuid

import click


def copiar_cit_clientes_registros(conn_old, cursor_old, conn_new, cursor_new):
    """Copiar tabla cit_clientes_registros de la base de datos ANTERIOR a la NUEVA"""
    click.echo(click.style("Copiando tabla cit_clientes_registros: ", fg="white"), nl=False)
    # Inicializar limit y offset para paginar la consulta de la base de datos ANTERIOR
    limit = 1000
    offset = 0
    contador = 0
    while True:
        # Leer registros en la base de datos ANTERIOR
        try:
            cursor_old.execute(
                """
                    SELECT
                        id AS id_original,
                        nombres,
                        apellido_primero,
                        apellido_segundo,
                        curp,
                        telefono,
                        email,
                        expiracion,
                        cadena_validar,
                        mensajes_cantidad,
                        ya_registrado,
                        estatus,
                        creado,
                        modificado
                    FROM
                        cit_clientes_registros
                    ORDER BY cit_clientes_registros.id ASC
                    LIMIT %s OFFSET %s
                """,
                (limit, offset),
            )
            rows = cursor_old.fetchall()
        except Exception as error:
            raise Exception(f"Error al leer registros de la BD ANTERIOR: {error}")
        # Si no hay más registros, salir del ciclo
        if not rows:
            break
        # Insertar registros en la base de datos NUEVA
        insert_query = """
            INSERT INTO cit_clientes_registros (id, id_original,
                nombres, apellido_primero, apellido_segundo, curp, telefono, email,
                expiracion, cadena_validar, mensajes_cantidad, ya_registrado,
                estatus, creado, modificado)
            VALUES (%s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s)
        """
        try:
            for row in rows:
                id_original = row[0]  # El id_original es la primer columna
                # Consultar si el registro ya existe
                cursor_new.execute("SELECT id FROM cit_clientes_registros WHERE id_original = %s", (id_original,))
                if cursor_new.fetchone():
                    click.echo(click.style("-", fg="blue"), nl=False)
                    continue  # Ya existe, se omite
                # Insertar
                new_id = str(uuid.uuid4())
                cursor_new.execute(insert_query, (new_id, *row))
                contador += 1
                click.echo(click.style("+", fg="green"), nl=False)
        except Exception as error:
            raise Exception(f"Error al insertar {id_original}: {error}")
        # Confirmar los cambios
        conn_new.commit()
        # Incrementar offset para la siguiente página
        offset += limit
    # Mensaje final
    click.echo()
    if contador > 0:
        click.echo(click.style(f"  {contador} cit_clientes_registros copiados.", fg="green"))
