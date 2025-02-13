from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, make_response
from scripts.patient_m import (
    create_patient_profile, 
    search_patients, 
    get_patient_profile
)
from scripts.inventory_m import (
    create_tables,
    view_inventory_table,
    add_inventory_entry, 
    update_balance_table, 
    get_drug_by_ndc, 
    check_ndc_in_inventory, 
    export_inventory_to_csv  
)
from scripts.inventory_m import log_inventory_transaction  # Import function to log inventory changes

from connect_to_database import connect_to_database, database_exists, create_database, selected_database
from io import StringIO
import csv
import random
from datetime import datetime, timedelta
import os
import webbrowser
import threading
import time



# Global variables for MySQL credentials, database name, and credential storage
db_name = None
mysql_user = None
mysql_password = None
credentials_storage = {}  # Initialize the global dictionary for storing credentials

def selected_database():
    """Return the currently selected database name."""
    global db_name
    return db_name

def get_database_credentials():
    global db_name, mysql_user, mysql_password

    # Prompt for MySQL username and password
    mysql_user = input("Enter MySQL username: ").strip()
    mysql_password = input("Enter MySQL password: ").strip()

    # Attempt to verify connection with given username and password
    try:
        # Attempt a connection to MySQL without specifying a database
        connection = connect_to_database(mysql_user, mysql_password)
        connection.close()  # Close immediately if successful
    except Exception as e:
        # If connection fails, show error and exit immediately
        print(f"Connection invalid: {e}")
        print("Incorrect username/password. Please try again.")
        exit()  # Exit the program if the credentials are invalid

    # If credentials are valid, proceed to ask for database name
    db_name = input("Name of Database: ").strip()

    # Check if the database exists
    if database_exists(mysql_user, mysql_password, db_name):
        print(f"Database '{db_name}' exists.")
        credentials_code, expiration_time = generate_credentials(mysql_user, mysql_password, db_name)
    else:
        # Handle case where database does not exist
        create_new = input(f"Database '{db_name}' does not exist. Do you want to create a new database? (y/n): ").strip().lower()
        if create_new == 'y':
            if create_database(mysql_user, mysql_password, db_name):
                print(f"Database '{db_name}' created.")
                credentials_code, expiration_time = generate_credentials(mysql_user, mysql_password, db_name)
            else:
                print("Failed to create the database. Exiting.")
                exit()
        else:
            print("Exiting without creating a database.")
            exit()




def open_browser():
    """Open the default web browser for the Flask application."""
    time.sleep(1)  # Wait for a second to ensure the server is fully started
    webbrowser.open_new("http://localhost:5000")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'


# Define a custom Jinja2 filter for enumerate
def jinja_enumerate(iterable, start=0):
    return enumerate(iterable, start=start)

# Add the filter to the Flask app
app.jinja_env.filters['enumerate'] = jinja_enumerate

def generate_credentials(username, password, db_name):
    global credentials_storage  # Ensure we're modifying the global dictionary

    credentials_code = random.randint(1000, 9999)
    expiration_time = datetime.now() + timedelta(hours=24)

    # Store credentials with expiration time and db_name
    credentials_storage[credentials_code] = {
        'username': username,
        'password': password,
        'db_name': db_name,  # Include db_name
        'expires_at': expiration_time
    }

    return credentials_code, expiration_time




# Regularly clean up expired credentials to enhance security
def cleanup_expired_credentials():
    global credentials_storage
    current_time = datetime.now()
    to_remove = [key for key, value in credentials_storage.items() if value['expires_at'] < current_time]
    
    for key in to_remove:
        del credentials_storage[key]


def verify_credentials(entered_credentials):
    # Fetch the stored credentials based on the entered ones
    user_info = credentials_storage.get(int(entered_credentials))  # Ensure it's converted to int

    if user_info and 'db_name' not in user_info:
        user_info['db_name'] = selected_database()  # Correctly call selected_database()

    return user_info


