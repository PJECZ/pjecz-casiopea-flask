-- 2026-11-20
-- Agregar el módulo `AUT TIPOS ENVIOS` a la tabla `modulos` (visible en el menú de navegación)
-- y darle al rol `ADMINISTRADOR` en nivel 4 (ADMINISTRAR) en `permisos`

-- Insertar el módulo
INSERT INTO modulos (id, nombre, nombre_corto, icono, ruta, en_navegacion, creado, modificado, estatus)
VALUES (
    gen_random_uuid(),
    'AUT TIPOS ENVIOS',
    'Tipos de Envíos',
    'mdi mdi-send',
    '/aut_tipos_envios',
    TRUE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    'A'
);

-- Insertar el permiso para el rol ADMINISTRADOR con nivel 4
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
  AND m.nombre = 'AUT TIPOS ENVIOS';
