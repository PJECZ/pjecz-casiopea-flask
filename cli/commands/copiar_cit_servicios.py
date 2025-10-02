"""
Copiar tabla cit_servicios de la base de datos ANTERIOR a la NUEVA

AVISO: Solo se copian los registros que NO EXISTEN en la base de datos NUEVA
Lo que significa que NO SE ACTUALIZAN los que hayan sido modificados en la base de datos ANTERIOR

- copiar_cit_servicios: Copiar tabla cit_servicios de la base de datos ANTERIOR a la NUEVA
"""

import uuid

import click


def copiar_cit_servicios(conn_old, cursor_old, conn_new, cursor_new):
    """Copiar tabla cit_servicios de la base de datos ANTERIOR a la NUEVA"""
    # Leer registros de la tabla cit_servicios en la base de datos ANTERIOR
    try:
        cursor_old.execute(
            """
            SELECT
                cit_categorias.clave AS cit_categoria_clave,
                cit_servicios.clave,
                cit_servicios.descripcion,
                cit_servicios.duracion,
                cit_servicios.documentos_limite,
                cit_servicios.desde,
                cit_servicios.hasta,
                cit_servicios.dias_habilitados,
                cit_servicios.estatus,
                cit_servicios.creado,
                cit_servicios.modificado
            FROM cit_servicios
                JOIN cit_categorias ON cit_servicios.cit_categoria_id = cit_categorias.id
        """
        )
        rows = cursor_old.fetchall()
    except Exception as error:
        raise Exception(f"Error al leer registros de la BD ANTERIOR: {error}")
    # Continuar solo si se leyeron registros
    if not rows:
        raise Exception("No hay registros en la tabla cit_servicios de la base de datos ANTERIOR.")
    # Insertar datos en la tabla oficinas en la base de datos NUEVA
    contador = 0
    click.echo(click.style("Copiando registros en oficinas: ", fg="white"), nl=False)
    insert_query = """
        INSERT INTO cit_servicios (id,
            cit_categoria_id,
            clave, descripcion, duracion, documentos_limite,
            desde, hasta, dias_habilitados,
            estatus, creado, modificado, es_activo)
        VALUES (%s,
            (SELECT id FROM cit_categorias WHERE clave = %s),
            %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s, true)
    """
    try:
        for row in rows:
            # Consultar si el registro ya existe
            cursor_new.execute("SELECT id FROM cit_servicios WHERE clave = %s", (row[1],))
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
        click.echo(click.style(f"  {contador} cit_servicios copiados.", fg="green"))
