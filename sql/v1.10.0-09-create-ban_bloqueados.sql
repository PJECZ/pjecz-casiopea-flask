-- 2026-11-23
-- Crear tabla `ban_bloqueados`, la lista de castigo: direcciones IP y cuentas (email) bloqueadas.
-- Si `direccion_ip` tiene valor se bloquea esa IP, si `email` tiene valor se bloquea esa cuenta (pueden venir ambos).

-- Crear tabla `ban_bloqueados`
CREATE TABLE IF NOT EXISTS ban_bloqueados (
    id SERIAL PRIMARY KEY,
    creado TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modificado TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estatus CHAR(1) NOT NULL DEFAULT 'A',
    ban_tipo_id INT NOT NULL REFERENCES ban_tipos(id),
    tiempo TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Fecha y hora del último acceso
    direccion_ip VARCHAR(45),
    email VARCHAR(256),
    -- Debe haber al menos un dato a quién bloquear
    CONSTRAINT ban_bloqueados_ip_o_email_chk CHECK (direccion_ip IS NOT NULL OR email IS NOT NULL)
);

-- Índices para consultar rápido si una IP o una cuenta están bloqueadas
CREATE INDEX IF NOT EXISTS ban_bloqueados_direccion_ip_idx ON ban_bloqueados (direccion_ip);
CREATE INDEX IF NOT EXISTS ban_bloqueados_email_idx ON ban_bloqueados (email);
