from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import date
from ....core.database import get_db_cursor
from ..dependencies import get_current_user

router = APIRouter()

class TimesheetRequest(BaseModel):
    project_id: int
    date: date
    hours_worked: float
    description: str

@router.get("/assigned")
async def get_assigned_projects(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    conn, cursor = get_db_cursor()
    if not cursor:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        query = """
            SELECT p.id, p.name, p.description, p.status, pa.role 
            FROM projects p
            JOIN project_assignments pa ON p.id = pa.project_id
            WHERE pa.user_id = %s
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@router.get("/{project_id}/tasks")
async def get_project_tasks(project_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    conn, cursor = get_db_cursor()
    if not cursor:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        # Check if user is assigned to project
        cursor.execute("SELECT role FROM project_assignments WHERE project_id = %s AND user_id = %s", (project_id, user_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=403, detail="Not assigned to this project")
            
        query = "SELECT * FROM tasks WHERE project_id = %s"
        cursor.execute(query, (project_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@router.post("/timesheet")
async def submit_timesheet(request: TimesheetRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    conn, cursor = get_db_cursor()
    if not cursor:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        query = """
            INSERT INTO timesheets (user_id, project_id, date, hours_worked, description)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, request.project_id, request.date, request.hours_worked, request.description))
        conn.commit()
        return {"message": "Timesheet submitted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
