from flask import Flask, render_template, request, redirect, url_for, flash
from scripts.patient_m import create_patient_profile  # Corrected import path
from connect_to_database import connect_to_database
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Global variables to store credentials and expiration time
credentials_code = None
expiration_time = None

# Generate a random 4-digit number for credentials and calculate expiration time
def generate_credentials():
    global expiration_time
    expiration_time = (datetime.now() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
    return random.randint(1000, 9999)

# Login Route (Credential Prompt)
@app.route('/', methods=['GET', 'POST'])
def login():
    global credentials_code
    if request.method == 'POST':
        # Get the username and password from the form
        username = request.form['username']
        password = request.form['password']
        
        # Try connecting to the database
        mydb = connect_to_database(username, password)
        if mydb:  # Successful connection
            credentials_code = generate_credentials()  # Generate credentials only on successful login
            return redirect(url_for('main_menu'))  # Redirect to the main menu
        else:  # Incorrect username/password
            flash("Incorrect Username/Password")
            credentials_code = None  # Ensure credentials code is not generated for incorrect login
    
    return render_template('login.html')  # No credentials passed to login page

# Main Menu Route (Shown after successful login)
@app.route('/main_menu')
def main_menu():
    from_management = request.args.get('from_management', default=False, type=bool)
    
    # If coming from a management page, do not display credentials
    if from_management:
        return render_template('index.html', credentials_code=None, expiration_time=None)
    
    if credentials_code is None:
        return redirect(url_for('login'))  # Redirect to login if no credentials are present
    
    # Render main menu with credentials
    return render_template('index.html', credentials_code=credentials_code, expiration_time=expiration_time)

# Patients Route (For managing patients)
@app.route('/patients', methods=['GET', 'POST'])
def patients():
    if request.method == 'POST':
        # Handle patient-related actions here
        flash("Patient management functionality here.")
    
    # Render the patient management page
    return render_template('patients.html')

# Add New Patient Route (Displays the form to add a new patient)
@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    global credentials_code
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        dob = request.form['dob']
        gender = request.form['gender']
        address = request.form['address']
        delivery = request.form['delivery']
        phone = request.form['phone']
        entered_credentials = request.form['credentials']

        # Check if the entered credentials match the generated credentials
        if entered_credentials == str(credentials_code):
            # Insert the new patient using the patient_m function
            result = create_patient_profile('username', 'password', name, dob, gender, address, delivery, phone)
            flash(result)
            return redirect(url_for('patients'))  # Redirect back to the patient management screen
        else:
            flash("Invalid credentials. Please try again.")

    return render_template('add_patient.html')

# Inventory Route (For managing inventory)
@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    if request.method == 'POST':
        # Handle inventory-related actions here (e.g., adding, updating inventory)
        flash("Inventory management functionality here.")
    
    # Render the inventory management page
    return render_template('inventory.html')

# Employees Route (For managing employees)
@app.route('/employees', methods=['GET', 'POST'])
def employees():
    if request.method == 'POST':
        # Handle employee-related actions here (e.g., adding, updating employees)
        flash("Employee management functionality here.")
    
    # Render the employee management page
    return render_template('employees.html')

# Sign Off Route (Sign off and return to login screen)
@app.route('/sign_off')
def sign_off():
    global credentials_code, expiration_time
    # Clear credentials and return to login screen
    credentials_code = None
    expiration_time = None
    flash("You have been signed off.")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
