import configparser

CONFIG_PATH = "config.ini"

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

SECRET_KEY = config.get("JWT", "secret_key")                   # Especialmente importante ser una variable de entorno NO VISIBLE.
ALGORITHM = config.get("JWT", "algorithm")
ACCESS_TOKEN_EXPIRE_MINUTES = int(config.get("JWT", "exp_mins"))