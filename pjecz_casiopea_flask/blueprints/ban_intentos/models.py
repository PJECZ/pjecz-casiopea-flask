"""
Ban Intentos, modelos
"""

from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ...config.extensions import database
from ...lib.universal_mixin import UniversalMixin


class BanIntento(database.Model, UniversalMixin):
    """BanIntento"""

    # Nombre de la tabla
    __tablename__ = "ban_intentos"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Columnas
    intentos: Mapped[int] = mapped_column(default=0)
    tiempo: Mapped[datetime] = mapped_column(default=datetime.now)  # Fecha y hora del último intento
    direccion_ip: Mapped[str] = mapped_column(String(45))
    email: Mapped[str] = mapped_column(String(256))

    def __repr__(self):
        """Representación"""
        return f"<BanIntento {self.id}>"
