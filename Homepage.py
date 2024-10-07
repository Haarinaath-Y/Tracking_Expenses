import streamlit as st
import mysql.connector

# Establish MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="user",  # Replace with your MySQL username
    password="TestingDB12345",  # Replace with your MySQL password
    database="Tracking_Expenses"
)
cursor = conn.cursor()

st.set_page_config(
    page_title='Tracking Expenses App',
    page_icon='🧾'
)

st.title("Welcome to Expense Tracker App")
st.sidebar.success('Select a page above')


def fetch_project_data(table_name):
    query = f'SELECT CONCAT(project_id, " - ", project_name) FROM {table_name}'
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]


def fetch_project_id(table_name):
    query = f'SELECT project_id FROM {table_name}'
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]


project = fetch_project_data('projects')
project_selection = st.selectbox("Select the project:", project)
project_id_selected = project_selection.split(' - ')[0]

# Store the project details in session state
if project_selection:
    st.session_state["project_selection"] = project_selection

# Store the project id in session state
if project_id_selected:
    st.session_state["project_id_selected"] = project_id_selected

st.success(f"You have selected the project: {project_selection}")


