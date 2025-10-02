"""
Copiar tabla autoridades de la base de datos ANTERIOR a la NUEVA

AVISO: Solo se copian los registros que NO EXISTEN en la base de datos NUEVA
Lo que significa que NO SE ACTUALIZAN los que hayan sido modificados en la base de datos ANTERIOR

- copiar_autoridades: Copiar tabla autoridades de la base de datos ANTERIOR a la NUEVA
"""

import uuid

import click


def copiar_autoridades(conn_old, cursor_old, conn_new, cursor_new):
    """Copiar tabla autoridades de la base de datos ANTERIOR a la NUEVA"""
    click.echo(click.style("Copiando tabla autoridades: ", fg="white"), nl=False)
    # Leer registros de la tabla cit_categorias en la base de datos ANTERIOR
    try:
        cursor_old.execute(
            """
                SELECT
                    distritos.clave AS distrito_clave,
                    materias.clave AS materia_clave,
                    autoridades.clave,
                    autoridades.descripcion,
                    autoridades.descripcion_corta,
                    autoridades.es_jurisdiccional,
                    autoridades.estatus,
                    autoridades.creado,
                    autoridades.modificado
                FROM
                    autoridades
                    JOIN distritos ON autoridades.distrito_id = distritos.id
                    JOIN materias ON autoridades.materia_id = materias.id
                ORDER BY
                    autoridades.id ASC
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
        INSERT INTO autoridades (id,
            distrito_id,
            materia_id,
            clave, descripcion, descripcion_corta, es_jurisdiccional,
            estatus, creado, modificado, es_activo)
        VALUES (%s,
            (SELECT id FROM distritos WHERE clave = %s),
            (SELECT id FROM materias WHERE clave = %s),
            %s, %s, %s, %s,
            %s, %s, %s, true)
    """
    try:
        for row in rows:
            # Consultar si el registro ya existe
            cursor_new.execute("SELECT id FROM autoridades WHERE clave = %s", (row[2],))
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
        click.echo(click.style(f"  {contador} autoridades copiados.", fg="green"))
