import configparser
import os

CONFIG_PATH = "config.ini"

config = configparser.ConfigParser()
config.read(CONFIG_PATH)                # si no existe el archivo (p. ej. dentro de Docker), no falla: se usan las variables de entorno


def _read(env_var: str, key: str) -> str:
    """Prioridad: variable de entorno > config.ini. Así, en Docker el secreto no tiene que ir dentro de la imagen."""
    value = os.getenv(env_var) or config.get("JWT", key, fallback=None)
    if value is None:
        raise RuntimeError(f"Missing setting '{key}': set {env_var} or add it to {CONFIG_PATH}")
    return value


SECRET_KEY = _read("JWT_SECRET_KEY", "secret_key")                  # Especialmente importante ser una variable de entorno NO VISIBLE.
ALGORITHM = _read("JWT_ALGORITHM", "algorithm")
ACCESS_TOKEN_EXPIRE_MINUTES = int(_read("JWT_EXP_MINS", "exp_mins"))
