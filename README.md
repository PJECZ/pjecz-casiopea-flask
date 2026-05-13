# 🏛️ [pjecz-casiopea-flask]

> Aplicación Web para la administración del sitio de Citas del PJECZ con cara al público.
> Proyectos relaccionados:
> - [pjecz-casiopea-api-oauth2](https://github.com/PJECZ/pjecz-casiopea-api-oauth2)
> - [pjecz-casiopea-api-key](https://github.com/PJECZ/pjecz-casiopea-api-key)
> - [pjecz-casiopea-reactjs](https://github.com/PJECZ/pjecz-casiopea-reactjs)

---

## 📋 Tabla de Contenidos
- [Descripción General](#descripción-general)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Requisitos Previos](#requisitos-previos)
- [Instalación y Configuración](#instalación-y-configuración)
- [Estructura de Ramas](#estructura-de-ramas)
- [Despliegue](#despliegue)
- [Contacto](#contacto)

---

## 📖 Descripción General
Es parte de un conjunto de proyecto para otorgar la administración web del sistema de Citas con cara al público. En este sistema podemos administrar las ubicaciones, oficinas, horarios y servicios que otorga el PJECZ en sus diferentes unidades. Además se administra el calendario oficial.

## 🛠️ Tecnologías Utilizadas
* **Lenguaje:** Python 3.14
* **Framework:** Flask
* **Base de Datos:** PostgreSQL
* **Servidor:** Nginx
* **Otros:** Redis

## ⚙️ Requisitos Previos
Lista de herramientas necesarias para correr el proyecto localmente:
- Git
- Python
- uv - manejador de paquetes para Python

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio:
   ```bash
   git clone https://github.com/PJECZ/pjecz-casiopea-flask.git
   cd pjecz-casiopea-flask
   ```

### 2. Configurar variables de entorno:
Copia el archivo de ejemplo y edita las credenciales necesarias (Base de datos, API Keys):
```
cp .env.example .env
```

### 3. Instalar dependencias:
```bash
uv sync
```

### 4. Iniciar el servidor de desarrollo:
```bash
uv run flask run --host=0.0.0.0 --port=5021
```

## 🌿 Estructura de Ramas

Este proyecto sigue el flujo de trabajo institucional:
- `main`: Rama de producción (Solo código estable).
- `dev`: Rama de integración y pruebas (_Staging_).
- `feature/*`: Ramas temporales para nuevas funcionalidades.

Ver más sobre como contribuir: [CONTRIBUTING](CONTRIBUTING.md)

## 🚢 Despliegue

Ejecutar comando en servidor de producción después de haber integrado el PR en la rama `dev`:

```bash
actualizar-proyecto-casiopea
```

## 📥 Migración

1. Extraer un respaldo de la base de datos del sistema anterior `pjecz_citas_v2`.
2. Limpiar el sistema de desarrollo `cli db reiniciar`.
3. Restaurar el respaldo del viejo sistema al sistema de desarrollo en una base de datos espejo y de respaldo llamada igual que la antigua: `pg_restore -d pjecz_citas_v2 --clean --if-exists -v pjecz_citas_v2.tar`
4. Ejecutar el comando de migración `cli migrar copiar`
5. Actualizar viejos registros que no utilizaban códigos QR, para que en lugar de ser `null` sean vacíos
```sql
UPDATE cit_citas SET codigo_acceso_url = '' WHERE codigo_acceso_url IS NULL;
```
6. Eliminar citas pasadas. Ejecutando el comando: `cli cit-citas eliminar`
7. Restablecer un usuario para su acceso al sistema. Ejecute el comando `cli usuarios nueva-contrasena administrado@email.com`

---

## ✉️ Contacto

- **Departamento:** Dirección de Informática - PJECZ
- **Responsable:** Dir. Guillermo Valdés, Lucía Aranda y Ricardo Valdés
- **Email:** [correo@pjecz.gob.mx]

---

© 2026 Poder Judicial del Estado de Coahuila de Zaragoza.
