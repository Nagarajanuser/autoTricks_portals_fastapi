import random
import hashlib
from datetime import datetime, timedelta, date

# Number of users
NUM_USERS = 50

# Helper to generate a hash
def get_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

sql_statements = []

sql_statements.append("-- ============================================")
sql_statements.append("-- AutoTricks Employee Portal Mock Data")
sql_statements.append("-- Run this script in your MySQL client")
sql_statements.append("-- ============================================\n")

sql_statements.append("USE autotricks_db;\n")
sql_statements.append("SET FOREIGN_KEY_CHECKS = 0;")
sql_statements.append("TRUNCATE TABLE timesheets;")
sql_statements.append("TRUNCATE TABLE tasks;")
sql_statements.append("TRUNCATE TABLE project_assignments;")
sql_statements.append("TRUNCATE TABLE projects;")
sql_statements.append("TRUNCATE TABLE payroll;")
sql_statements.append("TRUNCATE TABLE leaves;")
sql_statements.append("TRUNCATE TABLE attendance;")
sql_statements.append("TRUNCATE TABLE employee_profiles;")
sql_statements.append("TRUNCATE TABLE users;")
sql_statements.append("SET FOREIGN_KEY_CHECKS = 1;\n")

# 1. Generate Users & Profiles
print(f"Generating {NUM_USERS} users...")
first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

user_ids = list(range(1, NUM_USERS + 1))
password_hash = get_hash('password')

# Generate the specific user `johndoe` as ID 1
sql_statements.append(f"INSERT INTO users (id, username, password_hash, role) VALUES (1, 'johndoe', '{password_hash}', 'Employee');")
sql_statements.append(f"INSERT INTO employee_profiles (user_id, full_name, email, phone) VALUES (1, 'John Doe', 'johndoe@autotricks.com', '555-0100');")

for i in range(2, NUM_USERS + 1):
    fname = random.choice(first_names)
    lname = random.choice(last_names)
    username = f"{fname.lower()}.{lname.lower()}{i}"
    
    sql_statements.append(f"INSERT INTO users (id, username, password_hash, role) VALUES ({i}, '{username}', '{password_hash}', 'Employee');")
    sql_statements.append(f"INSERT INTO employee_profiles (user_id, full_name, email, phone) VALUES ({i}, '{fname} {lname}', '{username}@autotricks.com', '555-{random.randint(1000, 9999)}');")

sql_statements.append("\n")

# 2. Generate Projects
print("Generating Projects...")
projects = [
    (1, "AutoTricks NextGen UI", "Revamping the main user interface", "2025-01-01", "2026-12-31"),
    (2, "Cloud Migration Strategy", "Migrating legacy servers to AWS", "2024-06-01", "2026-08-30"),
    (3, "AI Driven Analytics", "Building predictive models for sales", "2025-10-01", "2027-05-01")
]
for p in projects:
    sql_statements.append(f"INSERT INTO projects (id, name, description, start_date, end_date, status) VALUES ({p[0]}, '{p[1]}', '{p[2]}', '{p[3]}', '{p[4]}', 'Active');")

sql_statements.append("\n")

# 3. Project Assignments & Tasks
print("Generating Assignments & Tasks...")
for u_id in user_ids:
    assigned_proj = random.sample([1, 2, 3], random.randint(1, 2))
    for p_id in assigned_proj:
        sql_statements.append(f"INSERT INTO project_assignments (project_id, user_id, role) VALUES ({p_id}, {u_id}, 'Developer');")
        # Add 2 tasks per user per project
        for t in range(2):
            due_date = date.today() + timedelta(days=random.randint(5, 60))
            sql_statements.append(f"INSERT INTO tasks (project_id, assigned_to, title, status, due_date) VALUES ({p_id}, {u_id}, 'Task {t+1} for User {u_id}', 'To Do', '{due_date}');")

sql_statements.append("\n")

# 4. Generate History (Attendance, Payroll, Timesheets)
print("Generating History (this might take a second)...")
today = date.today()

for u_id in user_ids:
    # Random tenure between 1 to 10 years
    tenure_years = random.randint(1, 10)
    join_date = today - timedelta(days=tenure_years * 365)
    
    # Generate last 12 months of payroll
    base_salary = random.randint(50000, 120000) / 12
    for m in range(12):
        pay_date = today - timedelta(days=m * 30)
        net = base_salary - (base_salary * 0.15) # 15% deductions
        sql_statements.append(f"INSERT INTO payroll (user_id, month, year, basic_salary, deductions, net_salary) VALUES ({u_id}, {pay_date.month}, {pay_date.year}, {base_salary:.2f}, {base_salary * 0.15:.2f}, {net:.2f});")

    # Generate last 30 days of attendance and timesheets
    for d in range(30):
        current_date = today - timedelta(days=d)
        if current_date.weekday() < 5: # Monday to Friday
            # Attendance
            check_in = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=9, minutes=random.randint(0, 30))
            check_out = check_in + timedelta(hours=random.randint(8, 9))
            sql_statements.append(f"INSERT INTO attendance (user_id, date, check_in, check_out, status) VALUES ({u_id}, '{current_date}', '{check_in}', '{check_out}', 'Present');")
            
            # Timesheet
            sql_statements.append(f"INSERT INTO timesheets (user_id, project_id, date, hours_worked, description) VALUES ({u_id}, {random.choice([1,2,3])}, '{current_date}', 8.0, 'Worked on assigned tasks');")

# Write to file
with open("mock_data.sql", "w") as f:
    f.write("\n".join(sql_statements))

print("Successfully generated mock_data.sql!")
