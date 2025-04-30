"""
Bitácoras
"""

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_casiopea_flask.extensions import database
from pjecz_casiopea_flask.lib.universal_mixin import UniversalMixin


class Bitacora(database.Model, UniversalMixin):
    """Bitacora"""

    # Nombre de la tabla
    __tablename__ = "bitacoras"

    # Clave primaria
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Claves foráneas
    modulo_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("modulos.id"))
    modulo: Mapped["Modulo"] = relationship(back_populates="bitacoras")
    usuario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id"))
    usuario: Mapped["Usuario"] = relationship(back_populates="bitacoras")

    # Columnas
    descripcion: Mapped[str] = mapped_column(String(256))
    url: Mapped[str] = mapped_column(String(512))

    def __repr__(self):
        """Representación"""
        return f"<Bitacora {self.creado} {self.descripcion}>"
