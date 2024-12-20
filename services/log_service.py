import os
from datetime import datetime
import pandas as pd
from db.connection import get_db_connection
import streamlit as st


def create_log_archive():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM logs")
            data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            archive_folder = "archive_copies"
            os.makedirs(archive_folder, exist_ok=True)

            file_name = f"logs_archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            file_path = os.path.join(archive_folder, file_name)

            pd.DataFrame(data, columns=columns).to_csv(file_path, index=False)

            st.success(f"Архив логов создан: {file_path}")
    except Exception as e:
        st.error(f"Ошибка при создании архива: {e}")
    finally:
        connection.close()
