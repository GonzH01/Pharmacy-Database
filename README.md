# Pharmacy Database

## Description

The Pharmacy Database is a web-based application for managing patient profiles, medications, inventory, and prescribers in a pharmacy environment. The system uses Flask as a backend framework, MySQL for database management, and a combination of HTML, CSS, and JavaScript for the frontend.

## Features

- **Manage Patients**: Add, search, and view patient profiles with details such as name, address, allergies, conditions, and medications.
- **Manage Inventory**: Add and update inventory for pharmacy products.
- **Manage Prescribers**: Placeholder page for managing prescribers (coming soon).
- **Add New Rx**: Add prescriptions to patient profiles (currently displays "Coming Soon").
- **Secure Access**: Credential-based access with a generated 4-digit code that expires after 24 hours.
- **Responsive Design**: User-friendly interface with easy navigation between patients, inventory, and prescriber management.
  
## Technologies Used

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Inline CSS for easy customization
- **Security**: Credentials expire after 24 hours

## Setup

### Requirements

- Python 3.x
- MySQL
- Flask (`pip install flask`)
- MySQL Connector (`pip install mysql-connector-python`)

### Instructions

1. Clone the repository:


2. Install required Python packages:


3. Set up your MySQL database:
- Create a new MySQL database.
- Update the `connect_to_database.py` file with your MySQL credentials.

4. Run the Flask application:

python app.py


5. Access the app on `http://127.0.0.1:5000` in your web browser.

### Database Schema

- **Patients Table**:
- patient_ID (Primary Key)
- first_name, last_name
- dob (date of birth)
- gender
- street, city, state, zip_code
- delivery (Yes/No)
- phone number
- allergies, conditions

- **Meds Table**:
- patient_ID (Foreign Key)
- drug, quantity, days_supply, refills
- date_written, date_expired, date_filled
- ndc_number (National Drug Code)

## Usage

- **Login**: Use your MySQL credentials to log in and generate a 4-digit code.
- **Main Menu**: Choose between managing patients, inventory, or prescribers.
- **Patient Management**: Add new patients, view patient profiles, and search for patients by name, DOB, or phone number.
- **Prescribers and Inventory**: Manage inventory and prescriber information (prescribers are coming soon).
- **Sign Off**: Log out of the system securely by signing off.

## Coming Soon

- **Manage Prescribers**: Full functionality for managing prescribers.
- **Add Rx**: Functionality to add and manage prescriptions for patients.
