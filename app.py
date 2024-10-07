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

st.title("Purchases and Expenses Data Entry")


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


# Display all purchases data for each
def to_title_case(column_values):
    return [str(value).title() for value in column_values]


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
            """INSERT INTO purchases (item_name, stage, category, vendor, purchase_date, purchase_amount, mode_of_payment, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (item_name, stage, category, vendor, purchase_date, purchase_amount, mode_of_payment, notes)
        )
        conn.commit()
        st.success(f"Data submitted successfully! Item Name: {item_name}, Stage: {stage}, Category: {category}, Vendor Name: {vendor}, Purchase Date: {purchase_date},"
                   f"Purchase Amount: {purchase_amount}, Mode of Payment: {mode_of_payment}, Notes: {notes}")


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

if st.button("Purchase data for the selected column"):
    purchase_data = f"""
        SELECT * 
        FROM purchases_x 
        WHERE trim(upper({selected_column})) = %s
    """

    cursor.execute(purchase_data, (selected_item,))
    rows = cursor.fetchall()

    # Convert rows to a pandas DataFrame for better display
    df = DataFrame(rows, columns=[desc[0] for desc in cursor.description])

    # Display the DataFrame in tabular format
    st.dataframe(df)  # You can also use st.table(df) if you prefer a static table

# Display all data from the database
if st.button("Show All Expenses Data"):
    whole_purchases_table_data = """
        SELECT purchase_id as Purchase_ID, item_name as Item_Name, category as Category, vendor as Vendor, 
        purchase_date as Purchase_Date, purchase_amount as Purchase_Amount, mode_of_payment as Mode_of_Payment, notes as Notes
        FROM purchases_x
    """
    fetch_and_display_data(whole_purchases_table_data)


if st.button("Show Expenditure for each category"):
    expenditure_on_each_category = """
        SELECT c.category as Category, COALESCE(SUM(p.purchase_amount),"Not Yet Started") as Purchase_Amount
        FROM purchases_x p
        RIGHT JOIN category c ON p.category=c.category
        GROUP BY c.category;
    """

    fetch_and_display_data(expenditure_on_each_category)


if st.button("Show Expenditure for each stage"):
    expenditure_on_each_stage = """
        SELECT s.stage as Stage, COALESCE(SUM(p.purchase_amount),"Not Yet Started") as Purchase_Amount
        FROM purchases_x p
        RIGHT JOIN stages s ON s.stage=p.stage
        GROUP BY s.stage;
    """

    fetch_and_display_data(expenditure_on_each_stage)


if st.button("Show Expenditure for each category in each stage"):
    cursor.execute("SELECT category FROM category")
    categories = cursor.fetchall()

    expenditure_on_each_category_in_each_stage = "SELECT stage"

    # Add dynamic category columns to the SQL query
    for (category,) in categories:
        expenditure_on_each_category_in_each_stage += f", SUM(CASE WHEN p.category = '{category}' THEN p.purchase_amount ELSE 0 END) AS `{category}`"

    # Complete the SQL query
    expenditure_on_each_category_in_each_stage += " FROM purchases_x p GROUP BY p.stage"

    # Execute the dynamic SQL query
    fetch_and_display_data(expenditure_on_each_category_in_each_stage)

# Close the cursor and connection when done
cursor.close()
conn.close()
