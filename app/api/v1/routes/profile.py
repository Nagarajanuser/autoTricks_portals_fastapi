from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from ....core.database import get_db_cursor
from ..dependencies import get_current_user

router = APIRouter()

class ProfileUpdate(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    aadhaar_number: Optional[str] = None
    pan_number: Optional[str] = None
    bank_account: Optional[str] = None
    bank_ifsc: Optional[str] = None

class ProfileResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    aadhaar_number: Optional[str] = None
    pan_number: Optional[str] = None
    bank_account: Optional[str] = None
    bank_ifsc: Optional[str] = None

@router.get("/", response_model=ProfileResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    conn, cursor = get_db_cursor()
    if not cursor:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        # Fetch the employee profile
        query = "SELECT * FROM employee_profiles WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        profile = cursor.fetchone()

        # If profile doesn't exist, create a default one automatically
        if not profile:
            insert_query = """
                INSERT INTO employee_profiles (user_id, full_name, email) 
                VALUES (%s, %s, %s)
            """
            # Fallback values from user token
            username = current_user.get("sub")
            full_name = username.capitalize() if username else "Employee"
            email = f"{username}@autotricks.com" if username else "employee@autotricks.com"
            
            cursor.execute(insert_query, (user_id, full_name, email))
            conn.commit()

            # Retrieve the newly created profile
            cursor.execute(query, (user_id,))
            profile = cursor.fetchone()

        return profile

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.put("/", response_model=ProfileResponse)
async def update_profile(request: ProfileUpdate, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    conn, cursor = get_db_cursor()
    if not cursor:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        # Check if profile exists first
        check_query = "SELECT id FROM employee_profiles WHERE user_id = %s"
        cursor.execute(check_query, (user_id,))
        exists = cursor.fetchone()

        if not exists:
            # If not exist, insert first
            insert_query = """
                INSERT INTO employee_profiles 
                (user_id, full_name, email, phone, address, aadhaar_number, pan_number, bank_account, bank_ifsc) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                user_id, request.full_name, request.email, request.phone, request.address,
                request.aadhaar_number, request.pan_number, request.bank_account, request.bank_ifsc
            ))
        else:
            # Update existing
            update_query = """
                UPDATE employee_profiles 
                SET full_name = %s, email = %s, phone = %s, address = %s, 
                    aadhaar_number = %s, pan_number = %s, bank_account = %s, bank_ifsc = %s
                WHERE user_id = %s
            """
            cursor.execute(update_query, (
                request.full_name, request.email, request.phone, request.address,
                request.aadhaar_number, request.pan_number, request.bank_account, request.bank_ifsc,
                user_id
            ))
        
        conn.commit()

        # Fetch the updated profile to return
        query = "SELECT * FROM employee_profiles WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        updated_profile = cursor.fetchone()
        return updated_profile

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()
