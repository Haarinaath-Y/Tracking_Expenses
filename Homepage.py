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


st.title("📚 Welcome to Expense Tracker App")
st.sidebar.success('Select a page above')


def fetch_project_data(table_name):
    query = f'SELECT CONCAT(project_id, " - ", project_name) FROM {table_name}'
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]


def fetch_project_id(table_name):
    query = f'SELECT project_id FROM {table_name}'
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]


# Function to store the selected value in session state
def store_session_state(key, value):
    if key == 'project_selection' and value == "Project Names with Project ID" or value == 'Null' or value == '':
        st.warning("Please select a valid project")
    else:
        st.session_state[key] = value


project = fetch_project_data('projects')

# Adding a blank option to the project selection
project_with_blank = ["Project Names with Project ID"] + project  # Prepend an empty string to the project list

project_selection = st.selectbox("Select the project:", project_with_blank)
project_id_selected = project_selection.split(' - ')[0]

# Store the project details in session state using the refactored function
store_session_state("project_selection", project_selection)
store_session_state("project_id_selected", project_id_selected)

if project_selection != "Project Names with Project ID":
    st.success(f"You have selected the project: {project_selection}")


