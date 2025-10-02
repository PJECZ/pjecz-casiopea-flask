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
    # Leer registros de la tabla cit_oficinas_servicios en la base de datos ANTERIOR
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
            FROM cit_oficinas_servicios
                JOIN cit_servicios ON cit_oficinas_servicios.cit_servicio_id = cit_servicios.id
                JOIN oficinas ON cit_oficinas_servicios.oficina_id = oficinas.id
            ORDER BY cit_oficinas_servicios.id ASC
        """
        )
        rows = cursor_old.fetchall()
    except Exception as error:
        raise Exception(f"Error al leer registros de la BD ANTERIOR: {error}")
    # Continuar solo si se leyeron registros
    if not rows:
        raise Exception("No hay registros en la tabla cit_oficinas_servicios de la base de datos ANTERIOR.")
    # Insertar datos en la tabla oficinas en la base de datos NUEVA
    contador = 0
    click.echo(click.style("Copiando registros en cit_oficinas_servicios: ", fg="white"), nl=False)
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
        click.echo(click.style(f"  {contador} cit_oficinas_servicios copiados.", fg="green"))
