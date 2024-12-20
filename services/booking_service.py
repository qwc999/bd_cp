from db.connection import get_db_connection


def check_booking_availability(room_id, check_in, check_out):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*) FROM bookings
                WHERE room_id = %s AND (
                    (check_in <= %s AND check_out >= %s) OR
                    (check_in <= %s AND check_out >= %s) OR
                    (check_in >= %s AND check_out <= %s)
                )
                """,
                (room_id, check_in, check_in, check_out, check_out, check_in, check_out),
            )
            return cursor.fetchone()[0] == 0
    finally:
        connection.close()


def insert_booking(user_id, room_id, check_in, check_out):
    if not check_booking_availability(room_id, check_in, check_out):
        from streamlit import warning
        warning("The selected room is already booked for the specified period.")
        return

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO bookings (user_id, room_id, check_in, check_out) VALUES (%s, %s, %s, %s)",
                (user_id, room_id, check_in, check_out),
            )
            connection.commit()
    finally:
        connection.close()


def get_all_bookings():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT booking_id, user_id, user_name, user_email, room_id, check_in, check_out, status, days_booked,
                total_bookings_per_user
                FROM detailed_bookings
            """)
            return cursor.fetchall()
    finally:
        connection.close()


def delete_booking(booking_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM bookings WHERE booking_id = %s", (booking_id,))
            connection.commit()
    finally:
        connection.close()
