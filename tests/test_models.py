import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User
from datetime import datetime

# Test database URL (using SQLite for tests)
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture
def test_db():
    # Create test database
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)


def test_create_user(test_db):
    # Test user creation
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="User"
    )
    test_db.add(user)
    test_db.commit()

    # Verify user was created
    db_user = test_db.query(User).filter(User.email == "test@example.com").first()
    assert db_user is not None
    assert db_user.email == "test@example.com"
    assert db_user.first_name == "Test"
    assert db_user.last_name == "User"


def test_user_timestamps(test_db):
    # Test automatic timestamps
    user = User(
        email="time@example.com",
        password_hash="hashed_password"
    )
    test_db.add(user)
    test_db.commit()

    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)


def test_unique_email_constraint(test_db):
    # Test email uniqueness
    user1 = User(email="same@example.com", password_hash="hash1")
    user2 = User(email="same@example.com", password_hash="hash2")

    test_db.add(user1)
    test_db.commit()

    # Adding user with same email should raise an error
    with pytest.raises(Exception):  # SQLAlchemy's IntegrityError
        test_db.add(user2)
        test_db.commit()


def test_nullable_fields(test_db):
    # Test required vs optional fields
    user = User(
        email="minimal@example.com",
        password_hash="hashed_password"
    )
    test_db.add(user)
    test_db.commit()

    db_user = test_db.query(User).filter(User.email == "minimal@example.com").first()
    assert db_user.first_name is None
    assert db_user.last_name is None