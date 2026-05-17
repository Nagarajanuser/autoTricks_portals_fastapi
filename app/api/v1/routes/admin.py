from fastapi import APIRouter, Depends, HTTPException, status
from ....core.database import get_db_cursor
from ..dependencies import get_current_user
from datetime import date

router = APIRouter()

@router.get("/dashboard")
async def get_admin_dashboard(current_user: dict = Depends(get_current_user)):
    user_role = current_user.get("role")
    user_id = current_user.get("user_id")

    if user_role not in ["HR", "Project Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Administrative privileges required."
        )

    conn, cursor = get_db_cursor()
    if not cursor:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        today_str = date.today().strftime("%Y-%m-%d")

        if user_role == "HR":
            # 1. Total Employees Count
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'Employee'")
            total_employees = cursor.fetchone()["count"]

            # 2. Present Today Count
            cursor.execute("SELECT COUNT(*) as count FROM attendance WHERE date = %s AND status = 'Present'", (today_str,))
            present_today = cursor.fetchone()["count"]

            # 3. Pending Leaves Count
            cursor.execute("SELECT COUNT(*) as count FROM leaves WHERE status = 'Pending'")
            pending_leaves = cursor.fetchone()["count"]

            # 4. Total Payroll Disbursed (Sum of all Net Salaries in system)
            cursor.execute("SELECT COALESCE(SUM(net_salary), 0) as total FROM payroll")
            total_payroll = cursor.fetchone()["total"]

            # 5. Recent Leave Applications (with employee name)
            leave_query = """
                SELECT l.id, l.leave_type, l.start_date, l.end_date, l.status, l.reason, ep.full_name
                FROM leaves l
                JOIN users u ON l.user_id = u.id
                JOIN employee_profiles ep ON u.id = ep.user_id
                ORDER BY l.id DESC
                LIMIT 5
            """
            cursor.execute(leave_query)
            recent_leaves = cursor.fetchall()

            # 6. Recent Registered Employees
            employee_query = """
                SELECT u.id, u.username, ep.full_name, ep.email, ep.phone, u.created_at
                FROM users u
                JOIN employee_profiles ep ON u.id = ep.user_id
                WHERE u.role = 'Employee'
                ORDER BY u.id DESC
                LIMIT 5
            """
            cursor.execute(employee_query)
            recent_employees = cursor.fetchall()

            return {
                "role": "HR",
                "stats": {
                    "total_employees": total_employees,
                    "present_today": present_today,
                    "pending_leaves": pending_leaves,
                    "total_payroll": float(total_payroll)
                },
                "recent_leaves": recent_leaves,
                "recent_employees": recent_employees
            }

        elif user_role == "Project Manager":
            # 1. Total Active Projects Count
            cursor.execute("SELECT COUNT(*) as count FROM projects WHERE status = 'Active'")
            active_projects_count = cursor.fetchone()["count"]

            # 2. Total Tasks Count
            cursor.execute("SELECT COUNT(*) as count FROM tasks")
            total_tasks_count = cursor.fetchone()["count"]

            # 3. Pending Tasks Count (To Do or In Progress / not Completed)
            cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE status != 'Completed' AND status != 'Done'")
            pending_tasks_count = cursor.fetchone()["count"]

            # 4. Total Hours Worked Across all projects
            cursor.execute("SELECT COALESCE(SUM(hours_worked), 0) as total FROM timesheets")
            total_hours = cursor.fetchone()["total"]

            # 5. Active Projects List
            projects_query = """
                SELECT id, name, description, start_date, end_date, status 
                FROM projects 
                WHERE status = 'Active' 
                ORDER BY id DESC 
                LIMIT 5
            """
            cursor.execute(projects_query)
            active_projects = cursor.fetchall()

            # 6. Recent Tasks with Project & Assignee Details
            tasks_query = """
                SELECT t.id, t.title, t.status, t.due_date, p.name as project_name, ep.full_name as assigned_to_name
                FROM tasks t
                JOIN projects p ON t.project_id = p.id
                LEFT JOIN users u ON t.assigned_to = u.id
                LEFT JOIN employee_profiles ep ON u.id = ep.user_id
                ORDER BY t.id DESC
                LIMIT 5
            """
            cursor.execute(tasks_query)
            recent_tasks = cursor.fetchall()

            return {
                "role": "Project Manager",
                "stats": {
                    "active_projects": active_projects_count,
                    "total_tasks": total_tasks_count,
                    "pending_tasks": pending_tasks_count,
                    "total_hours": float(total_hours)
                },
                "active_projects_list": active_projects,
                "recent_tasks": recent_tasks
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
    finally:
        cursor.close()
        conn.close()
