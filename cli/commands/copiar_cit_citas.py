"""
Copiar tabla cit_citas de la base de datos ANTERIOR a la NUEVA

AVISO: Solo se copian los registros que NO EXISTEN en la base de datos NUEVA
Lo que significa que NO SE ACTUALIZAN los que hayan sido modificados en la base de datos ANTERIOR

- copiar_cit_citas: Copiar tabla cit_citas de la base de datos ANTERIOR a la NUEVA
"""

import uuid

import click


def copiar_cit_citas(conn_old, cursor_old, conn_new, cursor_new):
    """Copiar tabla cit_citas de la base de datos ANTERIOR a la NUEVA"""
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
                        cit_citas.id as id_original,
                        cit_clientes.email,
                        cit_servicios.clave AS cit_servicio_clave,
                        oficinas.clave AS oficina_clave,
                        cit_citas.inicio,
                        cit_citas.termino,
                        cit_citas.notas,
                        cit_citas.estado,
                        cit_citas.cancelar_antes,
                        cit_citas.asistencia,
                        cit_citas.codigo_asistencia,
                        cit_citas.estatus,
                        cit_citas.creado,
                        cit_citas.modificado
                    FROM
                        cit_citas
                        JOIN cit_clientes ON cit_citas.cit_cliente_id = cit_clientes.id
                        JOIN cit_servicios ON cit_citas.cit_servicio_id = cit_servicios.id
                        JOIN oficinas ON cit_citas.oficina_id = oficinas.id
                    ORDER BY cit_citas.id ASC
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
        if offset > 0:
            click.echo()
        click.echo(click.style("Copiando registros en cit_citas: ", fg="white"), nl=False)
        insert_query = """
            INSERT INTO cit_citas (id, id_original,
                cit_cliente_id, cit_servicio_id, oficina_id,
                inicio, termino, notas, estado, cancelar_antes,
                asistencia, codigo_asistencia, codigo_acceso_id, codigo_acceso_imagen,
                estatus, creado, modificado)
            VALUES (%s, %s,
                (SELECT id FROM cit_clientes WHERE email = %s),
                (SELECT id FROM cit_servicios WHERE clave = %s),
                (SELECT id FROM oficinas WHERE clave = %s),
                %s, %s, %s, %s, %s,
                %s, %s, NULL, NULL,
                %s, %s, %s)
        """
        try:
            for row in rows:
                # Consultar si el registro ya existe
                cursor_new.execute("SELECT id FROM cit_citas WHERE id_original = %s", (row[0],))
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
        click.echo(click.style(f"  {contador} cit_citas copiados.", fg="green"))
