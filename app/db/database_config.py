import sys
from os import getenv
# from dotenv import load_dotenv
from db.db import Database

# load_dotenv('../../.env')

PSQL_HOST = getenv('PSQL_HOST')
PSQL_PORT = int(getenv('PSQL_PORT'))
PSQL_USER = getenv('PSQL_USER')
PSQL_PASSWORD = getenv('PSQL_PASSWORD')
PSQL_DB = getenv('PSQL_DB')

db = Database(dbname=PSQL_DB, user=PSQL_USER, password=PSQL_PASSWORD, host=PSQL_HOST, port=PSQL_PORT, debug=True)