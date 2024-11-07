from os import getenv

API_TOKEN = getenv('TG_API_TOKEN')
DEBUG = bool(getenv('DEBUG'))

PSQL_HOST = getenv('PSQL_HOST')
PSQL_PORT = int(getenv('PSQL_PORT'))
PSQL_USER = getenv('PSQL_USER')
PSQL_PASSWORD = getenv('PSQL_PASSWORD')
PSQL_DB = getenv('PSQL_DB')