# Guía de Configuración EC2 — Funcionalidad "Actualizar Tableau DB"

Este documento explica qué se agregó al repositorio y qué hay que hacer en la instancia EC2 para que la nueva funcionalidad "Actualizar Tableau DB" funcione correctamente.

---

## Qué se agregó

Se agregó una nueva opción **"4. Actualizar Tableau DB"** en el sidebar dentro de la opción 5 de la app. Cuando el usuario hace clic en el botón de actualizar, el sistema:

1. Copia 27 tablas desde la base de datos fuente (`198.57.216.119`) a la base de datos AWS RDS
2. Reconstruye la tabla `importador_sales_all`
3. Reconstruye la tabla `isa_table` que lee el dashboard de Tableau

Los archivos nuevos son:
- `apps/app10.py` — interfaz de Streamlit para el botón de actualización
- `src/update_db/update_rds_db.py` — lógica del pipeline
- `.env.rds.example` — plantilla con las variables de entorno necesarias

---

## Pasos de configuración en EC2

### Paso 1 — Pedirle a Max que agregue la IP pública de la instancia EC2
El pipeline se conecta a la base de datos fuente en `198.57.216.119`. La **Public IPv4 address** de la instancia EC2 debe ser agregada a la lista de IPs permitidas por Max (el administrador de la base de datos fuente) antes de que el pipeline pueda ejecutarse.

### Paso 2 — Aprobar RP y luego bajar los últimos cambios
```bash
git pull origin main
```

### Paso 3 — Instalar las nuevas dependencias
```bash
pip install -r requirements.txt
```
Esto agrega `sqlalchemy` y `pymysql`, que son requeridos por la nueva funcionalidad.

### Paso 4 — Crear el archivo `.env.rds`
Este archivo NO está en el repositorio (contiene contraseñas). Crearlo manualmente en la instancia EC2:

```bash
cp .env.rds.example .env.rds
```

Luego abrir `.env.rds` y completar con la contraseña real de RDS:

```
RDS_HOST=guildin-db.cavss468efyn.us-east-1.rds.amazonaws.com
RDS_USER=admin
RDS_PASSWORD=<pedirle la contraseña a Cami>
RDS_DATABASE=gildinglocal
RDS_PORT=3306
```

### Paso 5 — Reiniciar la app
Reiniciar la app de Streamlit para que tome los cambios del nuevo archivo `.env.rds` y el código actualizado.

---

## Notas

- La funcionalidad existente (opciones 1, 2, 3) no fue modificada en absoluto
- La nueva opción 4 solo se activa cuando el usuario la selecciona — no afecta el resto de la app
- El pipeline puede tardar 15+ minutos dependiendo del volumen de datos — esto es esperado
- El dashboard de Tableau tiene una conexión en vivo a RDS, por lo que reflejará los datos nuevos inmediatamente después de que el pipeline finalice
