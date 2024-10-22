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
        drug_name VARCHAR(255),
        ndc_number VARCHAR(11) UNIQUE,
        dosage_form ENUM('tablet/capsule','liquid(ml)','each'),
        strength VARCHAR(50),
        quantity INT,
        quantity_per_unit INT,
        expiration_date DATE,
        lot_number VARCHAR(50),
        manufacturer_name VARCHAR(255),
        unit_price DECIMAL(10,2),
        phone_number BIGINT,
        email VARCHAR(255),
        fax BIGINT,
        description TEXT,
        storage_requirements VARCHAR(255),
        controlled_substance_status ENUM('Y','N'),
        allergies_warnings TEXT
    )
    """)

    # Check if the NDC exists
    cursor.execute("SELECT quantity, quantity_per_unit, unit_price FROM inventory WHERE ndc_number = %s", (ndc,))
    existing_med = cursor.fetchone()

    if existing_med:
        # Update existing medication data
        new_quantity = existing_med[0] + quantity
        new_balance_on_hand = new_quantity * quantity_per_unit
        inventory_value = new_balance_on_hand * unit_price

        cursor.execute("""
        UPDATE inventory
        SET quantity = %s, expiration_date = %s, lot_number = %s
        WHERE ndc_number = %s
        """, (new_quantity, expiration_date, lot_number, ndc))

        update_balance(ndc, new_quantity, quantity_per_unit, unit_price, username, password)

        mydb.commit()
        return f"Medication {drug_name} updated successfully."
    else:
        # Insert new medication data
        cursor.execute("""
        INSERT INTO inventory (drug_name, ndc_number, dosage_form, strength, quantity, quantity_per_unit,
                               expiration_date, lot_number, manufacturer_name, unit_price, phone_number, email, fax,
                               description, storage_requirements, controlled_substance_status, allergies_warnings)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (drug_name, ndc, dosage_form, strength, quantity, quantity_per_unit, expiration_date, lot_number,
              manufacturer_name, unit_price, phone_number, email, fax, description, storage_requirements,
              controlled_substance_status, allergies_warnings))

        mydb.commit()

        # Calculate balance on hand and inventory value for new entry
        balance_on_hand = quantity * quantity_per_unit
        inventory_value = balance_on_hand * unit_price

        add_balance_entry(ndc, balance_on_hand, unit_price, inventory_value, username, password)

        return f"Medication {drug_name} added successfully."

def add_balance_entry(ndc, balance_on_hand, unit_cost, inventory_value, username=None, password=None):
    """Create the balance table and insert a new entry or update an existing one."""
    mydb = connect_to_database(username, password)
    if not mydb:
        return "Error connecting to the database."

    cursor = mydb.cursor()

    # Create the balance table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS balance (
        balance_id INT AUTO_INCREMENT PRIMARY KEY,
        ndc_number VARCHAR(11),
        balance_on_hand INT,
        unit_cost DECIMAL(10, 2),
        inventory_value DECIMAL(10, 2),
        FOREIGN KEY (ndc_number) REFERENCES inventory(ndc_number)
    )
    """)

    # Insert or update the balance entry
    cursor.execute("""
    INSERT INTO balance (ndc_number, balance_on_hand, unit_cost, inventory_value)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        balance_on_hand = VALUES(balance_on_hand),
        unit_cost = VALUES(unit_cost),
        inventory_value = VALUES(inventory_value)
    """, (ndc, balance_on_hand, unit_cost, inventory_value))

    mydb.commit()
    return f"Balance entry for NDC {ndc} added/updated successfully."

def update_balance(ndc, new_quantity, new_quantity_per_unit, unit_price, username=None, password=None):
    """Update the balance for a specific NDC."""
    mydb = connect_to_database(username, password)
    if not mydb:
        return "Error connecting to the database."

    cursor = mydb.cursor()

    # Calculate new balance on hand and inventory value
    new_balance_on_hand = new_quantity * new_quantity_per_unit
    new_inventory_value = new_balance_on_hand * unit_price

    # Update the balance entry
    cursor.execute("""
    UPDATE balance
    SET balance_on_hand = %s, inventory_value = %s
    WHERE ndc_number = %s
    """, (new_balance_on_hand, new_inventory_value, ndc))

    mydb.commit()

def check_ndc_in_inventory(ndc, username=None, password=None):
    """Check if the NDC exists in the inventory and return full details if it does."""
    mydb = connect_to_database(username, password)
    if not mydb:
        return None

    cursor = mydb.cursor(dictionary=True)
    cursor.execute("""
    SELECT drug_name, strength, dosage_form, manufacturer_name, 
           unit_price, phone_number, email, fax, description, 
           storage_requirements, controlled_substance_status
    FROM inventory WHERE ndc_number = %s
    """, (ndc,))
    result = cursor.fetchone()

    return result if result else None

def get_drug_by_ndc(ndc, username=None, password=None):
    """Retrieve drug details by NDC from the inventory table."""
    mydb = connect_to_database(username, password)
    if not mydb:
        return None

    cursor = mydb.cursor(dictionary=True)
    cursor.execute("""
    SELECT drug_name, unit_price, (quantity * quantity_per_unit) AS balance_on_hand
    FROM inventory WHERE ndc_number = %s
    """, (ndc,))
    result = cursor.fetchone()

    return result

def view_inventory_table(username, password):
    """View inventory data with unique NDCs, swapping NDC and drug name columns."""
    mydb = connect_to_database(username, password)
    if not mydb:
        return []

    cursor = mydb.cursor()

    # Fetch inventory data with unique NDCs, swapping NDC and drug name columns
    cursor.execute("""
    SELECT DISTINCT i.ndc_number, i.drug_name, b.balance_on_hand, b.unit_cost, b.inventory_value
    FROM inventory i
    LEFT JOIN balance b ON i.ndc_number = b.ndc_number
    GROUP BY i.ndc_number, i.drug_name, b.balance_on_hand, b.unit_cost, b.inventory_value
    """)

    rows = cursor.fetchall()
    return rows
