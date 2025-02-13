import os
import uuid
import pytest
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from faker import Faker

from main import app
from db.database import get_db

#Chargement des variables d'environnement
load_dotenv()

#variable de connexion à la base de données
POSTGRES_USER = os.getenv('POSTGRES_USER_TEST')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD_TEST')
POSTGRES_DB = os.getenv('POSTGRES_DB_TEST')
POSTGRES_HOST = os.getenv('POSTGRES_HOST_TEST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT_TEST')

fake = Faker("fr_FR") 

#URL de connexion à la base de données
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

#Création de la connexion à la base de données
engine = create_engine(DATABASE_URL, echo=True)

# Create a sessionmaker to manage sessions
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables in the database
SQLModel.metadata.create_all(bind=engine)


def create_db():
    SQLModel.metadata.create_all(engine)
#Création de la base de données
def get_db():
    with Session(engine) as session:
        yield session

create_db()

@pytest.fixture(scope="function")
def db_session():
    """Create a new database session with a rollback at the end of the test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def test_client(db_session):
    """Create a test client that uses the override_get_db fixture to return a session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client



# Fixture to generate a random user id
@pytest.fixture()
def user_id() -> uuid.UUID:
    """Generate a random user id."""
    return str(uuid.uuid4())


# Fixture to generate a user payload
@pytest.fixture()
def user_particulier_payload(user_id):
    """Generate a user payload."""
    return {
        "nom": "Jean",
        "prenom": "michel",
        "email": fake.email(),
        "telephone": "0781648548",
        "role": "particulier", 
        "password": "testpassword*"
    }

@pytest.fixture()
def user_particulier_payload_updated(user_id):
    """Generate an updated user payload."""
    return {
        "nom": "Jean",
        "prenom": "updated",
        "email": "jean-michel-test-updated@cloud.decaweb.fr",
        "telephone": "0781648548",
        "role": "particulier", 
    }

