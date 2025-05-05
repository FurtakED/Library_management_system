from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base, engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import pytest
from app.crud import create_user
from app.schemas import UserCreate

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_register_user(setup_database):
    response = client.post(
        "/users/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_login_user(setup_database):
    client.post(
        "/users/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"}
    )
    response = client.post(
        "/users/login",
        data={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_create_book(setup_database):
    # Create admin user directly in the database
    db = TestingSessionLocal()
    admin_user = create_user(
        db,
        UserCreate(username="admin", email="admin@example.com", password="password123")
    )
    admin_user.is_admin = True
    db.commit()
    db.close()

    login_response = client.post(
        "/users/login",
        data={"username": "admin", "password": "password123"}
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.json()}"
    token = login_response.json()["access_token"]
    
    response = client.post(
        "/books/",
        json={"title": "Test Book", "author": "Test Author", "isbn": "1234567890", "publication_year": 2020},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, f"Create book failed: {response.json()}"
    assert response.json()["title"] == "Test Book"

def test_get_books(setup_database):
    response = client.get("/books/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_borrow_book(setup_database):
    # Create regular user
    client.post(
        "/users/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"}
    )
    
    # Create admin user directly in the database
    db = TestingSessionLocal()
    admin_user = create_user(
        db,
        UserCreate(username="admin", email="admin@example.com", password="password123")
    )
    admin_user.is_admin = True
    db.commit()
    db.close()

    admin_login = client.post(
        "/users/login",
        data={"username": "admin", "password": "password123"}
    )
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    
    book_response = client.post(
        "/books/",
        json={"title": "Test Book", "author": "Test Author", "isbn": "1234567890", "publication_year": 2020},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert book_response.status_code == 200
    
    user_login = client.post(
        "/users/login",
        data={"username": "testuser", "password": "password123"}
    )
    assert user_login.status_code == 200
    user_token = user_login.json()["access_token"]
    
    response = client.post(
        "/borrows/",
        json={"user_id": 1, "book_id": book_response.json()["id"]},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["user_id"] == 1

def test_recommendations(setup_database):
    # Create users directly in the database
    db = TestingSessionLocal()
    test_user = create_user(
        db,
        UserCreate(username="testuser", email="test@example.com", password="password123")
    )
    admin_user = create_user(
        db,
        UserCreate(username="admin", email="admin@example.com", password="password123")
    )
    admin_user.is_admin = True
    db.commit()
    db.close()

    # Login admin and create books
    admin_login = client.post(
        "/users/login",
        data={"username": "admin", "password": "password123"}
    )
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    
    client.post(
        "/books/",
        json={"title": "Book 1", "author": "Author 1", "isbn": "1234567890", "publication_year": 2020},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    client.post(
        "/books/",
        json={"title": "Book 2", "author": "Author 2", "isbn": "0987654321", "publication_year": 2021},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Login user and borrow book
    user_login = client.post(
        "/users/login",
        data={"username": "testuser", "password": "password123"}
    )
    assert user_login.status_code == 200
    user_token = user_login.json()["access_token"]
    
    client.post(
        "/borrows/",
        json={"user_id": 1, "book_id": 1},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    # Get recommendations
    response = client.get(
        "/recommendations/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)