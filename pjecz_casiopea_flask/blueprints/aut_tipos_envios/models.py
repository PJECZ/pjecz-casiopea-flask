"""
Aut Tipos Envíos, modelos
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ...config.extensions import database
from ...lib.universal_mixin import UniversalMixin


class AutTipoEnvio(database.Model, UniversalMixin):
    """AutTipoEnvio"""

    # Nombre de la tabla
    __tablename__ = "aut_tipos_envios"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Columnas
    descripcion: Mapped[str] = mapped_column(String(32))
    activo: Mapped[bool] = mapped_column(default=True)

    def __repr__(self):
        """Representación"""
        return f"<AutTipoEnvio {self.descripcion}>"
