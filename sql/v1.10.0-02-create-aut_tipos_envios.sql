-- 2026-11-20
-- Crear tabla `aut_tipos_envios` y poblarla con datos iniciales

-- Crear tabla `aut_tipos_envios`
CREATE TABLE aut_tipos_envios (
    id SERIAL PRIMARY KEY,
    descripcion  VARCHAR(32) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modificado TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estatus CHAR(1) NOT NULL DEFAULT 'A'
);

-- Insertar datos iniciales en la tabla `aut_tipos_envios`
INSERT INTO aut_tipos_envios (descripcion) VALUES
('Correo Electrónico'),
('SMS'),
('WhatsApp');