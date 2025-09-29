"""
Copiar tabla pag_tramites_servicios de la base de datos ANTERIOR a la NUEVA

- copiar_pag_tramites_servicios: Copiar tabla pag_tramites_servicios de la base de datos ANTERIOR a la NUEVA
"""

import sys
import uuid

import click


def copiar_pag_tramites_servicios(conn_old, cursor_old, conn_new, cursor_new):
    """Copiar tabla pag_tramites_servicios de la base de datos ANTERIOR a la NUEVA"""
    # Leer registros de la tabla pag_tramites_servicios en la base de datos ANTERIOR
    try:
        cursor_old.execute("SELECT clave, descripcion, costo, url FROM pag_tramites_servicios")
        rows = cursor_old.fetchall()
    except Exception as error:
        click.echo(click.style(f"Error al leer registros de la BD ANTERIOR: {error}", fg="red"))
        sys.exit(1)
    # Continuar solo si se leyeron registros
    if not rows:
        print("No hay registros en la tabla pag_tramites_servicios de la base de datos ANTERIOR.")
        sys.exit(0)
    # Insertar datos en la tabla pag_tramites_servicios en la base de datos NUEVA
    click.echo("Copiando registros en pag_tramites_servicios: ", nl=False)
    insert_query = """
        INSERT INTO pag_tramites_servicios (id, clave, descripcion, costo, url)
        VALUES (%s, %s, %s, %s, %s)
    """
    try:
        for row in rows:
            new_id = str(uuid.uuid4())
            cursor_new.execute(insert_query, (new_id, *row))
            click.echo(click.style(".", fg="green"), nl=False)
    except Exception as error:
        click.echo(click.style(f"Error al insertar registros en la BD NUEVA: {error}", fg="red"))
        sys.exit(1)
    # Confirmar los cambios y cerrar las conexiones
    conn_new.commit()
    cursor_old.close()
    conn_old.close()
    cursor_new.close()
    conn_new.close()
    click.echo()
    # Mensaje final
    click.echo(click.style(f"{len(rows)} registros copiados.", fg="green"))
