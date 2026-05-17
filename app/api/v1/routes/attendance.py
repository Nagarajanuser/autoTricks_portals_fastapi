from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
from ....core.database import get_db_cursor
from ..dependencies import get_current_user

router = APIRouter()

class AttendanceRecord(BaseModel):
    id: int
    date: date
    check_in: Optional[datetime]
    check_out: Optional[datetime]
    status: str

@router.post("/check-in")
async def check_in(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    today = datetime.now().date()
    now = datetime.now()

    conn, cursor = get_db_cursor()
    if not cursor:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        # Check if already checked in today
        cursor.execute("SELECT id FROM attendance WHERE user_id = %s AND date = %s", (user_id, today))
        existing = cursor.fetchone()

        if existing:
            raise HTTPException(status_code=400, detail="Already checked in today")

        query = "INSERT INTO attendance (user_id, date, check_in, status) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (user_id, today, now, "Present"))
        conn.commit()

        return {"message": "Check-in successful", "check_in_time": now}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/check-out")
async def check_out(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    today = datetime.now().date()
    now = datetime.now()

    conn, cursor = get_db_cursor()
    if not cursor:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        # Get today's record
        cursor.execute("SELECT id, check_out FROM attendance WHERE user_id = %s AND date = %s", (user_id, today))
        existing = cursor.fetchone()

        if not existing:
            raise HTTPException(status_code=400, detail="You must check-in first")
        if existing["check_out"]:
            raise HTTPException(status_code=400, detail="Already checked out today")

        query = "UPDATE attendance SET check_out = %s WHERE id = %s"
        cursor.execute(query, (now, existing["id"]))
        conn.commit()

        return {"message": "Check-out successful", "check_out_time": now}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/history", response_model=List[AttendanceRecord])
async def get_attendance_history(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    conn, cursor = get_db_cursor()
    if not cursor:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        query = "SELECT id, date, check_in, check_out, status FROM attendance WHERE user_id = %s ORDER BY date DESC LIMIT 30"
        cursor.execute(query, (user_id,))
        records = cursor.fetchall()
        return records
    finally:
        cursor.close()
        conn.close()
