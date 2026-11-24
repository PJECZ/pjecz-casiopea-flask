-- 2026-11-23
-- Crear tabla `ban_tipos` (catálogo de tipos de suspensión) y poblarla con datos iniciales

-- Crear tabla `ban_tipos`
CREATE TABLE IF NOT EXISTS ban_tipos (
    id SERIAL PRIMARY KEY,
    clave VARCHAR(32) NOT NULL,
    descripcion VARCHAR(128) NOT NULL,
    creado TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modificado TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estatus CHAR(1) NOT NULL DEFAULT 'A'
);

-- Insertar datos iniciales en la tabla `ban_tipos`
INSERT INTO ban_tipos (id, clave, descripcion) VALUES
(1, 'MINUTOS', 'Suspendido por minutos'),
(2, 'DIA', 'Suspendido por el día'),
(3, 'SIEMPRE', 'Suspendido indefinidamente.')
ON CONFLICT (id) DO NOTHING;

-- Sincronizar la secuencia del id con los registros insertados
SELECT setval(pg_get_serial_sequence('ban_tipos', 'id'), (SELECT MAX(id) FROM ban_tipos));

-- Si la tabla ya se había creado con el prefijo `BAN_` en la clave, quitárselo (MINUTOS, DIA, SIEMPRE)
UPDATE ban_tipos SET clave = substring(clave FROM 5) WHERE id IN (1, 2, 3) AND clave LIKE 'BAN\_%';
