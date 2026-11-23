"""
Ban Tipos, modelos
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ...config.extensions import database
from ...lib.universal_mixin import UniversalMixin


class BanTipo(database.Model, UniversalMixin):
    """BanTipo"""

    # Nombre de la tabla
    __tablename__ = "ban_tipos"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Columnas
    clave: Mapped[str] = mapped_column(String(32))
    descripcion: Mapped[str] = mapped_column(String(128))

    def __repr__(self):
        """Representación"""
        return f"<BanTipo {self.clave}>"
