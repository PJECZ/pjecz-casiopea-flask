"""
Oficinas, modelos
"""

from datetime import time
from typing import List
import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...config.extensions import database
from ...lib.universal_mixin import UniversalMixin


class Oficina(database.Model, UniversalMixin):
    """Oficina"""

    # Nombre de la tabla
    __tablename__ = "oficinas"

    # Clave primaria
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Claves foráneas
    domicilio_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("domicilios.id"))
    domicilio: Mapped["Domicilio"] = relationship(back_populates="oficinas")

    # Columnas
    clave: Mapped[str] = mapped_column(String(16), unique=True)
    descripcion: Mapped[str] = mapped_column(String(256))
    descripcion_corta: Mapped[str] = mapped_column(String(64))
    es_jurisdiccional: Mapped[bool] = mapped_column(default=False)
    puede_agendar_citas: Mapped[bool] = mapped_column(default=False)
    apertura: Mapped[time]
    cierre: Mapped[time]
    limite_personas: Mapped[int]
    puede_enviar_qr: Mapped[bool] = mapped_column(default=False)

    # Hijos
    cit_citas: Mapped[List["CitCita"]] = relationship("CitCita", back_populates="oficina")
    cit_horas_bloqueadas: Mapped[List["CitHoraBloqueada"]] = relationship("CitHoraBloqueada", back_populates="oficina")
    cit_oficinas_servicios: Mapped[List["CitOficinaServicio"]] = relationship("CitOficinaServicio", back_populates="oficina")
    usuarios_oficinas: Mapped[List["UsuarioOficina"]] = relationship("UsuarioOficina", back_populates="oficina")

    def __repr__(self):
        """Representación"""
        return f"<Oficina {self.clave}>"
