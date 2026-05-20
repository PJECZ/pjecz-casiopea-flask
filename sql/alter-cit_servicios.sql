-- Archivo SQL para añadir la columna 'instrucciones' a la tabla 'cit_servicios'
-- Fecha: 2026-05-19

ALTER TABLE cit_servicios ADD COLUMN instrucciones VARCHAR(1024);
