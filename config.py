import configparser
import os

CONFIG_PATH = "config.ini"

config = configparser.ConfigParser()
config.read(CONFIG_PATH)                # a missing file is fine: environment variables are used instead


def _read(env_var: str, key: str) -> str:
    """Return a setting from its environment variable, falling back to config.ini."""
    value = os.getenv(env_var) or config.get("JWT", key, fallback=None)
    if value is None:
        raise RuntimeError(f"Missing setting '{key}': set {env_var} or add it to {CONFIG_PATH}")
    return value


SECRET_KEY = _read("JWT_SECRET_KEY", "secret_key")
ALGORITHM = _read("JWT_ALGORITHM", "algorithm")
ACCESS_TOKEN_EXPIRE_MINUTES = int(_read("JWT_EXP_MINS", "exp_mins"))
