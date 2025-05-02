"""
Cit Dias Inhábiles, modelos
"""

from datetime import date
import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...config.extensions import database
from ...lib.universal_mixin import UniversalMixin


class CitDiaInhabil(database.Model, UniversalMixin):
    """CitDiaInhabil"""

    # Nombre de la tabla
    __tablename__ = "cit_dias_inhabiles"

    # Clave primaria
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Columnas
    fecha: Mapped[date] = mapped_column(unique=True)
    descripcion: Mapped[str] = mapped_column(String(256))

    def __repr__(self):
        """Representación"""
        return f"<CitDiaInhabil {self.fecha}>"
