import sys
#from dotenv import load_dotenv
from app.db.db import Database
from app.configs.config import PSQL_HOST, PSQL_PORT, PSQL_USER, PSQL_PASSWORD, PSQL_DB

#load_dotenv('../../.env')

db = Database(dbname=PSQL_DB, user=PSQL_USER, password=PSQL_PASSWORD, host=PSQL_HOST, port=PSQL_PORT, debug=False)