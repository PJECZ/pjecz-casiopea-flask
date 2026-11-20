"""
Aut Verificaciones Usuarios, modelos
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...config.extensions import database
from ...lib.universal_mixin import UniversalMixin


class AutVerificacionUsuario(database.Model, UniversalMixin):
    """AutVerificacionUsuario"""

    # Nombre de la tabla
    __tablename__ = "aut_verificaciones_usuarios"

    # Clave primaria
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Claves foráneas
    usuario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id"))
    usuario: Mapped["Usuario"] = relationship("Usuario")
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
        return f"<AutVerificacionUsuario {self.id}>"
