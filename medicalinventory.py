import streamlit as st
import sqlite3
import re
from datetime import datetime, date, timedelta
from fpdf import FPDF
import os
from piechrt import *

# Function to create a database connection
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn

def get_product_name(conn_products, product_id):
    query = "SELECT name FROM products WHERE id = ?"
    cursor = execute_query(conn_products, query, (product_id,))
    product_row = cursor.fetchone()
    if product_row:
        return product_row[0]
    else:
        return None

# Function to create a PDF invoice
def generate_invoice(conn_sales, id):
    query = "SELECT * FROM sales WHERE id = ?"
    cursor = execute_query(conn_sales, query, (id,))
    sale = cursor.fetchone()

    if not sale:
        st.write('Transaction not found.')
    else:
        # Extract transaction details
        customer_name, mobile_number, product_id, prod_quantity, amount, sale_date = sale[1], sale[2], sale[3], sale[4], sale[5], sale[6]
        product_name = get_product_name(conn_products, product_id)

        # Create PDF object
        pdf = FPDF()
        pdf.add_page()
        
        # Set font
        pdf.set_font("Arial", size = 12)

        # Add title
        pdf.cell(200, 10, txt = "Invoice", ln = True, align = 'C')
        pdf.ln(10)

        # Add transaction details to PDF
        pdf.cell(200, 10, txt = f"Transaction ID: {id}", ln=True, align='L')
        pdf.cell(200, 10, txt = f"Customer Name: {customer_name}", ln=True, align='L')
        pdf.cell(200, 10, txt = f"Mobile Number: {mobile_number}", ln=True, align='L')
        pdf.cell(200, 10, txt = f"Product Name: {product_name}", ln=True, align='L')
        pdf.cell(200, 10, txt = f"Quantity: {prod_quantity}", ln=True, align='L')
        pdf.cell(200, 10, txt = f"Amount: {amount}", ln=True, align='L')
        pdf.cell(200, 10, txt = f"Sale Date: {sale_date}", ln=True, align='L')

        # Save PDF to Downloads directory
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        pdf_file_name = f"Invoice_{id}.pdf"
        pdf_path = os.path.join(downloads_path, pdf_file_name)
        pdf.output(pdf_path)

        # Display the link for downloading the PDF
        st.success(f"Invoice generated successfully. You can view it in Downloads.")

def add_sales_transaction(conn_sales, customer_name, mobile_number, product_id, prod_quantity, amount, sale_date):
    cursor = conn_sales.cursor()
    cursor.execute("INSERT INTO sales (customer_name, mobile_number, product_id, prod_quantity, amount, sale_date) VALUES (?, ?, ?, ?, ?, ?)",
                   (customer_name, mobile_number, product_id, prod_quantity, amount, sale_date))
    conn_sales.commit()
    
    # Decrement the quantity of the product sold
    update_product_quantities(conn_products, product_id, prod_quantity)
    
    return cursor.lastrowid

def update_product_quantities(conn_products, product_id, prod_quantity):
    try:
        # Create a cursor object
        cursor = conn_products.cursor()

        # Execute the SQL query to update product quantities
        cursor.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (prod_quantity, product_id))
        
        # Commit the transaction
        conn_products.commit()

        print("Product quantity updated successfully.")

    except sqlite3.Error as e:
        print("Error updating product quantity:", e)




# Function to create a new user
def create_user(conn, pharmacy_name, username, email, password):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (pharmacy_name, username, email, password) VALUES (?, ?, ?, ?)", (pharmacy_name, username, email, password))
    conn.commit()
    return cursor.lastrowid

# Function to check if username exists
def check_username_exists(conn, username):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cursor.fetchone() is not None

# Function to check if email exists
def check_email_exists(conn, email):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    return cursor.fetchone() is not None

# Function to validate email address
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

# Function to validate password strength
def is_strong_password(password):
    return len(password) >= 8 and any(c.isupper() for c in password) and any(c.isdigit() for c in password)

# Function to search for products
def search_product(conn, user_id, name):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE user_id = ? AND name LIKE ?", (user_id, '%' + name + '%'))
    return cursor.fetchall()

# Function to execute a single query on the given database connection
def execute_query(connection, query, data=None):
    try:
        with connection:
            cursor = connection.cursor()
            if data:
                cursor.execute(query, data)
            else:
                cursor.execute(query)
            return cursor
    except sqlite3.Error as e:
        print(e)

# Function to add a product
def add_product(conn, user_id, name, expiry_date, quantity, amount):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (user_id, name, expiry_date, quantity, amount) VALUES (?, ?, ?, ?, ?)",
                   (user_id, name, expiry_date, quantity, amount))
    conn.commit()
    return cursor.lastrowid

# Function to remove product by name
def remove_product_by_name(conn, name):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE name = ?", (name,))
    conn.commit()

