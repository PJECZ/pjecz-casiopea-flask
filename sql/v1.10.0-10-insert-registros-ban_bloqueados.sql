-- 2026-11-23
-- Registros de prueba para la tabla `ban_bloqueados`: 20 bloqueos con variantes en los datos:
-- solo dirección IP, solo email (cuenta comprometida), ambos, los tres tipos de baneo y algunos dados de baja.
-- Requiere que ya existan los tipos de baneo (`v1.10.0-06-create-ban_tipos.sql`): 'MINUTOS', 'DIA' y 'SIEMPRE'.
-- `minutos_atras` es hace cuántos minutos fue el último acceso.
-- ADVERTENCIA: son datos de prueba, no ejecutar en producción. Cada ejecución agrega 20 registros nuevos.

WITH datos (orden, tipo_clave, minutos_atras, direccion_ip, email, estatus) AS (
    VALUES
        -- Solo dirección IP
        (1,  'MINUTOS', 5,     '189.203.10.25',                            NULL,                                   'A'),
        (2,  'MINUTOS', 12,    '201.141.55.8',                             NULL,                                   'A'),
        (3,  'DIA',     90,    '187.188.42.99',                            NULL,                                   'A'),
        (4,  'DIA',     600,   '148.202.77.130',                           NULL,                                   'A'),
        (5,  'SIEMPRE', 2880,  '45.231.12.4',                              NULL,                                   'A'),
        (6,  'SIEMPRE', 4320,  '177.248.9.61',                             NULL,                                   'A'),
        (7,  'MINUTOS', 30,    '2806:2f0:5000:1a2b:3c4d:5e6f:7a8b:9c0d',   NULL,                                   'A'),
        (8,  'DIA',     1500,  '2001:db8:85a3::8a2e:370:7334',             NULL,                                   'A'),
        -- Solo email (cuenta comprometida)
        (9,  'SIEMPRE', 200,   NULL,                                       'usuario1@ejemplo.gob.mx',              'A'),
        (10, 'SIEMPRE', 7200,  NULL,                                       'cliente1@ejemplo.com',                 'A'),
        (11, 'DIA',     360,   NULL,                                       'cliente2@ejemplo.com',                 'A'),
        (12, 'MINUTOS', 8,     NULL,                                       'usuario2@ejemplo.gob.mx',              'A'),
        (13, 'SIEMPRE', 10080, NULL,                                       'admin@ejemplo.com',                    'A'),
        (14, 'DIA',     45,    NULL,                                       'prueba.larga.de.correo.electronico@dominio-de-ejemplo.org.mx', 'A'),
        -- IP y email a la vez
        (15, 'MINUTOS', 3,     '200.68.100.17',                            'root@ejemplo.com',                     'A'),
        (16, 'DIA',     720,   '189.203.10.26',                            'test@ejemplo.com',                     'A'),
        (17, 'SIEMPRE', 5760,  '45.231.12.5',                              'no.existe@ejemplo.com',                'A'),
        -- Dados de baja (aparecen en Inactivos)
        (18, 'MINUTOS', 2000,  '201.141.55.9',                             NULL,                                   'B'),
        (19, 'DIA',     3000,  NULL,                                       'usuario3@ejemplo.gob.mx',              'B'),
        (20, 'SIEMPRE', 9000,  '148.202.77.131',                           'cliente3@ejemplo.com',                 'B')
)
INSERT INTO ban_bloqueados (creado, modificado, estatus, ban_tipo_id, tiempo, direccion_ip, email)
SELECT
    CURRENT_TIMESTAMP - (d.minutos_atras + 60) * INTERVAL '1 minute',
    CURRENT_TIMESTAMP - d.minutos_atras * INTERVAL '1 minute',
    d.estatus,
    t.id,
    CURRENT_TIMESTAMP - d.minutos_atras * INTERVAL '1 minute',
    d.direccion_ip,
    d.email
FROM datos AS d
JOIN ban_tipos AS t ON t.clave = d.tipo_clave
ORDER BY d.orden;
