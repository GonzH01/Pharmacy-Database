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
