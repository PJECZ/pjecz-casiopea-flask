"""
Copiar tabla cit_oficinas_servicios de la base de datos ANTERIOR a la NUEVA

AVISO: Solo se copian los registros que NO EXISTEN en la base de datos NUEVA
Lo que significa que NO SE ACTUALIZAN los que hayan sido modificados en la base de datos ANTERIOR

- copiar_cit_oficinas_servicios: Copiar tabla cit_oficinas_servicios de la base de datos ANTERIOR a la NUEVA
"""

import uuid

import click


def copiar_cit_oficinas_servicios(conn_old, cursor_old, conn_new, cursor_new):
    """Copiar tabla cit_oficinas_servicios de la base de datos ANTERIOR a la NUEVA"""
    click.echo(click.style("Copiando tabla cit_oficinas_servicios: ", fg="white"), nl=False)
    # Leer registros en la base de datos ANTERIOR
    try:
        cursor_old.execute(
            """
                SELECT
                    cit_servicios.clave AS cit_servicio_clave,
                    oficinas.clave AS oficina_clave,
                    cit_oficinas_servicios.descripcion,
                    cit_oficinas_servicios.estatus,
                    cit_oficinas_servicios.creado,
                    cit_oficinas_servicios.modificado
                FROM
                    cit_oficinas_servicios
                    JOIN cit_servicios ON cit_oficinas_servicios.cit_servicio_id = cit_servicios.id
                    JOIN oficinas ON cit_oficinas_servicios.oficina_id = oficinas.id
                ORDER BY cit_oficinas_servicios.id ASC
            """,
        )
        rows = cursor_old.fetchall()
    except Exception as error:
        raise Exception(f"Error al leer registros de la BD ANTERIOR: {error}")
    # Continuar solo si se leyeron registros
    if not rows:
        raise Exception("No hay registros en la base de datos ANTERIOR.")
    # Insertar registros en la base de datos NUEVA
    contador = 0
    insert_query = """
        INSERT INTO cit_oficinas_servicios (id,
            cit_servicio_id,
            oficina_id,
            descripcion,
            estatus, creado, modificado, es_activo)
        VALUES (%s,
            (SELECT id FROM cit_servicios WHERE clave = %s),
            (SELECT id FROM oficinas WHERE clave = %s),
            %s,
            %s, %s, %s, true)
    """
    try:
        for row in rows:
            cit_servicio_clave = row[0]  # La clave del servicio es la primer columna
            oficina_clave = row[1]  # La clave de la oficina es la segunda columna
            # Si ya existe un registro con cit_servicio_id y oficina_id, omitir
            cursor_new.execute(
                """
                SELECT id FROM cit_oficinas_servicios
                WHERE cit_servicio_id = (SELECT id FROM cit_servicios WHERE clave = %s)
                AND oficina_id = (SELECT id FROM oficinas WHERE clave = %s)
                """,
                (cit_servicio_clave, oficina_clave),
            )
            if cursor_new.fetchone():
                click.echo(click.style("-", fg="blue"), nl=False)
                continue  # Ya existe, se omite
            # Insertar
            new_id = str(uuid.uuid4())
            cursor_new.execute(insert_query, (new_id, *row))
            contador += 1
            click.echo(click.style("+", fg="green"), nl=False)
    except Exception as error:
        raise Exception(f"Error al insertar {cit_servicio_clave} en {oficina_clave}: {error}")
    # Confirmar los cambios
    conn_new.commit()
    # Mensaje final
    click.echo()
    if contador > 0:
        click.echo(click.style(f"  {contador} cit_oficinas_servicios copiados.", fg="green"))
