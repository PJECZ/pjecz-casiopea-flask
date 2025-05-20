"""
Cit Horas Bloqueadas, modelos
"""

from datetime import date, time
import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...config.extensions import database
from ...lib.universal_mixin import UniversalMixin


class CitHoraBloqueada(database.Model, UniversalMixin):
    """CitHoraBloqueada"""

    # Nombre de la tabla
    __tablename__ = "cit_horas_bloqueadas"

    # Clave primaria
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Clave foránea
    oficina_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("oficinas.id"))
    oficina: Mapped["Oficina"] = relationship(back_populates="cit_horas_bloqueadas")

    # Columnas
    fecha: Mapped[date] = mapped_column(index=True)
    inicio: Mapped[time]
    termino: Mapped[time]
    descripcion: Mapped[str] = mapped_column(String(256))

    def __repr__(self):
        """Representación"""
        return f"<CitHoraBloqueada {self.id}>"
