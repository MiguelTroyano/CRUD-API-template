import configparser
import os

CONFIG_PATH = "config.ini"

config = configparser.ConfigParser()
config.read(CONFIG_PATH)                # si no existe el archivo (p. ej. dentro de Docker), no falla: se usan las variables de entorno


def _leer(variable_entorno: str, clave: str) -> str:
    """Prioridad: variable de entorno > config.ini. Así, en Docker el secreto no tiene que ir dentro de la imagen."""
    valor = os.getenv(variable_entorno) or config.get("JWT", clave, fallback=None)
    if valor is None:
        raise RuntimeError(f"Falta la configuración '{clave}': define {variable_entorno} o añádela a {CONFIG_PATH}")
    return valor


SECRET_KEY = _leer("JWT_SECRET_KEY", "secret_key")                  # Especialmente importante ser una variable de entorno NO VISIBLE.
ALGORITHM = _leer("JWT_ALGORITHM", "algorithm")
ACCESS_TOKEN_EXPIRE_MINUTES = int(_leer("JWT_EXP_MINS", "exp_mins"))
