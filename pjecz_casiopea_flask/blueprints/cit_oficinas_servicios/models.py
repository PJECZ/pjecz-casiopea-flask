"""
Cit Oficinas Servicios, modelos
"""

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...config.extensions import database
from ...lib.universal_mixin import UniversalMixin


class CitOficinaServicio(database.Model, UniversalMixin):
    """CitOficinaServicio"""

    # Nombre de la tabla
    __tablename__ = "cit_oficinas_servicios"

    # Clave primaria
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Claves foráneas
    cit_servicio_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cit_servicios.id"), index=True)
    cit_servicio: Mapped["CitServicio"] = relationship(back_populates="cit_oficinas_servicios")
    oficina_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("oficinas.id"), index=True)
    oficina: Mapped["Oficina"] = relationship(back_populates="cit_oficinas_servicios")

    # Columnas
    descripcion: Mapped[str] = mapped_column(String(256))

    def __repr__(self):
        """Representación"""
        return f"<CitOficinaServicio {self.id}>"
