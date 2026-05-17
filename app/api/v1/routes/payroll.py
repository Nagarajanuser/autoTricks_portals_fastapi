from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from ....core.database import get_db_cursor
from ..dependencies import get_current_user

router = APIRouter()

class PayrollRecord(BaseModel):
    id: int
    month: int
    year: int
    basic_salary: float
    allowances: float
    deductions: float
    net_salary: float
    status: str

@router.get("/history", response_model=List[PayrollRecord])
async def get_payroll_history(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    conn, cursor = get_db_cursor()
    if not cursor:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        query = "SELECT * FROM payroll WHERE user_id = %s ORDER BY year DESC, month DESC"
        cursor.execute(query, (user_id,))
        records = cursor.fetchall()
        return records
    finally:
        cursor.close()
        conn.close()
