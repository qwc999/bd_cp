from db.connection import get_db_connection


def get_password_by_login(login):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT password FROM workers_pass WHERE login = %s", (login,))
            return cursor.fetchone()
    finally:
        connection.close()


def update_password(login, hashed_password):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE workers_pass SET password = %s WHERE login = %s", (hashed_password, login))
            connection.commit()
    finally:
        connection.close()


def get_user_role_by_login(login):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT position FROM workers
                WHERE worker_id = (
                    SELECT worker_id 
                    FROM workers_pass 
                    WHERE login = %s
                    LIMIT 1
                )
            """, (login,))
            return cursor.fetchone()
    finally:
        connection.close()


def insert_user(name, phone, email):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (name, phone, email) VALUES (%s, %s, %s)",
                (name, phone, email),
            )
            connection.commit()
    finally:
        connection.close()


def get_all_users():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id, name, email FROM users")
            return cursor.fetchall()
    finally:
        connection.close()


def add_new_user(name, login, position):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("CALL add_new_user(%s, %s, %s)", (name, login, position))
            connection.commit()
    finally:
        connection.close()


def delete_user(login):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM workers_pass WHERE login = %s
            """, (login,))
            connection.commit()
            return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        connection.close()
