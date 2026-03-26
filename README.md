# MMM-guildin

Plataforma de análisis de marketing (MMM) construida con Streamlit. Incluye múltiples aplicaciones para predicción de ventas, distribución de budget, análisis de tendencias y administración de la base de datos.

---

## Requisitos previos

- Python 3.11
- Docker (opcional, para correr en contenedor)
- Acceso al servidor MySQL (`HOSTS`, `USERS`, `PWDS`, etc.)

---

## Variables de entorno

Crear un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```
HOSTS=<host del servidor MySQL>
USERS=<usuario MySQL>
PWDS=<contraseña MySQL>
NAME_DATABASES=<nombre de la base de datos>
PORTS=3306
PYTHONPATH=.
AUTH_COOKIE_KEY=<string secreto para las cookies de sesión>
```

> `AUTH_COOKIE_KEY` puede ser cualquier string aleatorio y largo. Se usa para firmar las cookies de login.


---

## Correr con Docker

```bash
# 1. Buildear la imagen
docker build -t mmm-guildin .

# 2. Correr el contenedor
docker run -p 8501:8501 --env-file .env mmm-guildin
```

La app queda disponible en [http://localhost:8501](http://localhost:8501)

---

## Crear y administrar usuarios

Los usuarios se guardan en `config.yaml`, commiteado en el repo. Las contraseñas se almacenan como hashes bcrypt — nunca en texto plano.

**Agregar un usuario:**

```bash
python scripts/create_user.py
```

El script pide nombre, username, email y contraseña, genera el hash bcrypt y lo escribe en `config.yaml`. Después hay que commitearlo para que el cambio se refleje en el servidor:

```bash
git add config.yaml
git commit -m "add user nombre"
git push
```

---

## Estructura del proyecto

```
MMM-guildin/
├── main.py                  # Entry point — login + router de apps
├── config.yaml              # Credenciales de usuarios (hashes bcrypt)
├── auth/
│   └── auth.py              # Lógica de autenticación (streamlit-authenticator)
├── apps/
│   ├── app1.py              # Predicción de sales — regresión polinomial
│   ├── app3_4.py            # Tendencia de ventas en stores
│   ├── app5.py              # Inversión inicial y distribución de budget
│   ├── app6.py              # Predicción de sales + analytics MMM
│   └── app789.py            # Actualización de DB, períodos y entrenamiento
├── src/
│   ├── commons/functions.py # Utilidades compartidas de ML
│   ├── update_db/           # Sync MySQL → SQLite
│   └── mmm_shap.py          # Motor de MMM + SHAP
├── models/                  # Modelos entrenados (.pkl) y datasets por store group
├── datasets/                # CSVs pre-generados para las apps
├── scripts/
│   └── create_user.py       # CLI para crear usuarios en MySQL
├── spec/login/spec.md       # Especificación del sistema de login
├── Dockerfile
└── requirements.txt
```