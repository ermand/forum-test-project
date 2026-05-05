import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.db_connection.database import Base
from src.models.user import User
from src.models.posts import Post
from src.models.comments import Comment
from src.models.refresh_token import RefreshToken
from core.auth.password import hash_password
from core.auth.jwt import create_access_token


TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def run_ephemeral_test():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        username = "tester_virtual"
        plain_password = "password123"

        hashed_pw = hash_password(plain_password)

        user = User(
            username=username, email="virtual@test.com", password_hash=hashed_pw
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        token = create_access_token(subject=user.username)

        print("\n--- TEST AUTH (IN-MEMORY DB) ---")
        print(f"User krijuar: {user.username}")
        print(f"Email: {user.email}")
        print(f"User ID: {user.id}")

        print("\nTOKEN JWT:")
        print(token)

        print("\n--------------------------------")
        print("Ky user ekziston vetëm në RAM dhe fshihet pas mbylljes së script-it.")
        print("Database reale nuk është prekur.")

    finally:
        db.close()


if __name__ == "__main__":
    run_ephemeral_test()