# Ensure no caching for sensitive data
@app.after_request
def add_security_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route('/', methods=['GET', 'POST'])
def login():
    cleanup_expired_credentials()  # Clean up expired credentials on login

    if request.method == 'POST':
        # Get the username and password from the form without modifying it
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Try connecting to the database
        mydb = connect_to_database(username, password)
        if mydb:  # Successful connection
            credentials_code, expiration_time = generate_credentials(username, password, selected_database())  # Include db_name here
            flash(f"Your credentials are {credentials_code}. Expires in 24 hours: {expiration_time.strftime('%Y-%m-%d %I:%M:%S %p')}", category="credentials")
            return redirect(url_for('main_menu', credentials_code=credentials_code))  # Redirect to main menu with credentials
        else:
            flash("Incorrect Username/Password", category="login")
    
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



@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        # Extract the separate DOB fields and combine them to form the full date of birth
        dob_month = request.form.get('dob_month')
        dob_day = request.form.get('dob_day')
        dob_year = request.form.get('dob_year')
        dob = f"{dob_year}-{dob_month.zfill(2)}-{dob_day.zfill(2)}"  # Format as YYYY-MM-DD

        gender = request.form.get('gender')
        street = request.form.get('street')
        city = request.form.get('city')
        state = request.form.get('state')
        zip_code = request.form.get('zip_code')
        delivery = request.form.get('delivery')

        # Combine phone number fields
        phone_area = request.form.get('phone_area')
        phone_central = request.form.get('phone_central')
        phone_line = request.form.get('phone_line')
        phone = f"{phone_area}{phone_central}{phone_line}"

        allergies = request.form.get('allergies', 'None')  # Use 'None' if no allergies are provided
        conditions = request.form.get('conditions', 'None')  # Use 'None' if no conditions are provided

        # Get credentials entered by the user
        entered_credentials = request.form.get('credentials')
        user_info = verify_credentials(entered_credentials)

        # Ensure valid credentials
        if not user_info or 'db_name' not in user_info:
            flash("Invalid credentials or database not selected. Please try again.")
            return redirect(url_for('patients'))

        # Call the create_patient_profile function with all required arguments
        try:
            result = create_patient_profile(
                user_info['username'],
                user_info['password'],
                user_info['db_name'],  # Pass db_name
                first_name,
                last_name,
                dob,
                gender,
                street,
                city,
                state,
                zip_code,
                delivery,
                phone,
                allergies,
                conditions
            )
            # Redirect to 'patients' page with success flag for JavaScript alert
            return redirect(url_for('patients', success='true'))

        except Exception as e:
            # Handle errors if patient creation fails
            flash("An error occurred while adding the patient. Please try again.")
            print(f"Error adding patient: {e}")  # Optional: log the error for debugging
            return redirect(url_for('add_patient'))
            
    # Render the form if GET request
    return render_template('add_patient.html')



@app.route('/search_patient', methods=['POST'])
def search_patient():
    name = request.form.get('name')
    dob = request.form.get('dob')
    phone = request.form.get('phone')
    entered_credentials = request.form.get('credentials')  # Use get() to retrieve credentials without modifying request.form

    user_info = verify_credentials(entered_credentials)
    if not user_info or 'db_name' not in user_info:
        flash("Invalid or expired credentials, or no database selected. Please log in again.")
        return redirect(url_for('patients'))

    matching_patients = search_patients(
        user_info['username'],
        user_info['password'],
        user_info['db_name'], 
        name=name,
        dob=dob,
        phone=phone
    )

    # Render results without clearing request.form
    return render_template('search_results.html', patients=matching_patients)



@app.route('/view_patient/<patient_id>', methods=['GET', 'POST'])
def view_patient(patient_id):
    page = request.args.get('page', 1, type=int)  # Get page number from URL or default to 1
    limit = 9
    offset = (page - 1) * limit

    if request.method == 'POST':
        entered_credentials = request.form['credentials']
        user_info = verify_credentials(entered_credentials)
        if not user_info:
            flash("Invalid or expired credentials. Please try again.")
            return redirect(url_for('patients'))
    else:
        user_info = credentials_storage.get(list(credentials_storage.keys())[0])

    if not user_info:
        flash("Could not retrieve credentials. Please log in again.")
        return redirect(url_for('login'))

    # Fetch the patient profile, medications, and age with pagination
    patient_profile, medication_report, age = get_patient_profile(
        user_info['username'], user_info['password'], user_info['db_name'], patient_id, limit=limit, offset=offset
    )

    # Check if there is a next page
    has_next = len(medication_report) == limit

    return render_template(
        'view_profile.html',
        profile=patient_profile,
        meds=medication_report,
        age=age,
        page=page,
        has_next=has_next,
        enumerate=enumerate  # Pass enumerate to the template
    )




