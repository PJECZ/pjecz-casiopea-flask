"""
Sesiones, modelos
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...config.extensions import database
from ...lib.universal_mixin import UniversalMixin


class Sesion(database.Model, UniversalMixin):
    """Sesion: un registro por usuario, su id es el mismo que el del usuario"""

    # Nombre de la tabla
    __tablename__ = "sesiones"

    # Clave primaria, es la misma que la del usuario
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), primary_key=True)
    usuario: Mapped["Usuario"] = relationship("Usuario")

    # Columnas
    activa: Mapped[bool] = mapped_column(default=False, index=True)
    identificador: Mapped[str] = mapped_column(String(64))  # Token que también se guarda en la cookie de sesión
    direccion_ip: Mapped[Optional[str]] = mapped_column(String(64))
    navegador: Mapped[Optional[str]] = mapped_column(String(256))
    inicio: Mapped[datetime] = mapped_column(default=datetime.now)  # Fecha y hora del login
    ultimo_acceso: Mapped[datetime] = mapped_column(default=datetime.now)  # Fecha y hora de la última petición

    def __repr__(self):
        """Representación"""
        return f"<Sesion {self.id}>"
