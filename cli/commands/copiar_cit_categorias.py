"""
Copiar tabla cit_categorias de la base de datos ANTERIOR a la NUEVA

AVISO: Solo se copian los registros que NO EXISTEN en la base de datos NUEVA
Lo que significa que NO SE ACTUALIZAN los que hayan sido modificados en la base de datos ANTERIOR

- copiar_cit_categorias: Copiar tabla cit_categorias de la base de datos ANTERIOR a la NUEVA
"""

import uuid

import click


def copiar_cit_categorias(conn_old, cursor_old, conn_new, cursor_new):
    """Copiar tabla cit_categorias de la base de datos ANTERIOR a la NUEVA"""
    click.echo(click.style("Copiando tabla autoridades: ", fg="white"), nl=False)
    # Leer registros de la tabla cit_categorias en la base de datos ANTERIOR
    try:
        cursor_old.execute(
            """
            SELECT
                clave, nombre,
                estatus, creado, modificado
            FROM
                cit_categorias
            ORDER BY
                clave ASC
        """
        )
        rows = cursor_old.fetchall()
    except Exception as error:
        raise Exception(f"Error al leer registros de la BD ANTERIOR: {error}")
    # Continuar solo si se leyeron registros
    if not rows:
        raise Exception("No hay registros en la base de datos ANTERIOR.")
    # Insertar datos en la tabla cit_categorias en la base de datos NUEVA
    contador = 0
    insert_query = """
        INSERT INTO cit_categorias (id,
            clave, nombre,
            estatus, creado, modificado, es_activo)
        VALUES (%s,
            %s, %s,
            %s, %s, %s, true)
    """
    try:
        for row in rows:
            # Consultar si el registro ya existe
            cursor_new.execute("SELECT id FROM cit_categorias WHERE clave = %s", (row[0],))
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
        click.echo(click.style(f"  {contador} cit_categorias copiados.", fg="green"))