@app.route('/check_med', methods=['GET'])
def check_med():
    med_name = request.args.get('med_name')
    strength = request.args.get('strength')
    credentials = request.args.get('credentials')

    if not med_name or not credentials or not strength:
        return jsonify({'error': 'Invalid input parameters.'}), 400

    # Verify credentials
    user_info = verify_credentials(credentials)
    if not user_info:
        return jsonify({'error': 'Invalid or expired credentials.'}), 400

    username = user_info['username']
    password = user_info['password']

    # Connect to the database
    mydb = connect_to_database(username, password)
    if not mydb:
        return jsonify({'error': 'Error connecting to the database.'}), 500

    cursor = mydb.cursor(dictionary=True)

    # Query to find unique medications matching the name and strength, with aggregated BOH
    cursor.execute("""
        SELECT i.drug_name AS name, i.ndc_number AS ndc, i.strength, 
               COALESCE(SUM(b.balance_on_hand), 0) AS balance_on_hand
        FROM inventory i
        LEFT JOIN balance b ON i.ndc_number = b.ndc_number
        WHERE i.drug_name LIKE %s AND i.strength = %s
        GROUP BY i.ndc_number, i.drug_name, i.strength
        ORDER BY balance_on_hand DESC
        LIMIT 10
    """, (f"{med_name[:3]}%", strength))

    meds = cursor.fetchall()

    if not meds:
        return jsonify({'error': 'No matching medications found.'}), 404

    return jsonify({'meds': meds})





@app.route('/add_rx/<patient_id>', methods=['GET', 'POST'])
def add_rx(patient_id):
    if request.method == 'POST':
        # Get form data for the prescription
        ndc_number = request.form['ndc_number']
        drug = request.form['drug']
        strength = request.form.get('strength')  # Retrieve strength from form
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

        # Check if the strength field is populated for debugging
        if not strength:
            flash("Strength field is missing. Please select a medication.")
            return redirect(url_for('add_rx', patient_id=patient_id))

        # Insert the new prescription into the meds table
        mydb = connect_to_database(user_info['username'], user_info['password'])
        mycursor = mydb.cursor()

        sql = """
            INSERT INTO meds (patient_ID, drug, strength, quantity, days_supply, refills, date_written, date_expired, date_filled, ndc_number, sig)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (patient_id, drug, strength, quantity, days_supply, refills, date_written, date_expired, date_filled, ndc_number, sig)
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

        # Update the prescription details in the meds table
        sql = """
            UPDATE meds 
            SET drug=%s, quantity=%s, days_supply=%s, refills=%s, date_written=%s, date_expired=%s, date_filled=%s, sig=%s
            WHERE id=%s AND patient_ID=%s
        """
        values = (drug, quantity, days_supply, refills, date_written, date_expired, date_filled, sig, id, patient_id)
        mycursor.execute(sql, values)
        mydb.commit()

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

# Define the get_drug_by_ndc function with the updated inventory schema
def get_drug_by_ndc(ndc, username=None, password=None):
    mydb = connect_to_database(username, password)
    if not mydb:
        return None

    cursor = mydb.cursor(dictionary=True)
    cursor.execute("""
    SELECT drug_name, strength, dosage_form, manufacturer_name, unit_price, 
           phone_number, email, fax, controlled_substance_status, 
           (quantity * quantity_per_unit) AS balance_on_hand
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

    # Verify credentials
    user_info = verify_credentials(credentials)
    if not user_info:
        return jsonify({'error': 'Invalid or expired credentials.'}), 400

    username = user_info['username']
    password = user_info['password']

    # Check NDC in the database
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
            'controlled_substance_status': drug_details.get('controlled_substance_status', '')
        })
    else:
        return jsonify({'exists': False})

