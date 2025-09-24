"""
PJECZ Casiopea Flask
"""

from flask import Flask
from redis import Redis
from rq import Queue

from .blueprints.autoridades.views import autoridades
from .blueprints.bitacoras.views import bitacoras
from .blueprints.cit_categorias.views import cit_categorias
from .blueprints.cit_citas.views import cit_citas
from .blueprints.cit_clientes.views import cit_clientes
from .blueprints.cit_clientes_recuperaciones.views import cit_clientes_recuperaciones
from .blueprints.cit_clientes_registros.views import cit_clientes_registros
from .blueprints.cit_dias_inhabiles.views import cit_dias_inhabiles
from .blueprints.cit_horas_bloqueadas.views import cit_horas_bloqueadas
from .blueprints.cit_oficinas_servicios.views import cit_oficinas_servicios
from .blueprints.cit_servicios.views import cit_servicios
from .blueprints.distritos.views import distritos
from .blueprints.domicilios.views import domicilios
from .blueprints.entradas_salidas.views import entradas_salidas
from .blueprints.materias.views import materias
from .blueprints.modulos.views import modulos
from .blueprints.oficinas.views import oficinas
from .blueprints.pag_pagos.views import pag_pagos
from .blueprints.pag_tramites_servicios.views import pag_tramites_servicios
from .blueprints.permisos.views import permisos
from .blueprints.roles.views import roles
from .blueprints.sistemas.views import sistemas
from .blueprints.tareas.views import tareas
from .blueprints.usuarios.models import Usuario
from .blueprints.usuarios.views import usuarios
from .blueprints.usuarios_oficinas.views import usuarios_oficinas
from .blueprints.usuarios_roles.views import usuarios_roles
from .blueprints.web_archivos.views import web_archivos
from .blueprints.web_paginas.views import web_paginas
from .blueprints.web_ramas.views import web_ramas
from .config.extensions import authentication, csrf, database, login_manager, moment
from .config.settings import Settings

# Definir app
app = Flask(__name__, instance_relative_config=True)

# Cargar la configuración
app.config.from_object(Settings())

# Redis
app.redis = Redis(host=app.config["REDIS_URL"])
app.task_queue = Queue(app.config["TASK_QUEUE"], connection=app.redis, default_timeout=3000)

# Cargar las vistas
app.register_blueprint(autoridades)
app.register_blueprint(bitacoras)
app.register_blueprint(cit_categorias)
app.register_blueprint(cit_citas)
app.register_blueprint(cit_clientes)
app.register_blueprint(cit_clientes_recuperaciones)
app.register_blueprint(cit_clientes_registros)
app.register_blueprint(cit_dias_inhabiles)
app.register_blueprint(cit_horas_bloqueadas)
app.register_blueprint(cit_oficinas_servicios)
app.register_blueprint(cit_servicios)
app.register_blueprint(distritos)
app.register_blueprint(domicilios)
app.register_blueprint(entradas_salidas)
app.register_blueprint(materias)
app.register_blueprint(modulos)
app.register_blueprint(oficinas)
app.register_blueprint(pag_pagos)
app.register_blueprint(pag_tramites_servicios)
app.register_blueprint(permisos)
app.register_blueprint(roles)
app.register_blueprint(sistemas)
app.register_blueprint(tareas)
app.register_blueprint(usuarios)
app.register_blueprint(usuarios_oficinas)
app.register_blueprint(usuarios_roles)
app.register_blueprint(web_archivos)
app.register_blueprint(web_paginas)
app.register_blueprint(web_ramas)


# Cargar extensiones
csrf.init_app(app)
database.init_app(app)
login_manager.init_app(app)
moment.init_app(app)

# Flask Login authentication
authentication(Usuario)
