"""
Ban Bloqueados, modelos
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...config.extensions import database
from ...lib.universal_mixin import UniversalMixin


class BanBloqueado(database.Model, UniversalMixin):
    """BanBloqueado"""

    # Nombre de la tabla
    __tablename__ = "ban_bloqueados"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Claves foráneas
    ban_tipo_id: Mapped[int] = mapped_column(ForeignKey("ban_tipos.id"))
    ban_tipo: Mapped["BanTipo"] = relationship("BanTipo")

    # Columnas
    tiempo: Mapped[datetime] = mapped_column(default=datetime.now)  # Fecha y hora del último acceso
    direccion_ip: Mapped[Optional[str]] = mapped_column(String(45))  # Si existe, se bloquea esta IP
    email: Mapped[Optional[str]] = mapped_column(String(256))  # Si existe, se bloquea esta cuenta

    def __repr__(self):
        """Representación"""
        return f"<BanBloqueado {self.id}>"
