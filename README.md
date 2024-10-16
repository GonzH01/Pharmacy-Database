# Pharmacy Database Management System

This is a Pharmacy Database Management System built with Flask and MySQL, designed to manage patient profiles, inventory (medications), and prescribers. It supports creating, editing, viewing, and managing both patient and medication records.

## Features

- **User Authentication**: Username and password-based login.
- **Patient Management**: Add, search, view, and manage patient profiles.
- **Inventory Management**: Add, view, and manage medications in the pharmacy's inventory.
- **Prescription Management**: Add and edit prescriptions for patients.
- **Session-based Credentials**: Generated credentials for database access, which expire after 24 hours.

## Installation

### Prerequisites

Make sure you have the following installed on your system:

- [Python 3.7+](https://www.python.org/downloads/)
- [MySQL](https://www.mysql.com/downloads/)
- [Flask](https://flask.palletsprojects.com/en/latest/)

### Steps to Install

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-username/pharmacy-database.git
   cd pharmacy-database

    Create and activate a Python virtual environment (optional but recommended):

    bash

python -m venv pharmacy_env
source pharmacy_env/bin/activate  # On Windows use `pharmacy_env\Scripts\activate`

Install Dependencies:

Install the necessary Python packages listed in the requirements.txt file:

bash

pip install -r requirements.txt

Database Setup:

    Create a MySQL database named pharmacy_db.
    Update your MySQL connection details in the connect_to_database.py file.

Example:

python

def connect_to_database(username, password):
    mydb = mysql.connector.connect(
        host="localhost",
        user=username,
        password=password,
        database="pharmacy_db"
    )
    return mydb

Run the Application:

Once everything is set up, run the Flask application:

bash

    python app.py

    Access the Application:

    Open your browser and go to http://127.0.0.1:5000/ to access the application.

Project Structure

bash

pharmacy-database/
│
├── app.py                    # Main Flask application
├── connect_to_database.py     # Database connection logic
├── requirements.txt           # Python dependencies
├── templates/                 # HTML templates for the app (login.html, index.html, etc.)
│   ├── login.html
│   ├── index.html
│   ├── add_patient.html
│   ├── view_profile.html
│   ├── add_med.html
│   └── inventory.html
├── static/                    # Static files (CSS, JS)
├── scripts/                   # Python modules for database logic
│   ├── patient_m.py           # Logic for patient management
│   └── inventory_m.py         # Logic for inventory management
└── README.md                  # Project readme file

Usage
Adding a Patient

    Log in using your credentials.
    Navigate to "Manage Patients."
    Click "Add New Patient" and fill in the required information.
    Submit the form to add the patient to the database.

Managing Inventory

    Navigate to "Manage Inventory."
    Click "Add New Item" to add a new medication to the inventory.
    Fill in the required details such as NDC number, drug name, lot number, expiration date, etc.
    Submit to add the item to the database.

Editing Prescriptions

    Navigate to a patient's profile from the "Manage Patients" section.
    Click "Edit Rx" next to the prescription you want to edit.
    Update the fields as needed and submit to save changes.

Contributing

Feel free to fork this project, submit issues, or contribute by submitting pull requests. Contributions are always welcome!
