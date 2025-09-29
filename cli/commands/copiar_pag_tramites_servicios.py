"""
Copiar tabla pag_tramites_servicios de la base de datos ANTERIOR a la NUEVA

- copiar_pag_tramites_servicios: Copiar tabla pag_tramites_servicios de la base de datos ANTERIOR a la NUEVA
"""

import uuid

import click


def copiar_pag_tramites_servicios(conn_old, cursor_old, conn_new, cursor_new):
    """Copiar tabla pag_tramites_servicios de la base de datos ANTERIOR a la NUEVA"""
    # Leer registros de la tabla pag_tramites_servicios en la base de datos ANTERIOR
    try:
        cursor_old.execute("SELECT clave, descripcion, costo, url FROM pag_tramites_servicios")
        rows = cursor_old.fetchall()
    except Exception as error:
        raise Exception(f"Error al leer registros de la BD ANTERIOR: {error}")
    # Continuar solo si se leyeron registros
    if not rows:
        raise Exception("No hay registros en la tabla pag_tramites_servicios de la base de datos ANTERIOR.")
    # Insertar datos en la tabla pag_tramites_servicios en la base de datos NUEVA
    contador = 0
    click.echo(click.style("Copiando registros en pag_tramites_servicios: ", fg="white"), nl=False)
    insert_query = """
        INSERT INTO pag_tramites_servicios (id, clave, descripcion, costo, url)
        VALUES (%s, %s, %s, %s, %s)
    """
    try:
        for row in rows:
            # Consultar si el registro ya existe
            cursor_new.execute("SELECT id FROM pag_tramites_servicios WHERE clave = %s", (row[0],))
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
    # Mensaje final
    click.echo()
    if contador > 0:
        click.echo(click.style(f"{contador} pag_tramites_servicios copiados.", fg="green"))
