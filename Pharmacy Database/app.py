from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from scripts.patient_m import create_patient_profile, search_patients, get_patient_profile
from scripts.inventory_m import create_tables_and_input_data, view_inventory_table, update_balance, get_drug_by_ndc, check_ndc_in_inventory 
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
    return credentials_storage.get(int(entered_credentials))

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
            flash(f"Your credentials are {credentials_code}. Expires in 24 hours: {expiration_time.strftime('%Y-%m-%d %I:%M:%S %p')}")
            return redirect(url_for('main_menu', credentials_code=credentials_code))  # Redirect to main menu with credentials
        else:
            flash("Incorrect Username/Password")
    
    return render_template('login.html')

# Main Menu Route
@app.route('/main_menu')
def main_menu():
    credentials_code = request.args.get('credentials_code')
    
    if credentials_code:
        # Retrieve the expiration time from the credentials_storage
        expiration_info = credentials_storage.get(int(credentials_code))
        if expiration_info:
            expiration_time = expiration_info['expires_at']
            return render_template('index.html', credentials_code=credentials_code, expiration_time=expiration_time)
    
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

        allergies = request.form['allergies']
        conditions = request.form['conditions']

        entered_credentials = request.form['credentials']

        # Verify the credentials before accessing the database
        user_info = verify_credentials(entered_credentials)
        if not user_info:
            flash("Invalid or expired credentials. Please log in again.")
            return redirect(url_for('patients'))

        # Insert the new patient using the saved username and password
        result = create_patient_profile(user_info['username'], user_info['password'], first_name, last_name, dob, gender, street, city, state, zip_code, delivery, phone, allergies, conditions)
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
@app.route('/view_patient/<patient_id>', methods=['GET', 'POST'])
def view_patient(patient_id):
    if request.method == 'POST':
        entered_credentials = request.form['credentials']

        # Verify the credentials before accessing the database
        user_info = verify_credentials(entered_credentials)
        if not user_info:
            flash("Invalid or expired credentials. Please try again.")
            return redirect(url_for('patients'))
    else:
        # For GET requests, we bypass credential verification
        user_info = credentials_storage.get(list(credentials_storage.keys())[0])  # Grabbing stored credentials

    if not user_info:
        flash("Could not retrieve credentials. Please log in again.")
        return redirect(url_for('login'))

    # Fetch the patient profile and their medication report, along with age
    patient_profile, medication_report, age = get_patient_profile(user_info['username'], user_info['password'], patient_id)

    # Pass enumerate into the template context
    return render_template('view_profile.html', profile=patient_profile, meds=medication_report, age=age, enumerate=enumerate)

