from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from ....core.database import get_db_cursor
from ....core.security import create_access_token
import hashlib

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Assuming basic SHA256 for demo purposes. In production use bcrypt.
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    conn, cursor = get_db_cursor()
    if not cursor:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        query = "SELECT id, username, password_hash, role FROM users WHERE username = %s"
        cursor.execute(query, (request.username,))
        user = cursor.fetchone()

        if not user or not verify_password(request.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Create JWT token
        token_data = {"sub": user["username"], "user_id": user["id"], "role": user["role"]}
        token = create_access_token(data=token_data)

        return LoginResponse(access_token=token)

    finally:
        cursor.close()
        conn.close()
