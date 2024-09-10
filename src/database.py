from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# FIXME Remove the password later (include it as a secret), when this actually matters (app is going to get deployed)
SQLALCHEMY_DATABASE_URL = (
    "postgresql://postgres:mysecretpassword@localhost:5432/postgres"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
