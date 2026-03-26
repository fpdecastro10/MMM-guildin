# MMM-guildin

> Plataforma de análisis de marketing (MMM) construida con Streamlit y deployada en AWS EC2.

Incluye múltiples aplicaciones para predicción de ventas, distribución de budget, análisis de tendencias y administración de base de datos.

---

## Tabla de contenidos

- [Requisitos previos](#requisitos-previos)
- [Variables de entorno](#variables-de-entorno)
- [Correr con Docker](#correr-con-docker)
- [Usuarios y login](#usuarios-y-login)
- [Setup en EC2](#setup-en-ec2)
- [Estructura del proyecto](#estructura-del-proyecto)

---

## Requisitos previos

- Python 3.11
- Docker

---

## Variables de entorno

El proyecto usa dos archivos de entorno. **Ninguno se commitea al repo.**

<details>
<summary><code>.env</code> — credenciales MySQL</summary>

```env
HOSTS=<host MySQL>
USERS=<usuario MySQL>
PWDS=<contraseña MySQL>
NAME_DATABASES=<nombre de la base de datos>
PORTS=3306
PYTHONPATH=.
AUTH_COOKIE_KEY=<string secreto para las cookies de sesión>
```

`AUTH_COOKIE_KEY` puede ser cualquier string largo y aleatorio:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

</details>

<details>
<summary><code>.env.rds</code> — credenciales AWS RDS</summary>

```env
RDS_HOST=guildin-db.cavss468efyn.us-east-1.rds.amazonaws.com
RDS_USER=admin
RDS_PASSWORD=<contraseña RDS — pedirle a Cami>
RDS_DATABASE=gildinglocal
RDS_PORT=3306
```

</details>

---

## Correr con Docker

```bash
# Buildear la imagen
docker build -t mmm-guildin .

# Correr el contenedor
docker run -p 8501:8501 --env-file .env mmm-guildin
```

La app queda disponible en [http://localhost:8501](http://localhost:8501)

---

## Usuarios y login

Los usuarios se guardan en `config.yaml` (commiteado en el repo). Las contraseñas se almacenan como **hashes bcrypt** — nunca en texto plano.

```bash
python scripts/create_user.py
```

El script presenta un menú interactivo para **crear**, **borrar** o **listar** usuarios.

Después de cualquier cambio, hay que commitearlo para que se refleje en el servidor:

```bash
git add config.yaml && git commit -m "update users" && git push
```

---

## Setup en EC2

Pasos a seguir en la instancia EC2 al deployar una versión nueva.

| # | Paso | Comando |
|---|---|---|
| 1 | Bajar los cambios | `git pull origin main` |
| 2 | Instalar dependencias | `pip install -r requirements.txt` |
| 3 | Crear `.env.rds` | Ver sección [Variables de entorno](#variables-de-entorno) |
| 4 | Reiniciar la app | Reiniciar el proceso de Streamlit |

**Whitelist de IP:** La funcionalidad "Actualizar Tableau DB" se conecta a `198.57.216.119`. La **Public IPv4** de la instancia EC2 debe estar habilitada — pedírselo a **Max**.

> **Nota:** El pipeline de actualización puede tardar 15+ minutos. Tableau tiene conexión en vivo a RDS y reflejará los datos nuevos al instante.

---

## Estructura del proyecto

```
MMM-guildin/
├── main.py                   # Entry point — login + router de apps
├── config.yaml               # Usuarios y hashes bcrypt (commiteado)
├── .env                      # Credenciales MySQL          (NO commiteado)
├── .env.rds                  # Credenciales AWS RDS        (NO commiteado)
│
├── auth/
│   └── auth.py               # Login con streamlit-authenticator
│
├── apps/
│   ├── app1.py               # Predicción de sales — regresión polinomial
│   ├── app3_4.py             # Tendencia de ventas en stores
│   ├── app5.py               # Inversión inicial y distribución de budget
│   ├── app6.py               # Predicción de sales + analytics MMM
│   ├── app10.py              # Actualizar Tableau DB
│   └── app789.py             # Actualización de DB, períodos y entrenamiento
│
├── src/
│   ├── commons/functions.py  # Utilidades compartidas de ML
│   ├── update_db/            # Sync MySQL → SQLite / RDS
│   └── mmm_shap.py           # Motor MMM + SHAP
│
├── models/                   # Modelos entrenados (.pkl) y datasets por store group
├── datasets/                 # CSVs pre-generados para las apps
├── scripts/
│   └── create_user.py        # CLI para gestionar usuarios
│
├── Dockerfile
└── requirements.txt
```