def log_inventory_transaction(ndc_number, change_in_balance, transaction_type, username, password):
    """
    Logs inventory changes into the inventory_transactions table.
    """
    mydb = connect_to_database(username, password)
    if not mydb:
        print("Error connecting to the database.")
        return

    try:
        with mydb.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory_transactions (
                    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
                    ndc_number VARCHAR(11) NOT NULL,
                    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    change_in_balance INT NOT NULL,
                    transaction_type ENUM('restock', 'dispense', 'adjustment') NOT NULL,
                    FOREIGN KEY (ndc_number) REFERENCES inventory(ndc_number) ON DELETE CASCADE
                )
            """)

            sql = """
                INSERT INTO inventory_transactions (ndc_number, change_in_balance, transaction_type)
                VALUES (%s, %s, %s)
            """
            values = (ndc_number, change_in_balance, transaction_type)
            cursor.execute(sql, values)
            mydb.commit()
    except Exception as e:
        print(f"Error logging inventory transaction: {e}")
    finally:
        mydb.close()


# Ensure balance is updated when adding or modifying medications in inventory
@app.route('/add_med', methods=['GET', 'POST'])
def add_med():
    if request.method == 'POST':
        try:
            # Retrieve form data, including credentials
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
            controlled_substance_status = request.form['controlled_substance_status']
            credentials = request.form['credentials']

            # Verify credentials
            user_info = verify_credentials(credentials)
            if not user_info:
                flash("Invalid or expired credentials. Please try again.")
                return redirect(url_for('add_med'))

            # Connect and insert data
            username = user_info['username']
            password = user_info['password']
            mydb = connect_to_database(username, password)

            if not mydb:
                flash("Error connecting to the database", 'error')
                return redirect(url_for('add_med'))

            with mydb.cursor() as cursor:
                cursor.execute("SET SESSION innodb_lock_wait_timeout = 50")

                # ✅ **Ensure the medication exists in inventory BEFORE adding it to inventory_entry**
                cursor.execute("SELECT COUNT(*) FROM inventory WHERE ndc_number = %s", (ndc,))
                inventory_exists = cursor.fetchone()[0]

                if not inventory_exists:
                    cursor.execute("""
                        INSERT INTO inventory (drug_name, ndc_number, strength, balance_on_hand, 
                                               inventory_value, unit_price)
                        VALUES (%s, %s, %s, 0, 0.00, %s)
                    """, (drug_name, ndc, strength, unit_price))
                    print(f"✅ {drug_name} added to inventory successfully!")

                # ✅ **Now insert into inventory_entry**
                cursor.execute("""
                    INSERT INTO inventory_entry (drug_name, ndc_number, manufacturer_name, strength, 
                                                 quantity, quantity_per_unit, expiration_date, 
                                                 lot_number, unit_price, phone_number, email, fax, 
                                                 controlled_substance_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (drug_name, ndc, manufacturer_name, strength, quantity, quantity_per_unit, 
                      expiration_date, lot_number, unit_price, phone_number, email, fax, 
                      controlled_substance_status))
                print(f"✅ {drug_name} entry added to inventory_entry.")

                # ✅ **Log inventory transaction**
                cursor.execute("""
                    INSERT INTO inventory_transactions (ndc_number, transaction_date, change_in_balance, transaction_type)
                    VALUES (%s, NOW(), %s, 'restock')
                """, (ndc, quantity * quantity_per_unit))
                print(f"✅ Inventory transaction logged for {drug_name}.")

                # ✅ **Update balance table**
                cursor.execute("""
                    INSERT INTO balance (ndc_number, balance_on_hand, inventory_value, unit_cost)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        balance_on_hand = balance_on_hand + VALUES(balance_on_hand),
                        inventory_value = inventory_value + VALUES(inventory_value)
                """, (ndc, quantity * quantity_per_unit, unit_price * (quantity * quantity_per_unit), unit_price))

                print(f"✅ Balance table updated successfully!")

                mydb.commit()
                flash(f"{drug_name} added successfully.", "success")
                return redirect(url_for('inventory', success='true'))

        except Exception as e:
            flash(f"An error occurred: {e}", "error")
            print(f"❌ Error adding medication: {e}")
            return redirect(url_for('add_med'))

        finally:
            if mydb:
                mydb.close()

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

