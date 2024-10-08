from flask import Flask, render_template, request, redirect, url_for, flash
from scripts.patient_m import create_patient_profile, search_patients, get_patient_profile
from connect_to_database import connect_to_database
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dictionary to store credentials and login information
credentials_storage = {}

# Generate a random 4-digit number for credentials and calculate expiration time
def generate_credentials(username, password):
    credentials_code = random.randint(1000, 9999)
    expiration_time = datetime.now() + timedelta(hours=24)
    
    # Store credentials with expiration time
    credentials_storage[credentials_code] = {
        'username': username,
        'password': password,
        'expires_at': expiration_time
    }
    
    return credentials_code, expiration_time

# Remove expired credentials
def cleanup_expired_credentials():
    current_time = datetime.now()
    to_remove = [key for key, value in credentials_storage.items() if value['expires_at'] < current_time]
    
    for key in to_remove:
        del credentials_storage[key]

# Verify credentials before making any database connection
def verify_credentials(entered_credentials):
    cleanup_expired_credentials()  # Clean up expired credentials
    if int(entered_credentials) in credentials_storage:
        return credentials_storage[int(entered_credentials)]
    else:
        return None

# Login Route
@app.route('/', methods=['GET', 'POST'])
def login():
    cleanup_expired_credentials()  # Clean up expired credentials on login

    if request.method == 'POST':
        # Get the username and password from the form
        username = request.form['username']
        password = request.form['password']
        
        # Try connecting to the database
        mydb = connect_to_database(username, password)
        if mydb:  # Successful connection
            credentials_code, expiration_time = generate_credentials(username, password)
            flash(f"Your credentials are {credentials_code}. Expires in 24 hours: {expiration_time}")
            return redirect(url_for('main_menu', credentials_code=credentials_code))  # Redirect to main menu with credentials
        else:
            flash("Incorrect Username/Password")
    
    return render_template('login.html')

# Main Menu Route
@app.route('/main_menu')
def main_menu():
    credentials_code = request.args.get('credentials_code')
    
    if credentials_code:
        return render_template('index.html', credentials_code=credentials_code)
    
    return render_template('index.html', credentials_code=None)

# Add New Patient Route (Displays the form to add a new patient)
@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        # Get form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        
        # Concatenate separate DOB fields
        dob_month = request.form['dob_month']
        dob_day = request.form['dob_day']
        dob_year = request.form['dob_year']
        dob = f"{dob_year}{dob_month.zfill(2)}{dob_day.zfill(2)}"  # Format as YYYYMMDD
        
        gender = request.form['gender']
        street = request.form['street']
        zip_code = request.form['zip_code']
        city = request.form['city']
        state = request.form['state']
        delivery = request.form['delivery']
        
        # Concatenate separate phone number fields
        phone_area = request.form['phone_area']
        phone_central = request.form['phone_central']
        phone_line = request.form['phone_line']
        phone = f"{phone_area}{phone_central}{phone_line}"

        entered_credentials = request.form['credentials']

        # Verify the credentials before accessing the database
        user_info = verify_credentials(entered_credentials)
        if not user_info:
            flash("Invalid or expired credentials. Please log in again.")
            return redirect(url_for('patients'))

        # Insert the new patient using the saved username and password
        result = create_patient_profile(user_info['username'], user_info['password'], first_name, last_name, dob, gender, street, city, state, zip_code, delivery, phone)
        flash(result)
        return redirect(url_for('patients'))  # Redirect back to the patient management screen
    
    return render_template('add_patient.html')

# Search for a Patient Route
@app.route('/search_patient', methods=['POST'])
def search_patient():
    # Get form data
    name = request.form['name']
    dob = request.form['dob']
    phone = request.form['phone']
    entered_credentials = request.form['credentials']

    # Verify the credentials before accessing the database
    user_info = verify_credentials(entered_credentials)
    if not user_info:
        flash("Invalid or expired credentials. Please try again.")
        return redirect(url_for('patients'))

    # Perform the search in the database using valid credentials
    matching_patients = search_patients(user_info['username'], user_info['password'], name, dob, phone)

    return render_template('search_results.html', patients=matching_patients)

# View Patient Profile Route
@app.route('/view_patient/<patient_id>', methods=['POST'])
def view_patient(patient_id):
    entered_credentials = request.form['credentials']

    # Verify the credentials before accessing the database
    user_info = verify_credentials(entered_credentials)
    if not user_info:
        flash("Invalid or expired credentials. Please try again.")
        return redirect(url_for('patients'))

    # Fetch the patient profile and their medication report
    patient_profile, medication_report, age = get_patient_profile(user_info['username'], user_info['password'], patient_id)

    return render_template('view_profile.html', profile=patient_profile, meds=medication_report, age=age)

# Patients Route (For managing patients)
@app.route('/patients', methods=['GET', 'POST'])
def patients():
    return render_template('patients.html')

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
    global credentials_storage
    # Clear credentials and return to login screen
    credentials_storage.clear()
    flash("You have been signed off.")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