# Function to display sales input section
def show_sales_input(conn_sales, user_id):
    st.subheader('Input Sales Information')

    customer_name = st.text_input("Customer Name")
    mobile_number = st.text_input("Mobile Number")

    if not len(mobile_number) == 10 or not mobile_number.isdigit():
        st.error("Mobile number should be exactly 10 digits.")
        return

    name = st.text_input("Medicine Name")
    prod_quantity = st.number_input("Quantity", min_value=1, step=1)
    amount = st.number_input("Amount", min_value=0.01, step=0.01)
    
    # Ensure that the sale date is not ahead of today's date
    sale_date = st.date_input("Sale Date", date.today())
    if sale_date > date.today():
        st.error("Sale date cannot be ahead of today's date.")
        return

    if st.button("Add Transaction"):
        product_id = get_product_id_by_name(conn_products, user_id, name)
        if product_id is not None:
            add_sales_transaction(conn_sales, customer_name, mobile_number, product_id, prod_quantity, amount, sale_date)
            st.success("Transaction added successfully.")
        else:
            st.error(f"Product '{name}' not found.")

def get_product_id_by_name(conn_products, user_id, name):
    cursor = conn_products.cursor()
    cursor.execute("SELECT id FROM products WHERE user_id = ? AND name = ?", (user_id, name))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