@app.route('/view_inventory', methods=['GET', 'POST'])
def view_inventory():
    # Get credentials from request method
    credentials = request.form.get('credentials') if request.method == 'POST' else request.args.get('credentials')
    
    # Set sorting parameters with default values
    sort_by = request.args.get('sort_by', 'inventory_value')
    sort_order = request.args.get('sort_order', 'desc')

    # Verify credentials before accessing the database
    user_info = verify_credentials(credentials)
    if not user_info:
        flash("Invalid or expired credentials. Please log in again.")
        return redirect(url_for('inventory'))

    username = user_info['username']
    password = user_info['password']

    # ✅ Auto-update balance table before viewing inventory
    update_balance_table(username, password)

    # ✅ Fetch inventory data with sorting (ensuring unique NDCs)
    inventory_data, total_inventory_value, inventory_items_count = view_inventory_table(username, password, sort_by, sort_order)

    # Debugging output to confirm data retrieval
    if not inventory_data:
        print("❌ No inventory data retrieved or issue with query.")
    else:
        print(f"✅ Inventory Data Retrieved: {len(inventory_data)} items")

    # ✅ Render the template with unique inventory data
    return render_template(
        'view_inventory.html',
        inventory=inventory_data,
        total_inventory_value=total_inventory_value,
        inventory_items_count=inventory_items_count
    )


@app.route('/download_inventory_csv', methods=['POST'])
def download_inventory_csv():
    entered_credentials = request.form.get('credentials')

    # Check if credentials were provided
    if not entered_credentials:
        flash("Credentials are required to download the CSV.")
        return redirect(url_for('view_inventory'))

    # Verify credentials
    try:
        user_info = verify_credentials(entered_credentials)
    except ValueError:
        flash("Invalid credentials format. Please enter valid numeric credentials.")
        return redirect(url_for('view_inventory'))

    if not user_info:
        flash("Invalid or expired credentials. Please try again.")
        return redirect(url_for('view_inventory'))

    # Fetch inventory data
    inventory_data, total_inventory_value, inventory_items_count = view_inventory_table(
        user_info['username'], user_info['password']
    )

    # Generate CSV content in memory
    csv_content = export_inventory_to_csv(inventory_data)
    if not csv_content:
        flash("Failed to generate CSV content.")
        return redirect(url_for('view_inventory'))

    # Create a response for CSV download
    response = make_response(csv_content)
    response.headers['Content-Disposition'] = 'attachment; filename=inventory_data.csv'
    response.headers['Content-Type'] = 'text/csv'

    return response




# Route for managing prescribers (coming soon)
@app.route('/prescribers')
def prescribers():
    return render_template('prescriber.html')  # Display coming soon page for prescribers

# Patients Route (For managing patients)
@app.route('/patients', methods=['GET', 'POST'])
def patients():
    return render_template('patients.html')

