"""
Copiar tabla pag_pagos de la base de datos ANTERIOR a la NUEVA

AVISO: Solo se copian los registros que NO EXISTEN en la base de datos NUEVA
Lo que significa que NO SE ACTUALIZAN los que hayan sido modificados en la base de datos ANTERIOR

- copiar_pag_pagos: Copiar tabla pag_pagos de la base de datos ANTERIOR a la NUEVA
"""

import uuid

import click


def copiar_pag_pagos(conn_old, cursor_old, conn_new, cursor_new):
    """Copiar tabla pag_pagos de la base de datos ANTERIOR a la NUEVA"""
    click.echo(click.style("Copiando tabla pag_pagos: ", fg="white"), nl=False)
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
                        pag_pagos.id as id_original,
                        autoridades.clave AS autoridad_clave,
                        distritos.clave AS distrito_clave,
                        cit_clientes.email,
                        pag_tramites_servicios.clave AS pag_tramite_servicio_clave,
                        pag_pagos.caducidad,
                        pag_pagos.cantidad,
                        pag_pagos.descripcion,
                        pag_pagos.estado,
                        pag_pagos.email,
                        pag_pagos.folio,
                        pag_pagos.resultado_tiempo,
                        pag_pagos.resultado_xml,
                        pag_pagos.total,
                        pag_pagos.ya_se_envio_comprobante,
                        pag_pagos.estatus,
                        pag_pagos.creado,
                        pag_pagos.modificado
                    FROM
                        pag_pagos
                        JOIN autoridades ON pag_pagos.autoridad_id = autoridades.id
                        JOIN distritos ON pag_pagos.distrito_id = distritos.id
                        JOIN cit_clientes ON pag_pagos.cit_cliente_id = cit_clientes.id
                        JOIN pag_tramites_servicios ON pag_pagos.pag_tramite_servicio_id = pag_tramites_servicios.id
                    ORDER BY pag_pagos.id ASC
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
            INSERT INTO pag_pagos (id, id_original,
                autoridad_id,
                distrito_id,
                cit_cliente_id,
                pag_tramite_servicio_id,
                caducidad, cantidad, descripcion, estado, email,
                folio, resultado_tiempo, resultado_xml, total, ya_se_envio_comprobante,
                estatus, creado, modificado)
            VALUES (%s, %s,
                (SELECT id FROM autoridades WHERE clave = %s),
                (SELECT id FROM distritos WHERE clave = %s),
                (SELECT id FROM cit_clientes WHERE email = %s),
                (SELECT id FROM pag_tramites_servicios WHERE clave = %s),
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s)
        """
        try:
            for row in rows:
                # Consultar si el registro ya existe
                cursor_new.execute("SELECT id FROM pag_pagos WHERE id_original = %s", (row[0],))
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
        click.echo(click.style(f"  {contador} pag_pagos copiados.", fg="green"))
