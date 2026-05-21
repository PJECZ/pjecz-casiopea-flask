"""
CLI Commands Cit Citas
"""

import os
import random
from datetime import date, datetime, time, timedelta
from pathlib import Path

import sendgrid
import typer
from dotenv import load_dotenv
from faker import Faker
from rich.console import Console
from rich.progress import Progress
from sendgrid.helpers.mail import Content, Email, Mail
from sqlalchemy.sql import func
from typer import Typer

from pjecz_casiopea_flask.blueprints.cit_citas.models import CitCita, database
from pjecz_casiopea_flask.blueprints.cit_clientes.models import CitCliente
from pjecz_casiopea_flask.blueprints.cit_dias_inhabiles.models import CitDiaInhabil
from pjecz_casiopea_flask.blueprints.cit_oficinas_servicios.models import CitOficinaServicio
from pjecz_casiopea_flask.blueprints.cit_servicios.models import CitServicio
from pjecz_casiopea_flask.blueprints.oficinas.models import Oficina
from pjecz_casiopea_flask.blueprints.usuarios_oficinas.models import UsuarioOficina
from pjecz_casiopea_flask.main import app

app.app_context().push()

cit_citas = Typer()


@cit_citas.command()
def agregar_falsos(maximo: int = 10, desde: str = "", hasta: str = ""):
    """Agregar citas con datos falsos"""
    console = Console()

    # Si no viene desde, usar el día de hoy
    if not desde:
        desde_dt = datetime.now().date()
    else:
        try:
            desde_dt = datetime.strptime(desde, "%Y-%m-%d").date()
        except ValueError:
            console.print("[yellow]Fecha 'desde' inválida[/yellow]")
            return

    # Si no viene hasta, usar 30 días después del día de hoy
    if not hasta:
        hasta_dt = datetime.now().date() + timedelta(days=30)
    else:
        try:
            hasta_dt = datetime.strptime(hasta, "%Y-%m-%d").date()
        except ValueError:
            console.print("[yellow]Fecha 'hasta' inválida[/yellow]")
            return

    # Consultar cit_clientes
    cit_clientes = CitCliente.query.filter(CitCliente.estatus == "A").order_by(CitCliente.creado.desc()).limit(10).all()

    # Si no hay cit_clientes, salir
    if not cit_clientes:
        console.print("[yellow]No hay clientes para asignar citas[/yellow]")
        return

    # Inicializar el contador
    contador = 0

    # Bucle entre los cit_clientes
    for cit_cliente in cit_clientes:
        # Bucle para agregar citas, de una a LIMITE_CITAS_CANTIDAD
        for _ in range(1, random.randint(1, maximo) + 1):
            # Definir una fecha aleatoria entre desde_dt y hasta_dt
            delta_dias = (hasta_dt - desde_dt).days
            fecha = desde_dt + timedelta(days=random.randint(0, delta_dias))
            # Definir una hora aleatoria entre 9:00 y 12:00
            hora = random.randint(9, 11)
            minuto = random.choice([0, 15, 30, 45])
            fecha_hora = datetime(fecha.year, fecha.month, fecha.day, hora, minuto)
            # Bucle hasta encontrar un servicio y oficina
            while True:
                # Consultar un CitServicio aleatorio
                cit_servicio = CitServicio.query.order_by(func.random()).first()
                if cit_servicio is None:
                    console.print("[yellow]No hay servicios para asignar citas[/yellow]")
                    return
                # Consultar una Oficina aleatoria
                oficina = Oficina.query.order_by(func.random()).first()
                if oficina is None:
                    console.print("[yellow]No hay oficinas para asignar citas[/yellow]")
                    return
                # Consultar si hay un CitOficinaServicio para el servicio y oficina
                cit_oficina_servicio = CitOficinaServicio.query.filter_by(
                    cit_servicio_id=cit_servicio.id,
                    oficina_id=oficina.id,
                ).first()
                # Si lo hay, salir el bucle
                if cit_oficina_servicio:
                    break
            # Crear la cita
            cit_cita = CitCita()
            cit_cita.cit_cliente_id = cit_cliente.id
            cit_cita.cit_servicio_id = cit_servicio.id
            cit_cita.oficina_id = oficina.id
            cit_cita.inicio = fecha_hora
            cit_cita.termino = fecha_hora + timedelta(hours=cit_servicio.duracion.hour, minutes=cit_servicio.duracion.minute)
            cit_cita.notas = Faker().sentence(nb_words=6)
            cit_cita.estado = "PENDIENTE"
            cit_cita.cancelar_antes = cit_cita.inicio - timedelta(hours=24)
            cit_cita.asistencia = False
            cit_cita.codigo_asistencia = "".join(random.choices("0123456789", k=6))
            cit_cita.save()
            contador += 1
    # Mensaje final
    console.print(f"[green]Se han agregado {contador} citas falsas[/green]")


