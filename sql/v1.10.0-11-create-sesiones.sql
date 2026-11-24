-- 2026-11-24
-- Crear tabla `sesiones`: un registro por usuario (su id es el mismo del usuario) para saber quién tiene la sesión abierta.
-- No guarda historial: al volver a entrar se reutiliza el registro y `activa` indica si la sesión sigue abierta.
-- Agregar el módulo `SESIONES` al menú de navegación y darle al rol `ADMINISTRADOR` el nivel 4 (ADMINISTRAR).
-- El script se puede ejecutar varias veces.

-- Crear tabla `sesiones`
CREATE TABLE IF NOT EXISTS sesiones (
    id UUID PRIMARY KEY REFERENCES usuarios(id),
    creado TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modificado TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estatus CHAR(1) NOT NULL DEFAULT 'A',
    activa BOOLEAN NOT NULL DEFAULT FALSE,
    identificador VARCHAR(64) NOT NULL, -- Token que también se guarda en la cookie de sesión
    direccion_ip VARCHAR(64),
    navegador VARCHAR(256),
    inicio TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Fecha y hora del login
    ultimo_acceso TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP -- Fecha y hora de la última petición
);

-- Índice para listar rápido las sesiones activas
CREATE INDEX IF NOT EXISTS sesiones_activa_idx ON sesiones (activa);

-- Insertar el módulo si aún no está cargado
INSERT INTO modulos (id, nombre, nombre_corto, icono, ruta, en_navegacion, creado, modificado, estatus)
SELECT gen_random_uuid(), 'SESIONES', 'Sesiones', 'mdi mdi-account-clock', '/sesiones', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'A'
WHERE NOT EXISTS (
    SELECT 1 FROM modulos m WHERE m.nombre = 'SESIONES'
);

-- Insertar el permiso para el rol ADMINISTRADOR con nivel 4, si aún no lo tiene
INSERT INTO permisos (id, rol_id, modulo_id, nombre, nivel, creado, modificado, estatus)
SELECT
    gen_random_uuid(),
    r.id,
    m.id,
    r.nombre || ' puede ADMINISTRAR en ' || m.nombre,
    4,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    'A'
FROM roles r, modulos m
WHERE r.nombre = 'ADMINISTRADOR'
  AND m.nombre = 'SESIONES'
  AND NOT EXISTS (
    SELECT 1 FROM permisos p WHERE p.rol_id = r.id AND p.modulo_id = m.id
);
