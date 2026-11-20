"""
Aut Verificaciones Clientes, modelos
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...config.extensions import database
from ...lib.universal_mixin import UniversalMixin


class AutVerificacionCliente(database.Model, UniversalMixin):
    """AutVerificacionCliente"""

    # Nombre de la tabla
    __tablename__ = "aut_verificaciones_clientes"

    # Clave primaria
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Claves foráneas
    cit_cliente_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cit_clientes.id"))
    cit_cliente: Mapped["CitCliente"] = relationship("CitCliente")
    aut_tipo_envio_id: Mapped[int] = mapped_column(ForeignKey("aut_tipos_envios.id"))
    aut_tipo_envio: Mapped["AutTipoEnvio"] = relationship("AutTipoEnvio")

    # Columnas
    codigo_verificacion: Mapped[str] = mapped_column(String(6))
    tiempo_caducidad: Mapped[datetime]
    intentos: Mapped[int] = mapped_column(default=0)
    utilizado: Mapped[bool] = mapped_column(default=False)
    telefono: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(256))
    direccion_ip: Mapped[Optional[str]] = mapped_column(String(45))
    dispositivo: Mapped[Optional[str]] = mapped_column(String(300))

    def __repr__(self):
        """Representación"""
        return f"<AutVerificacionCliente {self.id}>"
