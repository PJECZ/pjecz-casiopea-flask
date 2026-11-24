-- 2026-11-23
-- Crear tabla `ban_intentos` para contar los intentos de acceso (login) por dirección IP y email,
-- y así aplicar las reglas de baneo y tener datos para reportes de posibles ataques.

-- Crear tabla `ban_intentos`
CREATE TABLE IF NOT EXISTS ban_intentos (
    id SERIAL PRIMARY KEY,
    creado TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modificado TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estatus CHAR(1) NOT NULL DEFAULT 'A',
    intentos INT NOT NULL DEFAULT 0,
    tiempo TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Fecha y hora del último intento
    direccion_ip VARCHAR(45) NOT NULL,
    email VARCHAR(256) NOT NULL
);

-- Índice para buscar rápido el contador de una persona por dirección IP y email
CREATE INDEX IF NOT EXISTS ban_intentos_direccion_ip_email_idx ON ban_intentos (direccion_ip, email);
