"""
Script de consola para gestionar usuarios en config.yaml.

Uso: python scripts/create_user.py
"""

import os
import sys
import getpass

import bcrypt
import yaml
from yaml.loader import SafeLoader

CONFIG_PATH = "config.yaml"


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def load_config() -> dict:
    if not os.path.isfile(CONFIG_PATH):
        return {"credentials": {"usernames": {}}}
    with open(CONFIG_PATH) as f:
        data = yaml.load(f, Loader=SafeLoader)
    if not data or "credentials" not in data:
        return {"credentials": {"usernames": {}}}
    return data


def save_config(config: dict) -> None:
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


def list_users() -> None:
    config = load_config()
    users = config["credentials"]["usernames"]
    if not users:
        print("No hay usuarios configurados.")
        return
    print(f"{'USERNAME':<20} {'NOMBRE':<30} {'EMAIL'}")
    print("-" * 70)
    for username, data in users.items():
        print(f"{username:<20} {data.get('name', ''):<30} {data.get('email', '')}")


def create_user() -> None:
    print("=== Crear usuario MMM-guildin ===\n")

    name = input("Nombre completo: ").strip()
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    password = getpass.getpass("Contraseña: ")
    confirm = getpass.getpass("Confirmar contraseña: ")

    if not all([name, username, email, password]):
        print("Error: todos los campos son obligatorios.")
        sys.exit(1)

    if password != confirm:
        print("Error: las contraseñas no coinciden.")
        sys.exit(1)

    config = load_config()

    if username in config["credentials"]["usernames"]:
        print(f"Error: el username '{username}' ya existe en {CONFIG_PATH}.")
        sys.exit(1)

    config["credentials"]["usernames"][username] = {
        "name": name,
        "email": email,
        "password": hash_password(password),
    }

    save_config(config)

    print(f"\n✓ Usuario '{username}' agregado a {CONFIG_PATH}.")
    print(f"  git add {CONFIG_PATH} && git commit -m 'add user {username}' && git push")


def delete_user() -> None:
    print("=== Borrar usuario MMM-guildin ===\n")

    config = load_config()
    users = config["credentials"]["usernames"]

    if not users:
        print("No hay usuarios configurados.")
        sys.exit(0)

    print("Usuarios existentes:")
    for username in users:
        print(f"  - {username} ({users[username].get('name', '')})")

    print()
    username = input("Username a borrar: ").strip()

    if username not in users:
        print(f"Error: el username '{username}' no existe.")
        sys.exit(1)

    confirm = input(f"¿Confirmar borrado de '{username}'? (s/n): ").strip().lower()
    if confirm != "s":
        print("Operación cancelada.")
        sys.exit(0)

    del config["credentials"]["usernames"][username]
    save_config(config)

    print(f"\n✓ Usuario '{username}' eliminado de {CONFIG_PATH}.")
    print(f"  git add {CONFIG_PATH} && git commit -m 'remove user {username}' && git push")


def menu() -> None:
    print("=== Gestión de usuarios MMM-guildin ===\n")
    print("  1. Crear usuario")
    print("  2. Borrar usuario")
    print("  3. Listar usuarios")
    print("  4. Salir")
    print()
    choice = input("Seleccioná una opción (1-4): ").strip()

    if choice == "1":
        create_user()
    elif choice == "2":
        delete_user()
    elif choice == "3":
        list_users()
    elif choice == "4":
        sys.exit(0)
    else:
        print("Opción inválida.")
        sys.exit(1)


if __name__ == "__main__":
    menu()
