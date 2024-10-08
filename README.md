# Pharmacy Database System

## Overview
This project is a Flask-based web application designed to manage various aspects of a pharmacy database system, including patient profiles, inventory management, and profit reporting. The system provides functionality for adding, searching, and viewing patient profiles, managing inventory items, and viewing profit reports. It also includes credential-based access control to ensure secure database interactions.

## Features
1. **Patient Management**
    - Add new patient profiles with fields for name, date of birth, address, and phone number.
    - Search patients by name and DOB or phone number.
    - View patient profiles and associated medication reports.

2. **Inventory Management**
    - Add and view inventory items, including item name, price, and quantity.
    - View profit reports based on the inventory balance.

3. **User Authentication**
    - Secure login system using username and password.
    - 4-digit credential system with 24-hour expiration for database interactions.

## Project Structure

### `app.py`
Main application file that defines the routes for login, patient management, inventory management, and authentication.

### `connect_to_database.py`
Handles MySQL database connections for user authentication and data management.

### `scripts/`
Contains backend logic for managing patients and inventory.
- **`patient_m.py`**: Handles patient creation, search, and profile retrieval.
- **`inventory_m.py`**: Manages inventory and profit tables.

### `templates/`
Contains the HTML files for the frontend interface.
- **`add_patient.html`**: Form for adding new patient profiles.
- **`patients.html`**: Manage and search patients.
- **`inventory.html`**: Manage and view inventory.
- **`index.html`**: Main menu for navigation.

## Setup and Installation

1. Clone the repository:
    ```bash
    git clone <repository-url>
    ```
2. Navigate to the project directory:
    ```bash
    cd pharmacy-database
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Create and configure your MySQL database. Update the connection details in `connect_to_database.py`.

5. Run the Flask application:
    ```bash
    python app.py
    ```

## Usage

- Access the web interface at `http://localhost:5000`.
- Log in with your username and password.
- Use the navigation menu to manage patients, inventory, and view reports.
