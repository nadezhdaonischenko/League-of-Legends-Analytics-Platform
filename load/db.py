import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DB_USER = "postgres" 
DB_PASSWORD = os.getenv("parole_postgresql", "")
DB_HOST = "localhost" 
DB_PORT = "5432" 
DB_NAME = "lol_db"

engine = create_engine(
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
