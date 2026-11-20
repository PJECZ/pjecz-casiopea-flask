-- 2026-11-20
-- Agregar los módulos `AUT TIPOS ENVIOS` y `AUT VERIFICACIONES USUARIOS` a la tabla `modulos` (visibles en el menú de navegación)
-- y darle al rol `ADMINISTRADOR` el nivel 4 (ADMINISTRAR) en `permisos`.
-- El script se puede ejecutar varias veces: no agrega los módulos ni los permisos que ya existen.

-- Insertar los módulos que aún no estén cargados
INSERT INTO modulos (id, nombre, nombre_corto, icono, ruta, en_navegacion, creado, modificado, estatus)
SELECT gen_random_uuid(), v.nombre, v.nombre_corto, v.icono, v.ruta, TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'A'
FROM (
    VALUES
        ('AUT TIPOS ENVIOS', 'Tipos de Envíos', 'mdi mdi-send', '/aut_tipos_envios'),
        ('AUT VERIFICACIONES USUARIOS', 'Verificaciones de Acceso de Usuarios', 'mdi mdi-shield-key', '/aut_verificaciones_usuarios')
) AS v (nombre, nombre_corto, icono, ruta)
WHERE NOT EXISTS (
    SELECT 1 FROM modulos m WHERE m.nombre = v.nombre
);

-- Insertar los permisos para el rol ADMINISTRADOR con nivel 4, si aún no los tiene
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
  AND m.nombre IN ('AUT TIPOS ENVIOS', 'AUT VERIFICACIONES USUARIOS')
  AND NOT EXISTS (
    SELECT 1 FROM permisos p WHERE p.rol_id = r.id AND p.modulo_id = m.id
);
