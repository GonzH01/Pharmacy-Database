from connect_to_database import connect_to_database

def create_tables_and_input_data(id_num, ndc_number, item, expiration_date, lot_number, unit_price, quantity, 
                                 manufacturer_name, phone_number, email, fax, username, password):
    """Create inventory table and insert medication data"""
    mydb = connect_to_database(username, password)
    if not mydb:
        return "Error connecting to the database."
    
    cursor = mydb.cursor()

    # Create the inventory table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INT PRIMARY KEY,
        ndc_number VARCHAR(11),
        item VARCHAR(255),
        expiration_date DATE,
        lot_number VARCHAR(50),
        unit_price DECIMAL(10, 2),
        quantity INT,
        manufacturer_name VARCHAR(255),
        phone_number BIGINT(10),
        email VARCHAR(255),
        fax BIGINT(10)
    )
    """)

    # Insert the new medication into the inventory table
    cursor.execute("""
    INSERT INTO inventory (id, ndc_number, item, expiration_date, lot_number, unit_price, quantity, manufacturer_name, phone_number, email, fax)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (id_num, ndc_number, item, expiration_date, lot_number, unit_price, quantity, manufacturer_name, phone_number, email, fax))

    mydb.commit()
    return f"Medication {item} added successfully."

def view_inventory_table(username, password):
    """View the inventory table"""
    mydb = connect_to_database(username, password)
    if not mydb:
        return "Error connecting to the database."
    
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM inventory")
    rows = cursor.fetchall()
    
    return rows

def view_profit_table(username, password):
    """View the profit table"""
    mydb = connect_to_database(username, password)
    if not mydb:
        return "Error connecting to the database."
    
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM profit ORDER BY balance DESC")
    rows = cursor.fetchall()
    
    return rows
