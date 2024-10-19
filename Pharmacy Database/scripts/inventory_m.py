from connect_to_database import connect_to_database

def create_tables_and_input_data(ndc, drug_name, dosage_form, strength, quantity, quantity_per_unit,
                                 expiration_date, lot_number, manufacturer_name, unit_price, phone_number, email, fax,
                                 description, storage_requirements, controlled_substance_status, allergies_warnings,
                                 username, password):
    """Create the inventory table and insert medication data."""
    mydb = connect_to_database(username, password)
    if not mydb:
        return "Error connecting to the database."

    cursor = mydb.cursor()

    # Create the inventory table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ndc_number VARCHAR(11),
        drug_name VARCHAR(255),
        dosage_form VARCHAR(50),
        strength VARCHAR(50),
        quantity INT,
        quantity_per_unit VARCHAR(50),
        expiration_date DATE,
        lot_number VARCHAR(50),
        manufacturer_name VARCHAR(255),
        unit_price DECIMAL(10, 2),
        phone_number BIGINT,
        email VARCHAR(255),
        fax BIGINT,
        description TEXT,
        storage_requirements VARCHAR(255),
        controlled_substance_status VARCHAR(10),
        allergies_warnings TEXT
    )
    """)

    # Insert the new medication into the inventory table
    cursor.execute("""
    INSERT INTO inventory (ndc_number, drug_name, dosage_form, strength, quantity, quantity_per_unit,
                           expiration_date, lot_number, manufacturer_name, unit_price, phone_number, email, fax,
                           description, storage_requirements, controlled_substance_status, allergies_warnings)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (ndc, drug_name, dosage_form, strength, quantity, quantity_per_unit, expiration_date, lot_number,
          manufacturer_name, unit_price, phone_number, email, fax, description, storage_requirements,
          controlled_substance_status, allergies_warnings))

    mydb.commit()
    return f"Medication {drug_name} added successfully."

def view_inventory_table(username, password):
    """View all inventory data."""
    mydb = connect_to_database(username, password)
    if not mydb:
        return "Error connecting to the database."

    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM inventory")
    rows = cursor.fetchall()

    return rows

def get_filtered_inventory(filter_option, username, password):
    """Retrieve inventory data based on the filter option."""
    mydb = connect_to_database(username, password)
    if not mydb:
        return "Error connecting to the database."

    cursor = mydb.cursor()

    # Apply different filters based on the filter_option
    if filter_option == 'quantity_high_to_low':
        cursor.execute("SELECT * FROM inventory ORDER BY quantity DESC")
    elif filter_option == 'quantity_low_to_high':
        cursor.execute("SELECT * FROM inventory ORDER BY quantity ASC")
    elif filter_option == 'most_expensive':
        cursor.execute("SELECT * FROM inventory ORDER BY unit_price DESC")
    elif filter_option == 'least_expensive':
        cursor.execute("SELECT * FROM inventory ORDER BY unit_price ASC")
    elif filter_option == 'controlled_only':
        cursor.execute("SELECT * FROM inventory WHERE controlled_substance_status = 'y'")
    elif filter_option == 'non_controlled_only':
        cursor.execute("SELECT * FROM inventory WHERE controlled_substance_status = 'n'")
    elif filter_option == 'expiration_soon':
        cursor.execute("SELECT * FROM inventory WHERE expiration_date <= CURDATE() + INTERVAL 30 DAY ORDER BY expiration_date ASC")
    else:
        cursor.execute("SELECT * FROM inventory")

    rows = cursor.fetchall()

    return rows

def view_profit_table(username, password):
    """View the profit table."""
    mydb = connect_to_database(username, password)
    if not mydb:
        return "Error connecting to the database."

    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM profit ORDER BY balance DESC")
    rows = cursor.fetchall()

    return rows
