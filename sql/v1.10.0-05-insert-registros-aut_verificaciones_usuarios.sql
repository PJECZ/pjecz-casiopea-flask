-- 2026-11-20
-- Registros de prueba para la tabla `aut_verificaciones_usuarios` con variantes en los datos:
-- utilizados, con máximo de intentos, en espera (vigentes) y caducados sin usar.
-- Los usuarios se toman de la tabla `usuarios` (hasta 3 activos, repartidos en rotación)
-- y los tipos de envío de `aut_tipos_envios` (1 = Correo Electrónico, 2 = SMS, 3 = WhatsApp).
-- ADVERTENCIA: son datos de prueba, no ejecutar en producción. Cada ejecución agrega 10 registros nuevos.

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
    aut_tipo_envio_id, utilizado, direccion_ip, dispositivo, estatus
) AS (
    VALUES
        -- Utilizados (verde)
        (1, -120, -110, '482915', 1, 1, TRUE,  '189.203.10.25',  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36', 'A'),
        (2, -90,  -80,  '730184', 0, 2, TRUE,  '201.141.55.8',   'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1', 'A'),
        (3, -60,  -50,  '156749', 3, 3, TRUE,  '187.188.42.99',  'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36', 'A'),
        -- Máx Intentos (rojo): más de 5 intentos
        (4, -45,  -35,  '904271', 6, 1, FALSE, '148.202.77.130', 'Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0', 'A'),
        (5, -30,  -20,  '618350', 8, 2, FALSE, '45.231.12.4',    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15', 'A'),
        -- En espera (azul): no utilizados, hasta 5 intentos y con tiempo vigente
        (6, -2,   8,    '327749', 0, 1, FALSE, '189.203.10.25',  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edg/130.0 Safari/537.36', 'A'),
        (7, -4,   6,    '851062', 2, 2, FALSE, '201.141.55.8',   'Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Mobile Safari/537.36', 'A'),
        (8, -1,   9,    '269438', 5, 3, FALSE, '187.188.42.99',  NULL, 'A'),
        -- No utilizado (gris): caducados sin usar
        (9, -300, -290, '573816', 0, 1, FALSE, '148.202.77.130', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36', 'A'),
        -- Registro dado de baja (aparece en Inactivos)
        (10, -600, -590, '095527', 1, 2, FALSE, NULL, NULL, 'B')
)
INSERT INTO aut_verificaciones_usuarios (
    id, creado, modificado, estatus, usuario_id, codigo_verificacion, tiempo_caducidad,
    intentos, aut_tipo_envio_id, utilizado, direccion_ip, dispositivo
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
    d.dispositivo
FROM datos d
JOIN cantidad c ON c.total > 0
JOIN usuarios_prueba u ON u.n = ((d.orden - 1) % c.total) + 1
ORDER BY d.orden;
