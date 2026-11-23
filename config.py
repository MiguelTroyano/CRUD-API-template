import configparser
import os

CONFIG_PATH = "config.ini"

config = configparser.ConfigParser()
config.read(CONFIG_PATH)                # if the file doesn't exist (e.g. inside Docker), it doesn't fail: environment variables are used instead


def _read(env_var: str, key: str) -> str:
    """Priority: environment variable > config.ini. This way, in Docker the secret doesn't have to be inside the image."""
    value = os.getenv(env_var) or config.get("JWT", key, fallback=None)
    if value is None:
        raise RuntimeError(f"Missing setting '{key}': set {env_var} or add it to {CONFIG_PATH}")
    return value


SECRET_KEY = _read("JWT_SECRET_KEY", "secret_key")                  # It's especially important that this is a HIDDEN environment variable.
ALGORITHM = _read("JWT_ALGORITHM", "algorithm")
ACCESS_TOKEN_EXPIRE_MINUTES = int(_read("JWT_EXP_MINS", "exp_mins"))
