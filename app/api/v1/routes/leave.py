from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import date
from ....core.database import get_db_cursor
from ..dependencies import get_current_user

router = APIRouter()

class LeaveApplyRequest(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    reason: str

class LeaveRecord(BaseModel):
    id: int
    leave_type: str
    start_date: date
    end_date: date
    status: str
    reason: str

@router.post("/apply")
async def apply_leave(request: LeaveApplyRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")

    if request.start_date > request.end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date")

    conn, cursor = get_db_cursor()
    if not cursor:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        query = """
            INSERT INTO leaves (user_id, leave_type, start_date, end_date, status, reason)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, request.leave_type, request.start_date, request.end_date, 'Pending', request.reason))
        conn.commit()

        return {"message": "Leave application submitted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/history", response_model=List[LeaveRecord])
async def get_leave_history(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    conn, cursor = get_db_cursor()
    if not cursor:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        query = "SELECT id, leave_type, start_date, end_date, status, reason FROM leaves WHERE user_id = %s ORDER BY start_date DESC"
        cursor.execute(query, (user_id,))
        records = cursor.fetchall()
        return records
    finally:
        cursor.close()
        conn.close()

@router.get("/balance")
async def get_leave_balance(current_user: dict = Depends(get_current_user)):
    # Mocking leave balance for now. In a real app, this would be calculated from the DB.
    return {
        "casual_leave": 5,
        "sick_leave": 3,
        "earned_leave": 12,
        "total_available": 20
    }