# Function to fetch all products from the database
def fetch_all_products(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE user_id = ?", (user_id,))
    return cursor.fetchall()

def display_products_table(products):
    if products:
        st.write("Products:")
        df = pd.DataFrame(products, columns=["ID", "User ID", "Name", "Expiry Date", "Quantity", "Amount"])
        st.dataframe(df)
    else:
        st.warning("No products found.")

# Function to check for expiring products
def check_expiring_products(conn_products, user_id, threshold_days=15):
    today = date.today()
    threshold_date = today + timedelta(days=threshold_days)
    cursor = conn_products.cursor()
    cursor.execute("SELECT name, expiry_date FROM products WHERE user_id = ? AND expiry_date BETWEEN ? AND ?", (user_id, today, threshold_date))
    expiring_products = cursor.fetchall()
    return expiring_products

# Function to check for low stock items
def check_low_stock_items(conn_products, user_id, threshold_quantity=10):
    cursor = conn_products.cursor()
    cursor.execute("SELECT name, quantity FROM products WHERE user_id = ? AND quantity < ?", (user_id, threshold_quantity))
    low_stock_items = cursor.fetchall()
    return low_stock_items

# Create or connect to SQLite databases
conn_users = create_connection("user_database.db")
conn_products = create_connection("product_database.db")
conn_sales = create_connection("sales_database.db")

# Create tables if they don't exist
create_table_users_query = '''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    pharmacy_name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);
'''
execute_query(conn_users, create_table_users_query)

create_table_products_query = '''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    expiry_date DATE NOT NULL,
    quantity INTEGER NOT NULL,
    amount REAL NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
'''
execute_query(conn_products, create_table_products_query)

create_table_sales_query = '''
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    mobile_number TEXT NOT NULL,
    product_id INTEGER NOT NULL,
    prod_quantity INTEGER NOT NULL,
    amount REAL NOT NULL,
    sale_date DATE NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
'''
execute_query(conn_sales, create_table_sales_query)

st.title("Medical Inventory Management System")

# Check if user is already logged in
if "username" not in st.session_state:
    st.subheader("Login")
    username_input = st.text_input("Username", key="login_username")
    password_input = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        cursor = conn_users.cursor()
        cursor.execute("SELECT id, pharmacy_name FROM users WHERE username = ? AND password = ?", (username_input, password_input))
        user_data = cursor.fetchone()
        if user_data:
            user_id, pharmacy_name = user_data
            st.success(f"Welcome back, {username_input}!")
            st.session_state.username = username_input  # Store username in session state
            st.session_state.user_id = user_id  # Store user ID in session state
            st.session_state.pharmacy_name = pharmacy_name  # Store pharmacy name in session state
            st.rerun()  # Rerun the app to hide login logic
        else:
            st.error("Invalid username or password")

    st.subheader("Sign Up")
    pharmacy_name = st.text_input("Pharmacy Name", key="signup_pharmacy_name")
    new_username = st.text_input("Username", key="signup_username")
    new_email = st.text_input("Email", key="signup_email")
    new_password = st.text_input("Password", type="password", key="signup_password")

    if st.button("Sign Up"):
        if not is_valid_email(new_email):
            st.error("Invalid email address")
        elif check_username_exists(conn_users, new_username):
            st.error("Username already exists. Please choose a different one.")
        elif check_email_exists(conn_users, new_email):
            st.error("Email address already registered.")
        elif not is_strong_password(new_password):
            st.error("Password should be at least 8 characters long and contain at least one uppercase letter and one digit.")
        else:
            create_user(conn_users, pharmacy_name, new_username, new_email, new_password)
            st.success("Account created successfully. You can now log in.")
            st.experimental_rerun()  # Rerun the app to hide signup logic

# Add Product functionality
elif "username" in st.session_state:
    st.sidebar.write(f"Logged in as: {st.session_state.pharmacy_name}")
    st.sidebar.button("Logout", on_click=lambda: st.session_state.pop("username"))
    menu = st.sidebar.selectbox("Menu", ["Home", "Add Product", "View Products", "Sales"])  # Added "Sales" option
    # Inside the main section of the app
    if menu == "Home":
        st.subheader("Home")
        st.write("Welcome to the Medical Inventory Management System. Please select an option from the sidebar.")
        # Check for expiring products
        expiring_products = check_expiring_products(conn_products, st.session_state.user_id)
        if expiring_products:
            st.warning("Expiring Products:")
            for product in expiring_products:
                st.write(f"- {product[0]} is expiring on {product[1]}")

        # Check for low stock items
        low_stock_items = check_low_stock_items(conn_products, st.session_state.user_id)
        if low_stock_items:
            st.warning("Low Stock Items:")
            for item in low_stock_items:
                st.write(f"- {item[0]} has only {item[1]} left")
        main()
    elif menu == "Add Product":
        st.subheader("Add Product")
        name = st.text_input("Product Name", key="add_product_name")
        expiry_date = st.date_input("Expiry Date", min_value=datetime.today(), key="add_product_expiry")
        quantity = st.number_input("Quantity", min_value=1, step=1, key="add_product_quantity")
        amount = st.number_input("Amount", min_value=0.01, step=0.01, key="add_product_amount")

        if st.button("Add Product", key="add_product_button"):
            add_product(conn_products, st.session_state.user_id, name, expiry_date, quantity, amount)
            st.success("Product added successfully.")

    # Inside the View Products section
    elif menu == "View Products":
        st.subheader("View Products")
        # Check for expiring products
        expiring_products = check_expiring_products(conn_products, st.session_state.user_id)
        if expiring_products:
            st.warning("Expiring Products:")
            for product in expiring_products:
                st.write(f"- {product[0]} is expiring on {product[1]}")

        # Check for low stock items
        low_stock_items = check_low_stock_items(conn_products, st.session_state.user_id)
        if low_stock_items:
            st.warning("Low Stock Items:")
            for item in low_stock_items:
                st.write(f"- {item[0]} has only {item[1]} left")
        # Search product
        search_query = st.text_input("Search Product", key="search_product_input")
        
        # Add remove button beside search button
        col1, col2 = st.columns([3, 15])  # Divide the layout into two columns
        
        with col1:
            # Search button
            if st.button("Search", key="search_product_button"):
                if search_query:
                    products = search_product(conn_products, st.session_state.user_id, search_query)
                    if products:
                        st.write("Found Products:")
                        found_products_info = []
                        for product in products:
                            product_info = f"Name: {product[2]}, Expiry Date: {product[3]}, Quantity: {product[4]}, Amount: {product[5]}"
                            found_products_info.append(product_info)
                        
                        # Display found products in a straight line
                        found_products_str = "\n".join(found_products_info)
                        st.markdown(found_products_str)
                    else:
                        st.warning("No products found.")
        
        with col2:
            # Remove button
            if st.button("Remove", key="remove_product_button") and search_query:
                product_name_to_remove = search_query
                remove_product_by_name(conn_products, product_name_to_remove)
                st.success(f"Product '{product_name_to_remove}' removed successfully.")

        # Display all products only if there's no search query
        
        all_products = fetch_all_products(conn_products, st.session_state.user_id)
        display_products_table(all_products)


    # Inside the Sales menu
    elif menu == "Sales":
        show_sales_input(conn_sales, st.session_state.user_id)
        st.subheader("Sales")
        
        # Option 1: Search sales by date
        selected_date = st.date_input("Select Date", date.today())
        
        # Fetch sales for the selected date
        query = "SELECT * FROM sales WHERE sale_date = ?"
        cursor = execute_query(conn_sales, query, (selected_date,))
        sales = cursor.fetchall()
        
        if sales:
            st.write(f"Sales on {selected_date}:")
            for sale in sales:
                customer_name = sale[1]
                transaction_id = sale[0]
                st.write(f"- Customer Name: {customer_name}")
                st.write(f"  - Transaction ID: {transaction_id}")
                
                # Generate button key for each transaction
                generate_button_key = f"generate_invoice_{transaction_id}"
                
                # Add validation to ensure only authorized user can generate invoice
                
                if st.button("Generate Invoice", key=generate_button_key):
                    generate_invoice(conn_sales, transaction_id)
                
        else:
            st.warning("No sales found for the selected date.")
        
conn_users.close()
conn_products.close()
conn_sales.close()