-- 2026-11-20
-- Creación de tablas para la verificación de usuarios y clientes en el proceso de autentificación de dos pasos.

-- Crea tabla `aut_verificaciones_usuarios` utilizada para el código de verificación que se usa en la autentificación de dos pasos.
CREATE TABLE IF NOT EXISTS  aut_verificaciones_usuarios (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    creado TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modificado TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estatus CHAR(1) NOT NULL DEFAULT 'A',
    usuario_id uuid NOT NULL REFERENCES usuarios(id),
    codigo_verificacion VARCHAR(6) NOT NULL,
    tiempo_caducidad TIMESTAMP NOT NULL,
    intentos INT NOT NULL DEFAULT 0,
    aut_tipo_envio_id INT NOT NULL REFERENCES aut_tipos_envios(id),
    utilizado BOOLEAN NOT NULL DEFAULT FALSE,
    direccion_ip VARCHAR(45),
    dispositivo VARCHAR(300),
    telefono VARCHAR(20),
    email VARCHAR(256)
);

-- Crea tabla `aut_verificaciones_clientes` utilizada para el código de verificación que se usa en la autentificación de dos pasos.
CREATE TABLE IF NOT EXISTS aut_verificaciones_clientes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    creado TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modificado TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estatus CHAR(1) NOT NULL DEFAULT 'A',
    cit_cliente_id uuid NOT NULL REFERENCES cit_clientes(id),
    codigo_verificacion VARCHAR(6) NOT NULL,
    tiempo_caducidad TIMESTAMP NOT NULL,
    intentos INT NOT NULL DEFAULT 0,
    aut_tipo_envio_id INT NOT NULL REFERENCES aut_tipos_envios(id),
    utilizado BOOLEAN NOT NULL DEFAULT FALSE,
    direccion_ip VARCHAR(45),
    dispositivo VARCHAR(300),
    telefono VARCHAR(20),
    email VARCHAR(256)
);