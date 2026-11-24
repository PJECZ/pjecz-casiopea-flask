"""
Servicio para bannear ataques de login
"""

import datetime
import enum

from ..config.settings import get_settings
from wtforms.validators import email

from ..blueprints.ban_bloqueados.models import BanBloqueado
from ..blueprints.ban_intentos.models import BanIntento


class LoginBanService:
    """
    Servicio para bannear ataques de login
    """

    class BanType(enum.IntEnum):
        """Tipos de ban"""
        MINUTOS = 1
        DIA = 2
        PERMANENTE = 3


    def __init__(self, modelo_bloqueado: BanBloqueado, modelo_intento: BanIntento):
        # Cargar variables de configuración desde settings.py
        settings = get_settings()
        self.__max_intentos = settings.BAN_MAX_ATTEMPTS
        self.__duracion_minutos = settings.BAN_DURATION_MINUTES
        self.__max_intentos_por_dia = settings.BAN_MAX_ATTEMPTS_PER_DAY

        self.__modelo_bloqueado = modelo_bloqueado
        self.__modelo_intento = modelo_intento

    def _esta_baneado_ip(self, ip: str) -> bool:
        """Verifica si una IP está baneada"""
        ban = self.__modelo_bloqueado.query.filter_by(direccion_ip=ip).filter_by(estatus='A').first()

        return self.__reglas_baneado(ban)

    def _esta_baneado_email(self, email: str) -> bool:
        """Verifica si un email está baneado"""

        ban = self.__modelo_bloqueado.query.filter_by(email=email).filter_by(estatus='A').first()

        return self.__reglas_baneado(ban)

    def esta_baneado(self, direccion_ip: str = None, email: str = None) -> bool:
        """Verifica si está baneado"""

        # Primero verificamos si la dirección IP está baneada
        if direccion_ip:
            if self._esta_baneado_ip(direccion_ip):
                return True

        # Validar si es un email válido antes de verificar el banneo
        if email and not email(email):
            self.__marcar_intento(direccion_ip, email)
            raise ValueError("El email proporcionado no es válido.")    

        # Luego verificamos si el email está baneado
        if email:
            if self._esta_baneado_email(email):
                return True

        # Marcamos el intento de login fallido si no está baneado
        intentos = self.__marcar_intento(direccion_ip, email)

        # Validar número de intentos
        if intentos >= self.__max_intentos:
            # Revisar si se ha excedido el número de intentos por día
            intentos_por_dia = self.__contar_numero_intentos_por_dia(direccion_ip, email)
            if intentos_por_dia >= self.__max_intentos_por_dia:
                # Bannear permanentemente
                ban = self.__modelo_bloqueado(direccion_ip=direccion_ip, email=email, ban_tipo=self.BanType.PERMANENTE, tiempo=datetime.datetime.now())
                ban.save()
                return True
            # Bannear por minutos
            ban = self.__modelo_bloqueado(direccion_ip=direccion_ip, email=email, ban_tipo=self.BanType.MINUTOS, tiempo=datetime.datetime.now())
            ban.save()
            return True

        return False

    def __reglas_baneado(self, ban: BanBloqueado) -> bool:
        """Verifica las reglas de baneado"""

        if ban.ban_tipo == self.BanType.PERMANENTE:
            return True
        
        if ban.ban_tipo == self.BanType.DIA:
            if ban.fecha_ban.date() == datetime.now().date():
                return True
            else:
                ban.delete()
                return False

        if ban.ban_tipo == self.BanType.MINUTOS:
            if ban.tiempo + datetime.timedelta(minutes=self.__duracion_minutos) > datetime.now():
                return True
            else:
                ban.delete()
                return False

        return False

    def __marcar_intento(self, direccion_ip: str = None, email: str = None) -> int:
        """Marca un intento de login fallido"""

        intentos = 0
        intentos_reg = self.__modelo_intento.query.filter_by(direccion_ip=direccion_ip).filter_by(email=email).first()
        if not intentos_reg:
            intentos_reg = self.__modelo_intento(direccion_ip=direccion_ip, email=email)
        else:
            intentos = intentos_reg.intentos
        intentos_reg.intentos = intentos + 1
        intentos_reg.save()
        return intentos_reg.intentos

    def __contar_numero_intentos_por_dia(self, direccion_ip: str = None, email: str = None) -> int:
        """Cuenta el número de intentos de login fallidos por día"""

        numero_registros = self.__modelo_intento.query\
            .filter_by(direccion_ip=direccion_ip)\
            .filter_by(email=email).filter_by(fecha=datetime.datetime.now().date())\
            .filter_by(estatus='A')\
            .count()
        if not numero_registros:
            return 0
        else:
            return numero_registros