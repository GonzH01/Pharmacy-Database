# Pharmacy Database Management System

This is a **Pharmacy Database Management System** built using **Flask** as the web framework and **MySQL** for the database. The system allows users to manage patients, inventory, and employees through a secure, credential-based login system.

## Features

- **Credential-Based Login**: Users must log in using their username, password, and a 4-digit one-time credential code generated upon login.
- **Patient Management**:
  - Add new patients with required details such as Name, DOB, Address, Phone Number, Gender, and Delivery options.
  - Auto-login to the database using the 4-digit credentials.
- **Inventory Management**: Manage pharmacy inventory by adding, viewing, and updating stock.
- **Employee Management**: Manage employee records with the ability to add, view, and update employee information.
- **Sign Off Functionality**: Securely sign off from the system, clearing credentials and returning to the login screen.

## Setup Instructions

1. **Clone the repository**:
   `git clone https://github.com/yourusername/pharmacy-database.git`
   `cd pharmacy-database`

2. **Install the required dependencies**:
   Create a virtual environment and install the required packages using the `requirements.txt` (if available) or the following command:
   `pip install flask mysql-connector-python`

3. **Set up the MySQL database**:
   - Ensure you have a MySQL database set up and accessible.
   - Create the necessary tables by running the provided `connect_to_database.py` and `patient_m.py` scripts.

4. **Run the application**:
   Run the Flask application:
   `python app.py`

5. **Access the application**:
   Open your browser and navigate to `http://localhost:5000` to use the application.

## Technologies Used

- **Flask**: Web framework for handling routing, requests, and rendering templates.
- **MySQL**: Database for managing pharmacy data, including patients, inventory, and employees.
- **HTML/CSS**: For front-end design and forms.