@app.route('/dashboards', methods=['GET'])
def dashboards():
    credentials = request.args.get('credentials')
    user_info = verify_credentials(credentials)
    if not user_info:
        flash("Invalid or expired credentials. Please log in again.")
        return redirect(url_for('inventory'))

    username = user_info['username']
    password = user_info['password']

    mydb = connect_to_database(username, password)
    if not mydb:
        flash("Error connecting to the database.")
        return redirect(url_for('inventory'))

    try:
        with mydb.cursor(dictionary=True) as cursor:
            # ✅ Total Inventory Value Over Time
            cursor.execute("""
                SELECT DATE(t.transaction_date) AS date, 
                       SUM(t.change_in_balance * COALESCE(i.unit_price, 0.00)) AS total_inventory_value
                FROM inventory_transactions t
                LEFT JOIN inventory i ON t.ndc_number = i.ndc_number
                GROUP BY DATE(t.transaction_date)
                ORDER BY DATE(t.transaction_date) ASC
            """)
            results = cursor.fetchall()
            dates = [row["date"].strftime('%Y-%m-%d') for row in results]
            total_values = [row["total_inventory_value"] if row["total_inventory_value"] else 0 for row in results]

            # ✅ Monthly Inventory Movement
            cursor.execute("""
                SELECT DATE_FORMAT(t.transaction_date, '%Y-%m') AS month, 
                    SUM(CASE WHEN t.change_in_balance > 0 THEN t.change_in_balance ELSE 0 END) AS total_items,
                    SUM(t.change_in_balance * COALESCE(i.unit_price, 0.00)) AS total_price
                FROM inventory_transactions t
                LEFT JOIN inventory i ON t.ndc_number = i.ndc_number
                WHERE t.transaction_date IS NOT NULL
                GROUP BY month
                ORDER BY month ASC
            """)
            movement_results = cursor.fetchall()

            months = [row["month"] for row in movement_results]
            net_changes = [row["total_items"] for row in movement_results]
            monthly_inventory_prices = [float(row["total_price"]) for row in movement_results]

            # ✅ Retrieve Price vs. Inventory Value Scatter Data with Strength
            cursor.execute("""
                SELECT i.drug_name, i.strength, 
                    COALESCE(i.unit_price, 0.00) AS unit_price, 
                    COALESCE(i.inventory_value, 0.00) AS inventory_value, 
                    COALESCE(i.balance_on_hand, 0) AS balance_on_hand
                FROM inventory i
                WHERE i.inventory_value > 0
            """)
            scatter_results = cursor.fetchall()

            scatter_data = [
                {
                    "x": float(row["unit_price"]), 
                    "y": float(row["inventory_value"]), 
                    "drug_name": row["drug_name"], 
                    "strength": row["strength"], 
                    "unit_price": float(row["unit_price"]), 
                    "balance_on_hand": row["balance_on_hand"]
                }
                for row in scatter_results
            ]



            # ✅ Top 5 Inventory Valued Medications + "Other"
            cursor.execute("""
                SELECT i.drug_name, i.strength, SUM(i.inventory_value) AS value
                FROM inventory i
                GROUP BY i.drug_name, i.strength
                ORDER BY value DESC
                LIMIT 5
            """)
            top_inventory_value_results = cursor.fetchall()

            # ✅ Extract values into lists
            top_inventory_value_labels = [row["drug_name"] for row in top_inventory_value_results]
            top_inventory_value_values = [float(row["value"]) for row in top_inventory_value_results]
            top_inventory_value_strengths = [row["strength"] for row in top_inventory_value_results]

            # ✅ Calculate "Other" category
            cursor.execute("""
                SELECT 'Other' AS drug_name, NULL AS strength, SUM(i.inventory_value) AS value
                FROM inventory i
                WHERE i.drug_name NOT IN (
                    SELECT drug_name FROM (
                        SELECT i.drug_name FROM inventory i
                        GROUP BY i.drug_name
                        ORDER BY SUM(i.inventory_value) DESC
                        LIMIT 5
                    ) AS subquery
                )
            """)
            other_inventory_value = cursor.fetchone()
            if other_inventory_value:
                top_inventory_value_labels.append(other_inventory_value["drug_name"])
                top_inventory_value_values.append(other_inventory_value["value"])
                top_inventory_value_strengths.append("")  # ✅ Use empty string for "Other"



            
            # ✅ Initialize lists to avoid undefined variables
            top_quantity_labels = []
            top_quantity_values = []
            top_quantity_strengths = []

            # ✅ Fetch Top 5 Inventory by Quantity
            cursor.execute("""
                SELECT i.drug_name, i.strength, SUM(i.balance_on_hand) AS value
                FROM inventory i
                WHERE i.balance_on_hand > 0
                GROUP BY i.drug_name, i.strength
                ORDER BY value DESC
                LIMIT 5
            """)
            top_quantity_results = cursor.fetchall()
            
            # ✅ Assign values to lists, ensuring no NULLs in strength
            top_quantity_labels = [row["drug_name"] for row in top_quantity_results]
            top_quantity_values = [float(row["value"]) for row in top_quantity_results]
            top_quantity_strengths = [row["strength"] if row["strength"] is not None else "N/A" for row in top_quantity_results]

            # ✅ Handle "Other" category separately
            cursor.execute("""
                SELECT 'Other' AS drug_name, NULL AS strength, SUM(i.balance_on_hand) AS value
                FROM inventory i
                WHERE i.drug_name NOT IN (
                    SELECT drug_name FROM (
                        SELECT i.drug_name FROM inventory i
                        GROUP BY i.drug_name
                        ORDER BY SUM(i.balance_on_hand) DESC
                        LIMIT 5
                    ) AS subquery
                )
            """)
            other_quantity = cursor.fetchone()

            if other_quantity and other_quantity["value"] > 0:
                top_quantity_labels.append(other_quantity["drug_name"])
                top_quantity_values.append(float(other_quantity["value"]))  # ✅ Convert Decimal to float
                top_quantity_strengths.append("")  # ✅ Empty string for "Other"

                       
            # ✅ Get Current Month's Totals
            cursor.execute("""
                SELECT SUM(balance_on_hand) AS total_items, SUM(inventory_value) AS total_price
                FROM inventory
            """)
            current_month_totals = cursor.fetchone()
            current_total_items = float(current_month_totals["total_items"]) if current_month_totals["total_items"] else 0
            current_total_price = float(current_month_totals["total_price"]) if current_month_totals["total_price"] else 0

            # ✅ Get Last Month's Totals
            cursor.execute("""
                SELECT SUM(balance_on_hand) AS total_items, SUM(inventory_value) AS total_price
                FROM inventory
                WHERE ndc_number IN (
                    SELECT DISTINCT ndc_number FROM inventory_transactions
                    WHERE transaction_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 2 MONTH) 
                    AND DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
                )
            """)
            last_month_totals = cursor.fetchone()
            last_month_items = float(last_month_totals["total_items"]) if last_month_totals["total_items"] else 0
            last_month_price = float(last_month_totals["total_price"]) if last_month_totals["total_price"] else 0

            # ✅ Fix Percentage Change Calculation (Avoid Division by Zero)
            items_change = ((current_total_items - last_month_items) / last_month_items) * 100 if last_month_items > 0 else 0
            price_change = ((current_total_price - last_month_price) / last_month_price) * 100 if last_month_price > 0 else 0

            # ✅ Ensure no undefined variables are passed
            scatter_data = scatter_data if 'scatter_data' in locals() else []
            months = months if 'months' in locals() else []
            net_changes = [int(row["total_items"]) for row in movement_results]
            dates = dates if 'dates' in locals() else []
            total_values = [float(row["total_inventory_value"]) for row in results]



            return render_template(
                "dashboards.html",
                dates=dates,
                total_values=total_values,
                months=months,
                net_changes=net_changes,
                monthly_inventory_prices=monthly_inventory_prices,
                scatter_data=scatter_data,
                top_inventory_value_labels=top_inventory_value_labels,  # ✅ Updated
                top_inventory_value_values=top_inventory_value_values,  # ✅ Updated
                top_inventory_value_strengths=top_inventory_value_strengths,  # ✅ Updated
                top_quantity_labels=top_quantity_labels,
                top_quantity_values=top_quantity_values,
                top_quantity_strengths=top_quantity_strengths,
                items_change=round(items_change, 2),
                price_change=round(price_change, 2)
)



    except Exception as e:
        flash(f"Error retrieving dashboard data: {e}")
        print(f"❌ Error retrieving dashboard data:", e)
        return redirect(url_for('inventory'))

    finally:
        mydb.close()





# Sign Off Route (Sign off and return to login screen)
@app.route('/sign_off')
def sign_off():
    global credentials_storage
    # Clear credentials and return to login screen
    credentials_storage.clear()
    flash("You have been signed off.")
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Prompt the user for the database credentials before running the app
    get_database_credentials()
    
    # Start a new thread to open the browser once the server is ready
    threading.Thread(target=open_browser, daemon=True).start()

    # Start the Flask app without debug mode
    app.run(use_reloader=False)
