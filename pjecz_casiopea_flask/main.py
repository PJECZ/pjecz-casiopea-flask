"""
PJECZ Casiopea Flask
"""

from flask import Flask

from pjecz_casiopea_flask.blueprints.autoridades.views import autoridades
from pjecz_casiopea_flask.blueprints.bitacoras.views import bitacoras
from pjecz_casiopea_flask.blueprints.cit_categorias.views import cit_categorias
from pjecz_casiopea_flask.blueprints.cit_citas.views import cit_citas
from pjecz_casiopea_flask.blueprints.cit_clientes.views import cit_clientes
from pjecz_casiopea_flask.blueprints.cit_clientes_recuperaciones.views import cit_clientes_recuperaciones
from pjecz_casiopea_flask.blueprints.cit_clientes_registros.views import cit_clientes_registros
from pjecz_casiopea_flask.blueprints.cit_dias_inhabiles.views import cit_dias_inhabiles
from pjecz_casiopea_flask.blueprints.cit_horas_bloqueadas.views import cit_horas_bloqueadas
from pjecz_casiopea_flask.blueprints.cit_oficinas_servicios.views import cit_oficinas_servicios
from pjecz_casiopea_flask.blueprints.cit_servicios.views import cit_servicios
from pjecz_casiopea_flask.blueprints.distritos.views import distritos
from pjecz_casiopea_flask.blueprints.domicilios.views import domicilios
from pjecz_casiopea_flask.blueprints.entradas_salidas.views import entradas_salidas
from pjecz_casiopea_flask.blueprints.materias.views import materias
from pjecz_casiopea_flask.blueprints.modulos.views import modulos
from pjecz_casiopea_flask.blueprints.permisos.views import permisos
from pjecz_casiopea_flask.blueprints.roles.views import roles
from pjecz_casiopea_flask.blueprints.sistemas.views import sistemas
from pjecz_casiopea_flask.blueprints.usuarios.views import usuarios
from pjecz_casiopea_flask.blueprints.usuarios_oficinas.views import usuarios_oficinas
from pjecz_casiopea_flask.blueprints.usuarios_roles.views import usuarios_roles
from pjecz_casiopea_flask.extensions import csrf, database, login_manager, moment
from pjecz_casiopea_flask.settings import Settings

# Definir app
app = Flask(__name__, instance_relative_config=True)

# Cargar la configuración
app.config.from_object(Settings())

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
app.register_blueprint(permisos)
app.register_blueprint(roles)
app.register_blueprint(sistemas)
app.register_blueprint(usuarios)
app.register_blueprint(usuarios_oficinas)
app.register_blueprint(usuarios_roles)

# Cargar extensiones
csrf.init_app(app)
database.init_app(app)
login_manager.init_app(app)
moment.init_app(app)
