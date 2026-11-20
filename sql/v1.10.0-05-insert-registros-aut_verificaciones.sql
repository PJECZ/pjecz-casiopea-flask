-- 2026-11-20
-- Registros de prueba para las tablas `aut_verificaciones_usuarios` y `aut_verificaciones_clientes` con variantes en los datos:
-- utilizados, con máximo de intentos, en espera (vigentes) y caducados sin usar.
-- Los usuarios se toman de la tabla `usuarios` y los clientes de `cit_clientes` (hasta 3 activos de cada una, repartidos en rotación)
-- y los tipos de envío de `aut_tipos_envios` (1 = Correo Electrónico, 2 = SMS, 3 = WhatsApp).
-- Los campos `telefono` y `email` son los datos a donde se envió el código (pueden ser NULL).
-- ADVERTENCIA: son datos de prueba, no ejecutar en producción. Cada ejecución agrega 10 registros nuevos a cada tabla.

WITH usuarios_prueba AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY creado, id) AS n
    FROM usuarios
    WHERE estatus = 'A'
    LIMIT 3
),
cantidad AS (
    SELECT COUNT(*) AS total FROM usuarios_prueba
),
datos (
    orden, minutos_creado, minutos_caducidad, codigo_verificacion, intentos,
    aut_tipo_envio_id, utilizado, direccion_ip, dispositivo, estatus, telefono, email
) AS (
    VALUES
        -- Utilizados (verde)
        (1, -120, -110, '482915', 1, 1, TRUE,  '189.203.10.25',  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36', 'A', NULL, 'usuario1@ejemplo.gob.mx'),
        (2, -90,  -80,  '730184', 0, 2, TRUE,  '201.141.55.8',   'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1', 'A', '8441234567', NULL),
        (3, -60,  -50,  '156749', 3, 3, TRUE,  '187.188.42.99',  'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36', 'A', '8442345678', NULL),
        -- Máx Intentos (rojo): más de 5 intentos
        (4, -45,  -35,  '904271', 6, 1, FALSE, '148.202.77.130', 'Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0', 'A', NULL, 'usuario2@ejemplo.gob.mx'),
        (5, -30,  -20,  '618350', 8, 2, FALSE, '45.231.12.4',    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15', 'A', '8443456789', NULL),
        -- En espera (azul): no utilizados, hasta 5 intentos y con tiempo vigente
        (6, -2,   8,    '327749', 0, 1, FALSE, '189.203.10.25',  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edg/130.0 Safari/537.36', 'A', NULL, 'usuario3@ejemplo.gob.mx'),
        (7, -4,   6,    '851062', 2, 2, FALSE, '201.141.55.8',   'Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Mobile Safari/537.36', 'A', '8444567890', 'usuario1@ejemplo.gob.mx'),
        (8, -1,   9,    '269438', 5, 3, FALSE, '187.188.42.99',  NULL, 'A', '8445678901', NULL),
        -- No utilizado (gris): caducados sin usar
        (9, -300, -290, '573816', 0, 1, FALSE, '148.202.77.130', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36', 'A', NULL, 'usuario2@ejemplo.gob.mx'),
        -- Registro dado de baja (aparece en Inactivos)
        (10, -600, -590, '095527', 1, 2, FALSE, NULL, NULL, 'B', NULL, NULL)
)
INSERT INTO aut_verificaciones_usuarios (
    id, creado, modificado, estatus, usuario_id, codigo_verificacion, tiempo_caducidad,
    intentos, aut_tipo_envio_id, utilizado, direccion_ip, dispositivo, telefono, email
)
SELECT
    gen_random_uuid(),
    CURRENT_TIMESTAMP + d.minutos_creado * INTERVAL '1 minute',
    CURRENT_TIMESTAMP + d.minutos_creado * INTERVAL '1 minute',
    d.estatus,
    u.id,
    d.codigo_verificacion,
    CURRENT_TIMESTAMP + d.minutos_caducidad * INTERVAL '1 minute',
    d.intentos,
    d.aut_tipo_envio_id,
    d.utilizado,
    d.direccion_ip,
    d.dispositivo,
    d.telefono,
    d.email
FROM datos d
JOIN cantidad c ON c.total > 0
JOIN usuarios_prueba u ON u.n = ((d.orden - 1) % c.total) + 1
ORDER BY d.orden;

-- Registros de prueba para `aut_verificaciones_clientes`
WITH clientes_prueba AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY creado, id) AS n
    FROM cit_clientes
    WHERE estatus = 'A'
    LIMIT 3
),
cantidad AS (
    SELECT COUNT(*) AS total FROM clientes_prueba
),
datos (
    orden, minutos_creado, minutos_caducidad, codigo_verificacion, intentos,
    aut_tipo_envio_id, utilizado, direccion_ip, dispositivo, estatus, telefono, email
) AS (
    VALUES
        -- Utilizados (verde)
        (1, -120, -110, '519284', 1, 1, TRUE,  '189.203.10.25',  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36', 'A', NULL, 'cliente1@ejemplo.com'),
        (2, -90,  -80,  '481037', 0, 2, TRUE,  '201.141.55.8',   'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1', 'A', '8711234567', NULL),
        (3, -60,  -50,  '947651', 3, 3, TRUE,  '187.188.42.99',  'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36', 'A', '8712345678', NULL),
        -- Máx Intentos (rojo): más de 5 intentos
        (4, -45,  -35,  '172409', 6, 1, FALSE, '148.202.77.130', 'Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0', 'A', NULL, 'cliente2@ejemplo.com'),
        (5, -30,  -20,  '053816', 8, 2, FALSE, '45.231.12.4',    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15', 'A', '8713456789', NULL),
        -- En espera (azul): no utilizados, hasta 5 intentos y con tiempo vigente
        (6, -2,   8,    '947723', 0, 1, FALSE, '189.203.10.25',  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edg/130.0 Safari/537.36', 'A', NULL, 'cliente3@ejemplo.com'),
        (7, -4,   6,    '260158', 2, 2, FALSE, '201.141.55.8',   'Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Mobile Safari/537.36', 'A', '8714567890', 'cliente1@ejemplo.com'),
        (8, -1,   9,    '834962', 5, 3, FALSE, '187.188.42.99',  NULL, 'A', '8715678901', NULL),
        -- No utilizado (gris): caducados sin usar
        (9, -300, -290, '618375', 0, 1, FALSE, '148.202.77.130', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36', 'A', NULL, 'cliente2@ejemplo.com'),
        -- Registro dado de baja (aparece en Inactivos)
        (10, -600, -590, '725590', 1, 2, FALSE, NULL, NULL, 'B', NULL, NULL)
)
INSERT INTO aut_verificaciones_clientes (
    id, creado, modificado, estatus, cit_cliente_id, codigo_verificacion, tiempo_caducidad,
    intentos, aut_tipo_envio_id, utilizado, direccion_ip, dispositivo, telefono, email
)
SELECT
    gen_random_uuid(),
    CURRENT_TIMESTAMP + d.minutos_creado * INTERVAL '1 minute',
    CURRENT_TIMESTAMP + d.minutos_creado * INTERVAL '1 minute',
    d.estatus,
    u.id,
    d.codigo_verificacion,
    CURRENT_TIMESTAMP + d.minutos_caducidad * INTERVAL '1 minute',
    d.intentos,
    d.aut_tipo_envio_id,
    d.utilizado,
    d.direccion_ip,
    d.dispositivo,
    d.telefono,
    d.email
FROM datos d
JOIN cantidad c ON c.total > 0
JOIN clientes_prueba u ON u.n = ((d.orden - 1) % c.total) + 1
ORDER BY d.orden;