# Add Rx Route (Displays the form to add a new prescription)
@app.route('/add_rx/<patient_id>', methods=['GET', 'POST'])
def add_rx(patient_id):
    if request.method == 'POST':
        # Get form data for the prescription
        ndc_number = request.form['ndc_number']
        drug = request.form['drug']
        quantity = request.form['quantity']
        days_supply = request.form['days_supply']
        refills = request.form['refills']
        date_written = request.form['date_written']
        date_expired = request.form['date_expired']
        date_filled = request.form['date_filled']
        sig = request.form['sig']  # Directions

        # Verify the credentials before accessing the database
        entered_credentials = request.form['credentials']
        user_info = verify_credentials(entered_credentials)
        if not user_info:
            flash("Invalid or expired credentials. Please log in again.")
            return redirect(url_for('patients'))

        # Insert the new prescription into the meds table
        mydb = connect_to_database(user_info['username'], user_info['password'])
        mycursor = mydb.cursor()

        sql = """
            INSERT INTO meds (patient_ID, drug, quantity, days_supply, refills, date_written, date_expired, date_filled, ndc_number, sig)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (patient_id, drug, quantity, days_supply, refills, date_written, date_expired, date_filled, ndc_number, sig)
        mycursor.execute(sql, values)
        mydb.commit()

        flash("Prescription added successfully.")
        return redirect(url_for('view_patient', patient_id=patient_id))

    return render_template('add_rx.html', patient_id=patient_id)

# Edit Rx Route (Displays the form to edit an existing prescription)
@app.route('/edit_rx/<int:id>/<patient_id>', methods=['GET', 'POST'])
def edit_rx(id, patient_id):
    if request.method == 'POST':
        # Get updated form data for the prescription
        drug = request.form['drug']
        quantity = int(request.form['quantity'])
        days_supply = request.form['days_supply']
        refills = request.form['refills']
        date_written = request.form['date_written']
        date_expired = request.form['date_expired']
        date_filled = request.form['date_filled']
        sig = request.form['sig']  # Directions

        # Verify credentials
        entered_credentials = request.form['credentials']
        user_info = verify_credentials(entered_credentials)
        if not user_info:
            flash("Invalid or expired credentials. Please log in again.")
            return redirect(url_for('patients'))

        # Update the prescription in the meds table
        mydb = connect_to_database(user_info['username'], user_info['password'])
        mycursor = mydb.cursor()

        sql = """
            UPDATE meds SET drug=%s, quantity=%s, days_supply=%s, refills=%s, date_written=%s, date_expired=%s, date_filled=%s, sig=%s
            WHERE id=%s AND patient_ID=%s
        """
        values = (drug, quantity, days_supply, refills, date_written, date_expired, date_filled, sig, id, patient_id)
        mycursor.execute(sql, values)
        mydb.commit()

        # Update the balance (if the edited prescription affects balance on hand)
        update_result = update_balance(
            ndc=drug,  # Assuming NDC is linked to the drug
            new_balance_on_hand=quantity,
            username=user_info['username'],
            password=user_info['password']
        )
        flash(update_result)

        flash("Prescription updated successfully.")
        return redirect(url_for('view_patient', patient_id=patient_id))


    # Fetch the medication details for editing
    user_info = credentials_storage.get(list(credentials_storage.keys())[0])  # Grabbing stored credentials
    if not user_info:
        flash("Could not retrieve credentials. Please log in again.")
        return redirect(url_for('login'))

    mydb = connect_to_database(user_info['username'], user_info['password'])
    mycursor = mydb.cursor()

    # Fetch the current details of the medication
    mycursor.execute("SELECT * FROM meds WHERE id = %s AND patient_ID = %s", (id, patient_id))
    med = mycursor.fetchone()
    return render_template('edit_rx.html', med=med, id=id, patient_id=patient_id)

def get_drug_by_ndc(ndc, username=None, password=None):
    mydb = connect_to_database(username, password)
    if not mydb:
        return None

    cursor = mydb.cursor(dictionary=True)
    cursor.execute("""
    SELECT drug_name, strength, dosage_form, manufacturer_name, unit_price, phone_number, email, fax, description, 
           storage_requirements, controlled_substance_status, (quantity * quantity_per_unit) AS balance_on_hand
    FROM inventory WHERE ndc_number = %s
    """, (ndc,))
    result = cursor.fetchone()

    return result


@app.route('/check_ndc', methods=['GET'])
def check_ndc():
    ndc = request.args.get('ndc')
    credentials = request.args.get('credentials')

    if not ndc or not credentials:
        return jsonify({'error': 'Invalid NDC or credentials.'}), 400

    # Retrieve user credentials
    user_info = verify_credentials(credentials)
    if not user_info:
        return jsonify({'error': 'Invalid or expired credentials.'}), 400

    username = user_info['username']
    password = user_info['password']

    # Call the function to check NDC in the database
    drug_details = check_ndc_in_inventory(ndc, username, password)

    if drug_details:
        return jsonify({
            'exists': True,
            'drug_name': drug_details.get('drug_name', ''),
            'strength': drug_details.get('strength', ''),
            'dosage_form': drug_details.get('dosage_form', ''),
            'manufacturer_name': drug_details.get('manufacturer_name', ''),
            'unit_price': str(drug_details.get('unit_price', '')),
            'phone_number': str(drug_details.get('phone_number', '')),
            'email': drug_details.get('email', ''),
            'fax': str(drug_details.get('fax', '')),
            'description': drug_details.get('description', ''),
            'storage_requirements': drug_details.get('storage_requirements', ''),
            'controlled_substance_status': drug_details.get('controlled_substance_status', '')
        })
    else:
        return jsonify({'exists': False})


@app.route('/add_med', methods=['GET', 'POST'])
def add_med():
    if request.method == 'POST':
        # Get form data including credentials
        ndc = request.form['ndc']
        drug_name = request.form['drug_name']
        dosage_form = request.form['dosage_form']
        strength = request.form['strength']
        quantity = int(request.form['quantity'])
        quantity_per_unit = int(request.form['quantity_per_unit'])
        expiration_date = request.form['expiration_date']
        lot_number = request.form['lot_number']
        manufacturer_name = request.form['manufacturer_name']
        unit_price = float(request.form['unit_price'])
        phone_number = request.form['phone_number']
        email = request.form['email']
        fax = request.form['fax']
        description = request.form['description']
        storage_requirements = request.form['storage_requirements']
        controlled_substance_status = request.form['controlled_substance_status']
        allergies_warnings = request.form['allergies_warnings']
        credentials = request.form['credentials']

        # Verify credentials before proceeding
        user_info = verify_credentials(credentials)
        if not user_info:
            flash("Invalid or expired credentials. Please try again.")
            return redirect(url_for('add_med'))

        # Use the verified username and password for database operations
        username = user_info['username']
        password = user_info['password']

        # Add medication to inventory
        result = create_tables_and_input_data(
            ndc, drug_name, dosage_form, strength, quantity, quantity_per_unit,
            expiration_date, lot_number, manufacturer_name, unit_price,
            phone_number, email, fax, description, storage_requirements,
            controlled_substance_status, allergies_warnings, username, password
        )

        if "Error connecting to the database" in result:
            flash(result)
            return redirect(url_for('add_med'))

        flash(result)
        return redirect(url_for('inventory'))

    return render_template('add_med.html')


# Route to view inventory sorted by unit price
@app.route('/sort_inventory', methods=['POST'])
def sort_inventory():
    # Get credentials from form
    entered_credentials = request.form.get('credentials')

    # Verify credentials before accessing the database
    user_info = verify_credentials(entered_credentials)
    if not user_info:
        flash("Invalid or expired credentials. Please try again.")
        return redirect(url_for('view_inventory'))

    # Fetch inventory data sorted by unit price
    inventory_data = view_inventory_table(user_info['username'], user_info['password'], sort_by_unit_price=True)

    # Render the template with fetched data
    return render_template('view_inventory.html', inventory=inventory_data)


# Inventory Route (For managing inventory)
@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    if request.method == 'POST':
        # Handle inventory-related actions here (e.g., adding, updating inventory)
        flash("Inventory management functionality here.")
    
    # Render the inventory management page
    return render_template('inventory.html')

# Route to view inventory with sorting options
@app.route('/view_inventory', methods=['GET', 'POST'])
def view_inventory():
    # Get the sorting option from the request (default is 'balance_on_hand')
    sort_by = request.args.get('sort_by', 'balance_on_hand')

    # Get the stored user credentials (assuming they are temporarily stored)
    user_info = credentials_storage.get(list(credentials_storage.keys())[0])  # Retrieve the first stored credentials
    if not user_info:
        flash("Could not retrieve credentials. Please log in again.")
        return redirect(url_for('login'))

    # Fetch the inventory data with the selected sorting option
    inventory_data = view_inventory_table(user_info['username'], user_info['password'], sort_by)

    # Render the view_inventory.html template with the fetched data
    return render_template('view_inventory.html', inventory=inventory_data, sort_by=sort_by)





# View Profit Table Route
@app.route('/view_profit')
def view_profit():
    profit_data = view_profit_table()
    return render_template('view_profit.html', profit=profit_data)

# Route for managing prescribers (coming soon)
@app.route('/prescribers')
def prescribers():
    return render_template('prescriber.html')  # Display coming soon page for prescribers

# Patients Route (For managing patients)
@app.route('/patients', methods=['GET', 'POST'])
def patients():
    return render_template('patients.html')

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