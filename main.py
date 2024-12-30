from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional

app = FastAPI()


# Pydantic model for request validation
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


# In-memory storage for demo purposes
users_db = {}


@app.post("/register")
async def register(user: UserRegister):
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")

    # In a real application, you would hash the password here
    users_db[user.email] = {
        "email": user.email,
        "password": user.password,  # Don't store plain passwords in production!
        "first_name": user.first_name,
        "last_name": user.last_name
    }

    return {"message": "User registered successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
