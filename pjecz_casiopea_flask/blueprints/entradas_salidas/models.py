"""
Entradas-Salidas
"""

import uuid

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_casiopea_flask.extensions import database
from pjecz_casiopea_flask.lib.universal_mixin import UniversalMixin


class EntradaSalida(database.Model, UniversalMixin):
    """Entrada-Salida"""

    TIPOS = {
        "INGRESO": "Ingresó",
        "SALIO": "Salió",
    }

    # Nombre de la tabla
    __tablename__ = "entradas_salidas"

    # Clave primaria
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Claves foráneas
    usuario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id"))
    usuario: Mapped["Usuario"] = relationship(back_populates="entradas_salidas")

    # Columnas
    tipo: Mapped[str] = mapped_column(Enum(*TIPOS, name="entradas_salidas_tipos", native_enum=False), index=True)
    direccion_ip: Mapped[str] = mapped_column(String(64))

    def __repr__(self):
        """Representación"""
        return f"<EntradaSalida {self.id}>"
