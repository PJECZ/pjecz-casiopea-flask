"""
Web Archivos, modelos
"""

from typing import Optional
import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...config.extensions import database
from ...lib.universal_mixin import UniversalMixin


class WebArchivo(database.Model, UniversalMixin):
    """WebArchivo"""

    # Nombre de la tabla
    __tablename__ = "web_archivos"

    # Clave primaria
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Clave foránea
    web_pagina_id: Mapped[int] = mapped_column(ForeignKey("web_paginas.id"))
    web_pagina: Mapped["WebPagina"] = relationship(back_populates="web_archivos")

    # Columnas
    archivo: Mapped[str] = mapped_column(String(256))
    clave: Mapped[str] = mapped_column(String(16), unique=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(256))
    url: Mapped[str] = mapped_column(String(256))

    def __repr__(self):
        """Representación"""
        return f"<WebArchivo {self.clave}>"
