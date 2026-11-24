-- 2026-11-23
-- Registros de prueba para la tabla `ban_intentos`: 20 intentos de acceso aleatorios.
-- Cada registro toma al azar una dirección IP (IPv4 e IPv6) y un email (algunos parecen intentos de ataque),
-- de 1 a 10 intentos, con el último intento en los últimos 7 días y cerca del 10% dados de baja (aparecen en Inactivos).
-- ADVERTENCIA: son datos de prueba, no ejecutar en producción. Cada ejecución agrega 20 registros nuevos.

WITH catalogos AS (
    SELECT
        ARRAY[
            '189.203.10.25', '201.141.55.8', '187.188.42.99', '148.202.77.130', '45.231.12.4',
            '177.248.9.61', '200.68.100.17', '2806:2f0:5000:1a2b:3c4d:5e6f:7a8b:9c0d', '2001:db8:85a3::8a2e:370:7334'
        ] AS ips,
        ARRAY[
            'usuario1@ejemplo.gob.mx', 'usuario2@ejemplo.gob.mx', 'usuario3@ejemplo.gob.mx', 'cliente1@ejemplo.com', 'cliente2@ejemplo.com',
            'admin@ejemplo.com', 'root@ejemplo.com', 'test@ejemplo.com', 'no.existe@ejemplo.com', 'prueba.larga.de.correo.electronico@dominio-de-ejemplo.org.mx'
        ] AS emails
),
aleatorios AS (
    SELECT
        g.n,
        CURRENT_TIMESTAMP - (random() * INTERVAL '7 days') AS tiempo,
        1 + floor(random() * 10)::int AS intentos,
        c.ips[1 + floor(random() * array_length(c.ips, 1))::int] AS direccion_ip,
        c.emails[1 + floor(random() * array_length(c.emails, 1))::int] AS email,
        CASE WHEN random() < 0.1 THEN 'B' ELSE 'A' END AS estatus
    FROM generate_series(1, 20) AS g(n)
    CROSS JOIN catalogos c
)
INSERT INTO ban_intentos (creado, modificado, estatus, intentos, tiempo, direccion_ip, email)
SELECT
    tiempo - (random() * INTERVAL '2 hours'),
    tiempo,
    estatus,
    intentos,
    tiempo,
    direccion_ip,
    email
FROM aleatorios
ORDER BY n;
