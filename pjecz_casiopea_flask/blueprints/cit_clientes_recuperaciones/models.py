"""
Cit Clientes Recuperaciones, modelos
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...config.extensions import database
from ...lib.universal_mixin import UniversalMixin


class CitClienteRecuperacion(database.Model, UniversalMixin):
    """CitClienteRecuperacion"""

    # Nombre de la tabla
    __tablename__ = "cit_clientes_recuperaciones"

    # Clave primaria
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Clave foránea
    cit_cliente_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cit_clientes.id"))
    cit_cliente: Mapped["CitCliente"] = relationship(back_populates="cit_clientes_recuperaciones")

    # Columnas
    expiracion: Mapped[datetime]
    cadena_validar: Mapped[str] = mapped_column(String(256))
    mensajes_cantidad: Mapped[int] = mapped_column(default=0)
    ya_recuperado: Mapped[bool] = mapped_column(default=False)

    # Para controlar la migracion desde pjecz_citas_v2 se incluye el id_original
    id_original: Mapped[Optional[int]] = mapped_column(index=True)

    def __repr__(self):
        """Representación"""
        return f"<CitClienteRecuperacion {self.id}>"
