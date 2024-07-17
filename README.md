# Medical Inventory Management System

## Introduction

The Medical Inventory Management System is a streamlined and efficient tool designed to help pharmacies and medical stores manage their inventory, track sales, and handle product information. Built using Python, Streamlit, and SQLite, this system provides an easy-to-use interface for managing medical supplies, generating invoices, and monitoring product expiration dates and stock levels.

## Features

- **User Authentication:** Secure login and signup functionality for users.
- **Product Management:** Add, search, view, and delete products from the inventory.
- **Sales Management:** Record sales transactions and generate PDF invoices.
- **Expiry Notifications:** Alerts for products that are nearing their expiration date.
- **Stock Alerts:** Notifications for low stock items to ensure timely restocking.
- **Responsive Design:** Intuitive and user-friendly interface built with Streamlit.

## Technologies Used

- **Python:** The core programming language used for backend logic.
- **Streamlit:** A powerful library for creating web applications.
- **SQLite:** A lightweight database for storing user, product, and sales information.
- **FPDF:** A Python library for generating PDF files.

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/Yashborse45/medicalinventorymanagementsystem.git
    cd medicalinventorymanagementsystem
    ```

2. **Create and activate a virtual environment:**
    ```bash
    python -m venv env
    source env/bin/activate   # On Windows: env\Scripts\activate
    ```

3. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the SQLite database:**
    - Ensure you have SQLite installed on your system.
    - Create the necessary database files and tables by running the following commands in your SQLite shell:

    ```sql
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        pharmacy_name TEXT NOT NULL,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        expiry_date DATE NOT NULL,
        quantity INTEGER NOT NULL,
        amount REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

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
    ```

5. **Run the application:**
    ```bash
    streamlit run medicalinventory.py
    ```
    Make sure to save the piechrt.py too.

## Usage

1. **Login/Signup:**
    - New users can sign up by providing their pharmacy name, username, email, and password.
    - Existing users can log in using their username and password.

2. **Dashboard:**
    - After logging in, users can navigate through the sidebar menu to access different functionalities such as Home, Add Product, View Products, and Sales.

3. **Add Product:**
    - Users can add new products to the inventory by providing the product name, expiry date, quantity, and amount.

4. **View Products:**
    - Users can view all products in the inventory. The system also displays notifications for products that are nearing expiry and those that have low stock levels.

5. **Sales:**
    - Users can record sales transactions and generate PDF invoices for customers. The system tracks customer details, product quantity sold, total amount, and sale date.

## Sample Data Insertion

To insert sample data into the database, use the following SQL commands:

```sql
INSERT INTO products (user_id, name, expiry_date, quantity, amount) VALUES
    (3, 'Vicks', '2024-05-02', 15, 19.99),
    (3, 'Candida', '2023-11-21', 10, 64),
    (3, 'CD DIORSKIN NUDE SKIN-GLOWING MAKEUP SUNSCREEN BROAD SPECTRUM SPF 15 041 Ochre', '2023-04-14', 8, 92),
    (3, 'Miconazole 3', '2023-09-02', 20, 28),
    (3, 'Propranolol Hydrochloride', '2023-09-10', 5, 61);
```

## Contributing

We welcome contributions to enhance the functionality of this project. Feel free to fork the repository and submit pull requests.

## License

This project is licensed under the MIT License.

## Acknowledgements

- Special thanks to the open-source community for providing the tools and libraries used in this project.

---

Feel free to modify this content based on your specific project details and requirements.
