"""
Cit Citas, modelos
"""

from datetime import datetime
import uuid

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...config.extensions import database
from ...lib.universal_mixin import UniversalMixin


class CitCita(database.Model, UniversalMixin):
    """CitCita"""

    ESTADOS = {
        "ASISTIO": "Asistió",
        "CANCELO": "Canceló",
        "INASISTENCIA": "Inasistencia",
        "PENDIENTE": "Pendiente",
    }

    # Nombre de la tabla
    __tablename__ = "cit_citas"

    # Clave primaria
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Claves foráneas
    cit_cliente_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cit_clientes.id"), index=True)
    cit_cliente: Mapped["CitCliente"] = relationship(back_populates="cit_citas")
    cit_servicio_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cit_servicios.id"), index=True)
    cit_servicio: Mapped["CitServicio"] = relationship(back_populates="cit_citas")
    oficina_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("oficinas.id"), index=True)
    oficina: Mapped["Oficina"] = relationship(back_populates="cit_citas")

    # Columnas
    inicio: Mapped[datetime]
    termino: Mapped[datetime]
    notas: Mapped[str] = mapped_column(Text())
    estado: Mapped[str] = mapped_column(Enum(*ESTADOS, name="estados", native_enum=False), index=True)
    asistencia: Mapped[bool] = mapped_column(default=False)
    codigo_asistencia: Mapped[str] = mapped_column(String(4))
    cancelar_antes: Mapped[datetime]

    def __repr__(self):
        """Representación"""
        return f"<CitCita {self.id}>"
