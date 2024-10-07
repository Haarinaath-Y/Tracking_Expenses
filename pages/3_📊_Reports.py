import streamlit as st
import mysql.connector
from pandas import DataFrame
from streamlit_extras.chart_container import chart_container

# Establish MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="user",  # Replace with your MySQL username
    password="TestingDB12345",  # Replace with your MySQL password
    database="Tracking_Expenses"
)
cursor = conn.cursor()

st.set_page_config(
    page_title='Reports',
    page_icon='📊'
)

st.title("📊 Reports")

# Check if the value is stored in session_state
if "project_selection" in st.session_state:
    st.write(f"The project selected is: {st.session_state['project_selection']}")
else:
    st.write("No project selected yet. Please go back to the home page and select a project.")


st.sidebar.success('Select a page above')
st.header('Purchase data for selected column', divider='orange')


# Function to fetch distinct data for a column from the database
def fetch_data(table_name, column_name):
    query = f'SELECT {column_name} FROM {table_name}'
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]


def fetch_and_display_data(query):
    """
    Execute the given SQL query, fetch the results, and display them in a Streamlit app.
    Handles any SQL syntax errors and displays appropriate messages.

    Args:
        query (str): The SQL query to be executed.
    """
    try:
        # Execute the SQL query
        cursor.execute(query)

        # Fetch all rows from the executed query
        results = cursor.fetchall()

        # Check if there are any results
        if results:
            # Convert rows to a pandas DataFrame for better display
            results_df = DataFrame(results, columns=[desc[0] for desc in cursor.description])

            # Display the DataFrame in tabular format
            st.dataframe(results_df)  # You can also use st.table(df) for a static table
        else:
            # Inform the user if no data was found
            st.warning("No data found for the selected criteria.")

    except mysql.connector.Error as err:
        # Catch and handle specific MySQL errors
        st.warning("Please check if you've selected a valid project")

    except Exception as e:
        # Catch any other exceptions
        st.error(f"An unexpected error occurred: {e}")


# Display all purchases data for each
def to_title_case(column_values):
    return [str(value).title() for value in column_values]


# Requested column names
column_names = ['category', 'vendor', 'stage', 'mode_of_payment']

# Converting column names to title case
column_names_title_case = to_title_case(column_names)

# Dropdown to select the column in title case
selected_column = st.selectbox("Select the column:", column_names_title_case)

column_data = fetch_data('purchases_x', f'distinct trim(upper({selected_column}))')

# Convert each value to title case
column_data_title_case = to_title_case(column_data)
selected_item = st.selectbox("Select the item name:", column_data_title_case)


if st.button("Show Purchase Data for selected column"):
    purchase_data = f"""
        SELECT purchase_id as Purchase_ID, project_id as Project_id, item_name as Item_Name, stage as Stage, category as Category, vendor as Vendor, 
        purchase_date as Purchase_Date, purchase_amount as Purchase_Amount, mode_of_payment as Mode_of_Payment, 
        notes as Notes
        FROM purchases_x 
        WHERE trim(upper({selected_column})) = %s
        and project_id = {st.session_state['project_id_selected']}
    """

    cursor.execute(purchase_data, (selected_item,))
    rows = cursor.fetchall()

    # Convert rows to a pandas DataFrame for better display
    df = DataFrame(rows, columns=[desc[0] for desc in cursor.description])

    # Display the DataFrame in tabular format
    st.dataframe(df)  # You can also use st.table(df) if you prefer a static table


st.header('Other Reports', divider=True)

if st.button("Show Expenditure for each category"):
    expenditure_on_each_category = F"""
        SELECT c.category as Category, COALESCE(SUM(p.purchase_amount),"Not Yet Started") as Purchase_Amount
        FROM purchases_x p
        RIGHT JOIN category c ON p.category=c.category
        WHERE p.project_id = {st.session_state['project_id_selected']}
        GROUP BY c.category;
    """

    fetch_and_display_data(expenditure_on_each_category)


if st.button("Show Expenditure for each stage"):
    expenditure_on_each_stage = F"""
        SELECT s.stage as Stage, COALESCE(SUM(p.purchase_amount),"Not Yet Started") as Purchase_Amount
        FROM purchases_x p
        RIGHT JOIN stages s ON s.stage=p.stage
        WHERE p.project_id = {st.session_state['project_id_selected']}
        GROUP BY s.stage;
    """

    fetch_and_display_data(expenditure_on_each_stage)


if st.button("Show Expenditure for each category in each stage"):
    cursor.execute("SELECT category FROM category")
    categories = cursor.fetchall()

    expenditure_on_each_category_in_each_stage = "SELECT p.stage"

    # Add dynamic category columns to the SQL query
    for (category,) in categories:
        expenditure_on_each_category_in_each_stage += f", SUM(CASE WHEN p.category = '{category}' THEN p.purchase_amount ELSE 0 END) AS `{category}`"

    # Complete the SQL query
    expenditure_on_each_category_in_each_stage += F" FROM purchases_x p WHERE p.project_id = {st.session_state['project_id_selected']} GROUP BY p.stage"

    # Execute the dynamic SQL query
    fetch_and_display_data(expenditure_on_each_category_in_each_stage)

# Close the cursor and connection when done
cursor.close()
conn.close()
