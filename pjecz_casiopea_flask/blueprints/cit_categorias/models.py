"""
Cit Categorías, modelos
"""

import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...config.extensions import database
from ...lib.universal_mixin import UniversalMixin


class CitCategoria(database.Model, UniversalMixin):
    """CitCategoria"""

    # Nombre de la tabla
    __tablename__ = "cit_categorias"

    # Clave primaria
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Columnas
    clave: Mapped[str] = mapped_column(String(16), unique=True)
    nombre: Mapped[str] = mapped_column(String(256))
    es_activo: Mapped[bool] = mapped_column(default=True)

    # Hijos
    cit_servicios: Mapped["CitServicio"] = relationship("CitServicio", back_populates="cit_categoria")

    def __repr__(self):
        """Representación"""
        return f"<CitCategoria {self.nombre}>"
