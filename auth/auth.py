"""
Módulo de autenticación usando streamlit-authenticator 0.2.3.
Lee los usuarios desde config.yaml y gestiona la sesión de login/logout.
"""

import os

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

CONFIG_PATH = "config.yaml"
COOKIE_NAME = "mmm_guildin_auth"
COOKIE_EXPIRY_DAYS = 30


def _get_cookie_key() -> str:
    key = os.getenv("AUTH_COOKIE_KEY", "")
    if not key:
        st.warning(
            "AUTH_COOKIE_KEY no está configurada en el .env. "
            "Agregala para mayor seguridad.",
            icon="⚠️",
        )
        key = "fallback_insecure_key_please_change"
    return key


def render_login() -> tuple[str | None, bool | None, str | None]:
    """
    Muestra el formulario de login si el usuario no está autenticado.
    Retorna (name, authentication_status, username).

    - authentication_status = True  → autenticado correctamente
    - authentication_status = False → credenciales incorrectas
    - authentication_status = None  → formulario vacío (primer render)
    """
    if not os.path.isfile(CONFIG_PATH):
        st.error(
            f"No se encontró el archivo de credenciales `{CONFIG_PATH}`. "
            "Creá al menos un usuario con `python scripts/create_user.py`."
        )
        st.stop()

    with open(CONFIG_PATH) as f:
        config = yaml.load(f, Loader=SafeLoader)

    if not config.get("credentials", {}).get("usernames"):
        st.error(
            "No hay usuarios configurados. "
            "Creá al menos uno con `python scripts/create_user.py`."
        )
        st.stop()

    authenticator = stauth.Authenticate(
        config["credentials"],
        COOKIE_NAME,
        _get_cookie_key(),
        COOKIE_EXPIRY_DAYS,
    )

    name, authentication_status, username = authenticator.login("Login", "main")

    if authentication_status:
        authenticator.logout("Cerrar sesión", "sidebar")
        st.sidebar.markdown(f"Bienvenido, **{name}**")

    return name, authentication_status, username
