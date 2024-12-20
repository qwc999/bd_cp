from db.connection import get_db_connection


def insert_room(room_number, room_type, price, description):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO rooms (room_number, type, price_per_night, description) 
                VALUES (%s, %s, %s, %s)
                """,
                (room_number, room_type, price, description),
            )
            connection.commit()
    finally:
        connection.close()


def get_all_rooms():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT room_id, room_number, type, price_per_night, status, description FROM rooms")
            return cursor.fetchall()
    finally:
        connection.close()
