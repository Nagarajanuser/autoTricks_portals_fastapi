import hashlib
from app.core.database import get_db_cursor

def seed_admin_data():
    conn, cursor = get_db_cursor()
    if not cursor:
        print("Database connection failed")
        return

    try:
        # Password for all users will be 'password'
        password_plain = "password"
        password_hash = hashlib.sha256(password_plain.encode()).hexdigest()

        # Seed 3 HR users
        hr_users = [
            ("hr1", "Alice HR", "alice.hr@autotricks.com", "555-9001"),
            ("hr2", "Bob HR", "bob.hr@autotricks.com", "555-9002"),
            ("hr3", "Charlie HR", "charlie.hr@autotricks.com", "555-9003")
        ]

        print("Seeding HR Users...")
        for username, full_name, email, phone in hr_users:
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            exists = cursor.fetchone()
            if not exists:
                # Insert into users
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, 'HR')",
                    (username, password_hash)
                )
                user_id = cursor.lastrowid
                
                # Insert into employee_profiles
                cursor.execute(
                    "INSERT INTO employee_profiles (user_id, full_name, email, phone) VALUES (%s, %s, %s, %s)",
                    (user_id, full_name, email, phone)
                )
                print(f"Created HR User: {username}")
            else:
                print(f"HR User {username} already exists.")

        # Seed 10 Project Managers
        pm_users = [
            ("pm1", "Manager One", "pm1@autotricks.com", "555-8001"),
            ("pm2", "Manager Two", "pm2@autotricks.com", "555-8002"),
            ("pm3", "Manager Three", "pm3@autotricks.com", "555-8003"),
            ("pm4", "Manager Four", "pm4@autotricks.com", "555-8004"),
            ("pm5", "Manager Five", "pm5@autotricks.com", "555-8005"),
            ("pm6", "Manager Six", "pm6@autotricks.com", "555-8006"),
            ("pm7", "Manager Seven", "pm7@autotricks.com", "555-8007"),
            ("pm8", "Manager Eight", "pm8@autotricks.com", "555-8008"),
            ("pm9", "Manager Nine", "pm9@autotricks.com", "555-8009"),
            ("pm10", "Manager Ten", "pm10@autotricks.com", "555-8010")
        ]

        print("\nSeeding Project Manager Users...")
        for username, full_name, email, phone in pm_users:
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            exists = cursor.fetchone()
            if not exists:
                # Insert into users
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, 'Project Manager')",
                    (username, password_hash)
                )
                user_id = cursor.lastrowid
                
                # Insert into employee_profiles
                cursor.execute(
                    "INSERT INTO employee_profiles (user_id, full_name, email, phone) VALUES (%s, %s, %s, %s)",
                    (user_id, full_name, email, phone)
                )
                print(f"Created PM User: {username}")
            else:
                print(f"PM User {username} already exists.")

        conn.commit()
        print("\nAll mock admin and manager data seeded successfully!")

    except Exception as e:
        print(f"Error seeding data: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_admin_data()