@cit_citas.command()
def eliminar(horas: int = 24):
    """Eliminar citas pasadas"""
    console = Console()
    # Definir el tiempo límite
    tiempo_limite = datetime.now() - timedelta(hours=horas)
    # Consultar las citas a eliminar (solo activas)
    query_citas = CitCita.query.filter(CitCita.inicio < tiempo_limite, CitCita.estatus == "A")
    total_citas = query_citas.count()

    if total_citas == 0:
        console.print(f"[green]No hay citas para eliminar con más de {horas} horas de antigüedad.[/green]")
        return

    commit_cada = 500

    with Progress(console=console) as progress:
        task = progress.add_task(f"Eliminando {total_citas} citas...", total=total_citas)

        # 1. Obtener solo los IDs para no cargar todos los objetos en memoria.
        #    Se usa with_entities para seleccionar solo la columna 'id'.
        #    .all() aquí es seguro porque solo trae una lista de tuplas de IDs.
        citas_ids = [c[0] for c in query_citas.with_entities(CitCita.id).all()]

        # 2. Procesar los IDs en lotes.
        for i in range(0, total_citas, commit_cada):
            # Seleccionar el lote actual de IDs
            lote_ids = citas_ids[i : i + commit_cada]

            # 3. Ejecutar un UPDATE masivo para el lote actual.
            #    Esto es mucho más eficiente que cargar y modificar cada objeto.
            database.session.query(CitCita).filter(CitCita.id.in_(lote_ids)).update({"estatus": "B"}, synchronize_session=False)

            database.session.commit()
            progress.update(task, advance=len(lote_ids))

    console.print(f"[green]Se han eliminado {total_citas} citas con más de {horas} horas de antigüedad.[/green]")


def _get_proximo_dia_habil() -> date:
    """Obtener el próximo día hábil, saltando fines de semana y días inhábiles"""
    dias_inhabiles = {
        d.fecha
        for d in CitDiaInhabil.query.filter(
            CitDiaInhabil.estatus == "A",
            CitDiaInhabil.fecha >= date.today(),
        ).all()
    }
    candidate = date.today() + timedelta(days=1)
    while True:
        if candidate.weekday() in (5, 6) or candidate in dias_inhabiles:
            candidate += timedelta(days=1)
            continue
        return candidate


