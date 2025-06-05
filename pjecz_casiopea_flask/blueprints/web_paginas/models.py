"""
Web Páginas, modelos
"""

from datetime import datetime, date
from typing import List, Optional
import uuid

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...config.extensions import database
from ...lib.universal_mixin import UniversalMixin


class WebPagina(database.Model, UniversalMixin):
    """WebPagina"""

    ESTADOS = {
        "BORRADOR": "Borrador",
        "PUBLICADO": "Publicado",
        "CANCELADO": "Cancelado",
    }

    # Nombre de la tabla
    __tablename__ = "web_paginas"

    # Clave primaria
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Claves foráneas
    web_rama_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("web_ramas.id"))
    web_rama: Mapped["WebRama"] = relationship(back_populates="web_paginas")

    # Columnas
    clave: Mapped[str] = mapped_column(String(16), unique=True)
    titulo: Mapped[str] = mapped_column(String(256))
    resumen: Mapped[Optional[str]] = mapped_column(String(1024))
    ruta: Mapped[str] = mapped_column(String(256))
    fecha_modificacion: Mapped[date]
    responsable: Mapped[Optional[str]] = mapped_column(String(256))
    etiquetas: Mapped[Optional[str]] = mapped_column(String(256))
    vista_previa: Mapped[Optional[str]] = mapped_column(String(256))
    contenido: Mapped[str] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(Enum(*ESTADOS, name="web_paginas_estados", native_enum=False), index=True)
    tiempo_publicar: Mapped[Optional[datetime]]
    tiempo_archivar: Mapped[Optional[datetime]]
    es_archivado: Mapped[bool] = mapped_column(default=False)

    # Hijos
    web_archivos: Mapped[List["WebArchivo"]] = relationship("WebArchivo", back_populates="web_pagina")

    def __repr__(self):
        """Representación"""
        return f"<WebPagina {self.clave}>"
