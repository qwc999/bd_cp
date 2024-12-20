import bcrypt
from db.connection import get_db_connection
from services.user_service import get_password_by_login, update_password


def authenticate(username, password):
    result = get_password_by_login(username)
    if result:
        stored_hash = result[0]
        if stored_hash is None or stored_hash == '':
            return "set_password"
        if bcrypt.checkpw(password.encode(), stored_hash.encode()):
            return True
    return False


def set_password(username, new_password):
    hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    update_password(username, hashed_password)


def get_user_role(username):
    from services.user_service import get_user_role_by_login
    result = get_user_role_by_login(username)
    return result[0] if result else None


def logout():
    import streamlit as st
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None
    st.experimental_set_query_params(authenticated="false")
