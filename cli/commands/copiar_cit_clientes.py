"""
Copiar tabla cit_clientes de la base de datos ANTERIOR a la NUEVA

- copiar_cit_clientes: Copiar tabla cit_clientes de la base de datos ANTERIOR a la NUEVA
"""

import uuid

import click


def copiar_cit_clientes(conn_old, cursor_old, conn_new, cursor_new):
    """Copiar tabla cit_clientes de la base de datos ANTERIOR a la NUEVA"""
    # Leer registros de la tabla cit_clientes en la base de datos ANTERIOR
    try:
        cursor_old.execute(
            """
                SELECT nombres, apellido_primero, apellido_segundo, curp, telefono, email,
                contrasena_md5, contrasena_sha256, renovacion, limite_citas_pendientes,
                estatus, creado, modificado
                FROM cit_clientes
            """
        )
        rows = cursor_old.fetchall()
    except Exception as error:
        raise Exception(f"Error al leer registros de la BD ANTERIOR: {error}")
    # Continuar solo si se leyeron registros
    if not rows:
        raise Exception("No hay registros en la tabla cit_clientes de la base de datos ANTERIOR.")
    # Insertar datos en la tabla cit_clientes en la base de datos NUEVA
    contador = 0
    click.echo(click.style("Copiando registros en cit_clientes: ", fg="white"), nl=False)
    insert_query = """
        INSERT INTO cit_clientes
            (id, nombres, apellido_primero, apellido_segundo, curp, telefono, email,
            contrasena_md5, contrasena_sha256, renovacion, limite_citas_pendientes,
            estatus, creado, modificado,
            autoriza_mensajes, enviar_boletin,
            es_adulto_mayor, es_mujer, es_identidad, es_discapacidad, es_personal_interno)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            false, false,
            false, false, false, false, false)
    """
    try:
        for row in rows:
            # Consultar si el registro ya existe
            cursor_new.execute("SELECT id FROM cit_clientes WHERE email = %s", (row[5],))
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
        click.echo(click.style(f"  {contador} cit_clientes copiados.", fg="green"))
