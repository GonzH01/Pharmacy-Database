# Pharmacy Database Management System

## Overview

The **Pharmacy Database Management System** is a web-based application built with Flask and MySQL, designed to manage patients, medications, inventory, and prescribers in a pharmacy setting. The system allows users to add, edit, view, and manage patients and prescriptions while ensuring data integrity and security through user authentication and credential management.

## Features

- **User Authentication:** Secure login system with random 4-digit credentials, valid for 24 hours.
- **Patient Management:**
  - Add new patient profiles with details like name, date of birth, contact information, allergies, and conditions.
  - Search for patients by name, date of birth, or phone number.
  - View detailed patient profiles with medication history.
  - Edit patient details and update prescriptions.
- **Prescription Management:**
  - Add new prescriptions for patients.
  - Edit existing prescriptions, including dosage, refills, and directions (SIG).
  - Automatic expiration calculations for prescriptions.
- **Inventory Management:**
  - Add, view, and update inventory items, including medication name, NDC, dosage, expiration date, and balance on hand.
  - Check NDC existence and details.
  - Export inventory data to CSV.
- **Credential System:**
  - Temporary login credentials generated for secure database access.
  - Session-based credential management for secure data access across sessions.
  
## Prerequisites

- Python 3.8+
- MySQL Server
- MySQL Workbench (for database management)
- Web browser (e.g., Chrome, Firefox)

## Installation

1. **Clone the repository:**

   "git clone https://github.com/yourusername/pharmacy-database.git"
   "cd pharmacy-database"

2. **Set up a virtual environment:**

   "python -m venv pharmacy_env"
   "pharmacy_env\\Scripts\\activate" (For Windows)
   "source pharmacy_env/bin/activate" (For macOS/Linux)

3. **Install dependencies:**

   "pip install -r requirements.txt"

4. **Set up the database:**

   - Ensure MySQL Server is running.
   - Launch MySQL Workbench and create a new user with appropriate privileges.
   - Create a new database or let the app handle it during setup.

## Usage

1. **Run the application:**

   "python app.py"

2. **When prompted:**
   - Enter your MySQL credentials (username and password).
   - Specify the name of the database.
   - If the database doesn't exist, the system will prompt you to create a new one.
   - Once the connection is successful, the default web browser will open at "http://localhost:5000".

3. **Login:**
   - Use your credentials to log in.
   - Upon successful login, you will receive a 4-digit code valid for 24 hours.

4. **Main Functionalities:**
   - **Manage Patients:** Add, search, view, or edit patient profiles.
   - **Manage Inventory:** Add, update, or view inventory items.
   - **Manage Prescriptions:** Add or edit prescriptions for patients.
   - **Export Inventory:** Export inventory data to a CSV file.

## Key Files and Structure

- **app.py**: Main Flask application file with all routes and logic.
- **templates/**: HTML templates for web pages (login, patient management, inventory management, etc.).
- **static/**: Static files like images and CSS.
- **scripts/**:
  - **patient_m.py**: Functions for patient management.
  - **inventory_m.py**: Functions for inventory management.
  - **connect_to_database.py**: Functions for database connection and creation.

## Security

- **Session-based Credential Handling:** Temporary credentials are used to manage sessions securely.
- **Input Validation:** User inputs are validated to prevent SQL injection and other common vulnerabilities.
- **Error Handling:** Try-except blocks ensure that the application handles errors gracefully.

## Future Enhancements

- **Pagination for Patient and Medication Lists:** Add pagination to handle large datasets more efficiently.
- **Audit Trail:** Implement logging for tracking changes made by users.
- **Advanced Search:** Add fuzzy matching for more flexible patient and medication searches.
- **Role-Based Access Control:** Differentiate user access levels for better security.

## Troubleshooting

- **Cannot Connect to MySQL:** Ensure MySQL Server is running and accessible. Verify the username, password, and database name.
- **Webpage Not Loading:** Check if the Flask app is running and the browser is directed to "http://localhost:5000".
- **Login Issues:** Ensure you’re using valid credentials and that the temporary 4-digit code is still active.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests. Contributions are welcome! Star this repository if you wish to see more progress!!


## Acknowledgments

- **Flask**: Python web framework.
- **MySQL**: Database management system.
- **Bootstrap/HTML/CSS**: For web page design.
