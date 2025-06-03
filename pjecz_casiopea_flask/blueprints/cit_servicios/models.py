"""
Cit Servicios, modelos
"""

from datetime import time
from typing import List, Optional
import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...config.extensions import database
from ...lib.universal_mixin import UniversalMixin


class CitServicio(database.Model, UniversalMixin):
    """CitServicio"""

    # Nombre de la tabla
    __tablename__ = "cit_servicios"

    # Clave primaria
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Clave foránea
    cit_categoria_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cit_categorias.id"))
    cit_categoria: Mapped["CitCategoria"] = relationship(back_populates="cit_servicios")

    # Columnas
    clave: Mapped[str] = mapped_column(String(16), unique=True)
    descripcion: Mapped[str] = mapped_column(String(256))
    duracion: Mapped[time]
    documentos_limite: Mapped[int]
    desde: Mapped[Optional[time]]
    hasta: Mapped[Optional[time]]
    dias_habilitados: Mapped[str] = mapped_column(String(7))
    es_activo: Mapped[bool] = mapped_column(default=True)

    # Hijos
    cit_citas: Mapped[List["CitCita"]] = relationship("CitCita", back_populates="cit_servicio")
    cit_oficinas_servicios: Mapped[List["CitOficinaServicio"]] = relationship(
        "CitOficinaServicio", back_populates="cit_servicio"
    )

    def __repr__(self):
        """Representación"""
        return f"<CitServicio {self.clave}>"
