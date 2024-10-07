import streamlit as st
import mysql.connector
from pandas import DataFrame


# Establish MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="user",  # Replace with your MySQL username
    password="TestingDB12345",  # Replace with your MySQL password
    database="Tracking_Expenses"
)
cursor = conn.cursor()

st.set_page_config(
    page_title='Data Entry',
    page_icon='📝'
)

st.title("📝 Purchases and Expenses Data Entry")
st.sidebar.success('Select a page above')


# Check if the value is stored in session_state
if "project_selection" in st.session_state:
    st.write(f"The project selected is: {st.session_state['project_selection']}")
else:
    st.write("No project selected yet. Please go back to the home page and select a project.")


# Function to fetch distinct data for a column from the database
def fetch_data(table_name, column_name):
    query = f'SELECT {column_name} FROM {table_name}'
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]


def fetch_and_display_data(query):
    # Execute the query
    cursor.execute(query)
    results = cursor.fetchall()

    # Convert rows to a pandas DataFrame for better display
    if results:
        results_df = DataFrame(results, columns=[desc[0] for desc in cursor.description])

        # Display the DataFrame in tabular format
        st.dataframe(results_df)  # You can also use st.table(df) if you prefer a static table

    else:
        st.write("No data found for the selected criteria.")


# Pulling options for dropdown menus
category = fetch_data('category', 'category')
payment_options = fetch_data('mode_of_payment', 'mode_of_payment')
stage_options = fetch_data('stages', 'stage')


# Create a simple form for user data input
with st.form("purchases_data_entry"):
    item_name = st.text_input("Enter the item name:")
    stage = st.selectbox("Select stage:", stage_options)
    category = st.selectbox("Select category:", category)
    vendor = st.text_input("Enter the vendor name:")
    purchase_date = st.date_input("Select the purchase date:")
    purchase_amount = st.number_input("Enter the amount:", min_value=0, max_value=1000000)
    mode_of_payment = st.selectbox("Select mode of payment:", payment_options)
    notes = st.text_input("Add notes if necessary:")
    submitted = st.form_submit_button("Submit")

if submitted:
    # Check if any fields are empty
    if not item_name or vendor == "" or purchase_amount <= 0 or mode_of_payment == "" or category == "":
        st.error("All fields are mandatory! Please fill in all fields.")
    else:
        # Insert form data into MySQL database
        cursor.execute(
            f"""INSERT INTO purchases_x (project_id, item_name, stage, category, vendor, purchase_date, purchase_amount, mode_of_payment, notes)
            VALUES ({st.session_state['project_id_selected']}, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (item_name, stage, category, vendor, purchase_date, purchase_amount, mode_of_payment, notes)
        )
        conn.commit()
        st.success(f"Data submitted successfully! Item Name: {item_name}, Stage: {stage}, Category: {category}, "
                   f"Vendor Name: {vendor}, Purchase Date: {purchase_date},"
                   f"Purchase Amount: {purchase_amount}, Mode of Payment: {mode_of_payment}, Notes: {notes}")


# Display all data from the database
if st.button("Show All Expenses Data"):
    whole_purchases_table_data = f"""
        SELECT purchase_id as Purchase_ID, item_name as Item_Name, stage as Stage, category as Category, vendor as Vendor, 
        purchase_date as Purchase_Date, purchase_amount as Purchase_Amount, mode_of_payment as Mode_of_Payment, 
        notes as Notes
        FROM purchases_x
        WHERE project_id = {st.session_state['project_id_selected']}
    """
    fetch_and_display_data(whole_purchases_table_data)


# Close the cursor and connection when done
cursor.close()
conn.close()
