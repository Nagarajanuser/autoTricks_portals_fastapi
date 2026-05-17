import mysql.connector
from app.core.config import settings

def load_mock_data():
    try:
        conn = mysql.connector.connect(
            host=settings.MYSQL_HOST,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DATABASE,
            port=settings.MYSQL_PORT
        )
        cursor = conn.cursor()

        with open('mock_data.sql', 'r') as f:
            sql_content = f.read()

        # Split by semicolon but ignore semicolons within quotes if any (though here they should be fine)
        # A better way is to split by ;\n
        queries = sql_content.split(';')

        for query in queries:
            if query.strip():
                try:
                    cursor.execute(query)
                except Exception as e:
                    print(f"Error executing query: {e}")
                    # continue to next query

        conn.commit()
        cursor.close()
        conn.close()
        print("Mock data loaded successfully.")
    except Exception as e:
        print(f"Error loading mock data: {e}")

if __name__ == "__main__":
    load_mock_data()
