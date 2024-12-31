import json

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from uuid import UUID
from jose import jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

from app.database import get_db, redis_client
from app.models import User
from app import schemas

# Load environment variables
load_dotenv()

app = FastAPI()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({"exp": expires})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # Store in Redis with expiration
    redis_client.setex(
        f"token:{token}",
        ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        str(data["sub"])
    )
    return token


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    try:
        # Check if token exists in Redis
        user_id = redis_client.get(f"token:{token}")
        if not user_id:
            raise HTTPException(status_code=401)

        # Convert string user_id to UUID before querying
        user_uuid = UUID(user_id)

        # Verify JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if str(payload["sub"]) != str(user_id):
            raise HTTPException(status_code=401)

        # Query with UUID type
        user = db.query(User).filter(User.id == user_uuid).first()
        if user is None:
            raise HTTPException(status_code=401)

        return user

    except:
        raise HTTPException(status_code=401)


# Endpoints
@app.post("/register", response_model=schemas.UserResponse)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    db_user = User(
        email=user.email,
        password_hash=get_password_hash(user.password),
        first_name=user.first_name,
        last_name=user.last_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/login")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Try to get user from Redis cache first
    cached_user = redis_client.get(f"user:{current_user.id}")

    if cached_user:
        # Return cached data if available
        return json.loads(cached_user)
    # Convert string user_id to UUID before querying
    user_uuid = UUID(current_user.id)

    # If not in cache, get from database
    user = db.query(User).filter(User.id == user_uuid).first()

    # Store in Redis cache for future requests (expire in 1 hour)
    redis_client.setex(
        f"user:{user.id}",
        3600,  # 1 hour in seconds
        json.dumps(user.__dict__)
    )

    return user


@app.put("/me", response_model=schemas.UserResponse)
async def update_user(
        user_update: schemas.UserUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # Update user in database
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()

    # Invalidate cache after update
    redis_client.delete(f"user:{current_user.id}")

    return current_user


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
