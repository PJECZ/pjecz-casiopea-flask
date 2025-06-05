"""
Web Ramas, modelos
"""

from typing import List
import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...config.extensions import database
from ...lib.universal_mixin import UniversalMixin


class WebRama(database.Model, UniversalMixin):
    """WebRama"""

    ESTADOS = {
        "PENDIENTE": "Pendiente",
        "ENVIADO": "Enviado",
        "CANCELADO": "Cancelado",
    }

    # Nombre de la tabla
    __tablename__ = "web_ramas"

    # Clave primaria
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Columnas
    clave: Mapped[str] = mapped_column(String(16), unique=True)
    nombre: Mapped[str] = mapped_column(String(256))

    # Hijos
    web_paginas: Mapped[List["WebPagina"]] = relationship("WebPagina", back_populates="web_rama")

    def __repr__(self):
        """Representación"""
        return f"<WebRama {self.clave}>"
