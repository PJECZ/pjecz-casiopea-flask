"""
Copiar tabla cit_clientes_recuperaciones de la base de datos ANTERIOR a la NUEVA

AVISO: Solo se copian los registros que NO EXISTEN en la base de datos NUEVA
Lo que significa que NO SE ACTUALIZAN los que hayan sido modificados en la base de datos ANTERIOR

- copiar_cit_clientes_recuperaciones: Copiar tabla cit_clientes_recuperaciones de la base de datos ANTERIOR a la NUEVA
"""

import uuid

import click


def copiar_cit_clientes_recuperaciones(conn_old, cursor_old, conn_new, cursor_new):
    """Copiar tabla cit_clientes_recuperaciones de la base de datos ANTERIOR a la NUEVA"""
    click.echo(click.style("Copiando tabla cit_clientes_recuperaciones: ", fg="white"), nl=False)
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
                        cit_clientes_recuperaciones.id as id_original,
                        cit_clientes.email,
                        cit_clientes_recuperaciones.expiracion,
                        cit_clientes_recuperaciones.cadena_validar,
                        cit_clientes_recuperaciones.mensajes_cantidad,
                        cit_clientes_recuperaciones.ya_recuperado,
                        cit_clientes_recuperaciones.estatus,
                        cit_clientes_recuperaciones.creado,
                        cit_clientes_recuperaciones.modificado
                    FROM
                        cit_clientes_recuperaciones
                        JOIN cit_clientes ON cit_clientes_recuperaciones.cit_cliente_id = cit_clientes.id
                    ORDER BY cit_clientes_recuperaciones.id ASC
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
            INSERT INTO cit_clientes_recuperaciones (id, id_original,
                cit_cliente_id,
                expiracion, cadena_validar, mensajes_cantidad, ya_recuperado,
                estatus, creado, modificado)
            VALUES (%s, %s,
                (SELECT id FROM cit_clientes WHERE email = %s),
                %s, %s, %s, %s,
                %s, %s, %s)
        """
        try:
            for row in rows:
                # Consultar si el registro ya existe
                cursor_new.execute("SELECT id FROM cit_clientes_recuperaciones WHERE id_original = %s", (row[0],))
                if cursor_new.fetchone():
                    click.echo(click.style("-", fg="blue"), nl=False)
                    continue  # Ya existe, se omite
                # Insertar
                new_id = str(uuid.uuid4())
                cursor_new.execute(insert_query, (new_id, *row))
                contador += 1
                click.echo(click.style("+", fg="green"), nl=False)
        except Exception as error:
            raise Exception(f"Error al insertar registros en la BD NUEVA: {error}")
        # Confirmar los cambios
        conn_new.commit()
        # Incrementar offset para la siguiente página
        offset += limit
    # Mensaje final
    click.echo()
    if contador > 0:
        click.echo(click.style(f"  {contador} cit_clientes_recuperaciones copiados.", fg="green"))
