import streamlit as st
from services.auth_service import authenticate, set_password, get_user_role, logout
from services.user_service import insert_user, get_all_users, add_new_user, get_user_role_by_login, delete_user
from services.booking_service import insert_booking, get_all_bookings, delete_booking
from services.room_service import insert_room, get_all_rooms
from services.log_service import create_log_archive
import pandas as pd


def main():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.role = None

    if st.session_state.authenticated:
        st.sidebar.button("Logout", on_click=logout)
        st.sidebar.write(f"Welcome, {st.session_state.username}!")
        st.sidebar.write(f"Role: {st.session_state.role}")

        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
            "New guest", "View all users", "New Booking", "View all bookings", "New Room",
            "View all rooms", 'Add worker', 'Archive'
        ])

        with tab1:
            st.header("Add new guest")
            name = st.text_input("Name")
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            if st.button("Add Guest"):
                insert_user(name, phone, email)
                st.success("User created successfully!")

        with tab2:
            st.header("View all users")
            if st.button("Refresh Data") or "df_users" not in st.session_state:
                st.session_state.df_users = pd.DataFrame(get_all_users(), columns=["ID", "Name", "Email"])
            st.dataframe(st.session_state.df_users, hide_index=True)

        with tab3:
            st.header("Add new booking")
            user_id = st.number_input("User ID", min_value=1)
            room_id = st.number_input("Room ID", min_value=1)
            check_in = st.date_input("Check-in Date")
            check_out = st.date_input("Check-out Date")
            if st.button("Add Booking"):
                insert_booking(user_id, room_id, check_in, check_out)
                st.success("Booking created successfully!")

            st.header("Delete Booking")
            booking_id = st.number_input("Booking ID", min_value=1)
            if st.button("Delete Booking"):
                delete_booking(booking_id)
                st.success(f"Booking has been deleted.")

        with tab4:
            st.header("View all bookings")
            if st.button("Refresh Data", key="refresh_bookings") or "df_bookings" not in st.session_state:
                st.session_state.df_bookings = pd.DataFrame(
                    get_all_bookings(),
                    columns=["ID", "User ID", "User Name", "User Email", "Room", "Check-in", "Check-out", "Status",
                             "Days Booked", "Total bookings of user"]
                )
            st.dataframe(st.session_state.df_bookings, hide_index=True)

        with tab5:
            st.header("Add Room")
            room_number = st.number_input("Room Number", min_value=1)
            room_type = st.selectbox("Room Type", ["single", "double", "family"])
            price = st.number_input("Price per Night", min_value=0)
            description = st.text_area("Description")
            if st.button("Add Room"):
                insert_room(room_number, room_type, price, description)
                st.success("Room added successfully!")

        with tab6:
            st.header("View all rooms")
            if st.button("Refresh Data", key="refresh_rooms") or "df_rooms" not in st.session_state:
                st.session_state.df_rooms = pd.DataFrame(get_all_rooms(), columns=["ID", "Number", 'Type', 'Price',
                                                                                   'Status', 'Description'])
            st.dataframe(st.session_state.df_rooms, hide_index=True)

        with tab7:
            if st.session_state.role == "admin":
                st.header("Add User")
                name = st.text_input("Name", key="add_user_name")
                add_login = st.text_input("Login", key="add_user_login")
                position = st.selectbox(
                    "Position", ["receptionist", "manager", "admin"], key="add_user_position"
                )
                if st.button("Create User", key="add_user_button"):
                    if add_new_user(name, add_login, position):
                        st.success("User has been added successfully.")

                st.header("Delete User")
                delete_login = st.text_input("Login to delete", key="delete_user_login")
                if st.button("Delete User"):
                    if not delete_login:
                        st.warning("Please enter a login.")
                    else:
                        role = get_user_role_by_login(delete_login)
                        if role:
                            role = role[0]
                            if role != 'admin':
                                if delete_user(delete_login):
                                    st.success("User has been deleted successfully.")
                                else:
                                    st.error("Failed to delete the user. Please try again.")
                            else:
                                st.warning("Admin user cannot be deleted.")

            else:
                st.warning("Access restricted: This tab is available to administrators only.")

        with tab8:
            if st.session_state.role == "admin":
                st.header("Create Logs Archive")
                if st.button("Create Archive"):
                    create_log_archive()
            else:
                st.warning("Access restricted: This tab is available to administrators only.")

    else:
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            auth_result = authenticate(username, password)
            if auth_result == "set_password":
                set_password(username, password)
                st.success("Password set successfully!")
            elif auth_result:
                role = get_user_role(username)
                if role:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.role = role
                    st.experimental_set_query_params(authenticated="true")
                else:
                    st.error("Failed to retrieve user role.")
            else:
                st.error("Invalid username or password")


if __name__ == "__main__":
    main()