@cit_citas.command()
def enviar_agenda(test: bool = typer.Option(True, "--test/--no-test", help="Prueba: guarda en HTML pero no envía por correo")):
    """Enviar la agenda del próximo día hábil a los usuarios de cada oficina por SendGrid"""
    console = Console()

    # Cargar variables de entorno
    load_dotenv()
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY", "")
    sendgrid_from_email = os.getenv("SENDGRID_FROM_EMAIL", "")

    # Validar variables de entorno de SendGrid
    if not test and not sendgrid_api_key:
        console.print("[red]Falta SENDGRID_API_KEY[/red]")
        raise typer.Exit(1)
    if not test and not sendgrid_from_email:
        console.print("[red]Falta SENDGRID_FROM_EMAIL[/red]")
        raise typer.Exit(1)

    # Obtener el próximo día hábil
    proximo_dia_habil = _get_proximo_dia_habil()
    console.print(f"Próximo día hábil: [cyan]{proximo_dia_habil}[/cyan]")

    # Límites del día para el filtro de citas
    inicio_dia = datetime.combine(proximo_dia_habil, time.min)
    fin_dia = inicio_dia + timedelta(days=1)

    # Consultar las oficinas activas que pueden agendar citas
    oficinas = Oficina.query.filter(
        Oficina.estatus == "A",
        Oficina.puede_agendar_citas,
    ).all()

    mensajes_finales = []

    for oficina in oficinas:
        # Consultar las citas de la oficina para el próximo día hábil
        citas = (
            CitCita.query.filter(
                CitCita.estatus == "A",
                CitCita.oficina_id == oficina.id,
                CitCita.inicio >= inicio_dia,
                CitCita.inicio < fin_dia,
            )
            .order_by(CitCita.inicio)
            .all()
        )

        if not citas:
            continue

        # Consultar los usuarios activos asignados a la oficina
        usuarios_oficinas = UsuarioOficina.query.filter(
            UsuarioOficina.estatus == "A",
            UsuarioOficina.oficina_id == oficina.id,
        ).all()
        usuarios = [uo.usuario for uo in usuarios_oficinas if uo.usuario.estatus == "A"]

        if not usuarios:
            continue

        usuarios_emails_str = ", ".join(u.email for u in usuarios)

        # Elaborar asunto y encabezado
        subject = f"Citas de la oficina {oficina.descripcion_corta} para {proximo_dia_habil}"
        elaboracion_fecha_hora_str = datetime.now().strftime("%d/%B/%Y %I:%M%p")

        # Construir tabla HTML
        table_html = '<table border="1" style="width:100%; border: 1px solid black; border-collapse: collapse;">'
        table_html += "<thead><tr>"
        for col in ["Hora", "Nombre", "Servicio", "Notas"]:
            table_html += f'<th style="padding: 4px;">{col}</th>'
        table_html += "</tr></thead><tbody>"
        for cita in citas:
            nombre = (
                f"{cita.cit_cliente.nombres} {cita.cit_cliente.apellido_primero} {cita.cit_cliente.apellido_segundo}".strip()
            )
            table_html += "<tr>"
            table_html += f'<td style="padding: 4px;">{cita.inicio.strftime("%H:%M")}</td>'
            table_html += f'<td style="padding: 4px;">{nombre}</td>'
            table_html += f'<td style="padding: 4px;">{cita.cit_servicio.clave}</td>'
            table_html += f'<td style="padding: 4px;">{cita.notas or ""}</td>'
            table_html += "</tr>"
        table_html += "</tbody></table>"

        # Armar contenidos del mensaje
        contenidos = [
            "<style> td {border:2px black solid !important} </style>",
            "<h1>PJECZ Citas V2</h1>",
            f"<h2>{subject}</h2>",
            table_html,
            f"<p>Fecha de elaboración: <b>{elaboracion_fecha_hora_str}.</b></p>",
            "<p>ESTE MENSAJE ES ELABORADO POR UN PROGRAMA. FAVOR DE NO RESPONDER.</p>",
        ]

        # Enviar por SendGrid cuando no es prueba
        if not test:
            send_grid = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)
            mail = Mail(
                from_email=Email(sendgrid_from_email),
                to_emails=[u.email for u in usuarios],
                subject=subject,
                html_content=Content("text/html", "<br>".join(contenidos)),
            )
            send_grid.send(mail)
            mensajes_finales.append(f"Mensaje enviado a [blue]{usuarios_emails_str}[/blue] con [green]{subject}[/green]")

        # Guardar siempre en archivo HTML (útil para revisión)
        archivo = f"agenda_a_usuarios-{oficina.clave}.html"
        ruta = Path(archivo)
        html_doc = f"<!DOCTYPE html><html><head><title>{subject}</title></head><body>"
        html_doc += "".join(f"<div>{c}</div>" for c in contenidos)
        html_doc += "</body></html>"
        with open(ruta, "w", encoding="utf-8") as puntero:
            puntero.write(html_doc)

        if test:
            mensajes_finales.append(
                f"Se guardó el mensaje en [blue]{archivo}[/blue] con [green]{subject}[/green] porque es una prueba"
            )

    for mensaje in mensajes_finales:
        console.print(mensaje)
