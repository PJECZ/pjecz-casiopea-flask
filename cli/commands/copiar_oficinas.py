"""
Copiar tabla oficinas de la base de datos ANTERIOR a la NUEVA

- copiar_oficinas: Copiar tabla oficinas de la base de datos ANTERIOR a la NUEVA
"""

import uuid

import click


def copiar_oficinas(conn_old, cursor_old, conn_new, cursor_new):
    """Copiar tabla oficinas de la base de datos ANTERIOR a la NUEVA"""
    # Leer registros de la tabla oficinas en la base de datos ANTERIOR
    try:
        cursor_old.execute(
            """
            SELECT
                domicilios.clave AS domicilio_clave,
                oficinas.clave, oficinas.descripcion, oficinas.descripcion_corta,
                oficinas.es_jurisdiccional, oficinas.puede_agendar_citas,
                oficinas.apertura, oficinas.cierre, oficinas.limite_personas, oficinas.puede_enviar_qr,
                oficinas.estatus, oficinas.creado, oficinas.modificado
            FROM oficinas
                JOIN domicilios ON oficinas.domicilio_id = domicilios.id
            ORDER BY oficinas.clave ASC
        """
        )
        rows = cursor_old.fetchall()
    except Exception as error:
        raise Exception(f"Error al leer registros de la BD ANTERIOR: {error}")
    # Continuar solo si se leyeron registros
    if not rows:
        raise Exception("No hay registros en la tabla oficinas de la base de datos ANTERIOR.")
    # Insertar datos en la tabla oficinas en la base de datos NUEVA
    contador = 0
    click.echo(click.style("Copiando registros en oficinas: ", fg="white"), nl=False)
    insert_query = """
        INSERT INTO oficinas (id,
            domicilio_id,
            clave, descripcion, descripcion_corta,
            es_jurisdiccional, puede_agendar_citas,
            apertura, cierre, limite_personas, puede_enviar_qr,
            estatus, creado, modificado, es_activo)
        VALUES (%s,
            (SELECT id FROM domicilios WHERE clave = %s),
            %s, %s, %s,
            %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, true)
    """
    try:
        for row in rows:
            # Consultar si el registro ya existe
            cursor_new.execute("SELECT id FROM oficinas WHERE clave = %s", (row[0],))
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
        click.echo(click.style(f"  {contador} oficinas copiados.", fg="green"))
