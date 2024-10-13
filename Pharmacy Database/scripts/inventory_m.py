from connect_to_database import connect_to_database

def create_tables_and_input_data(id_num, item, unit_price, quantity):
    """Create inventory and profit tables and insert inventory data"""
    mydb = connect_to_database()
    if not mydb:
        return "Error connecting to the database."
    
    cursor = mydb.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS inventory (id INT(8) PRIMARY KEY, item VARCHAR(255), unit_price FLOAT, quantity FLOAT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS profit (id INT(8), balance FLOAT, FOREIGN KEY (id) REFERENCES inventory(id))")

    cursor.execute("INSERT INTO inventory (id, item, unit_price, quantity) VALUES (%s, %s, %s, %s)", (id_num, item, unit_price, quantity))
    balance = unit_price * quantity
    cursor.execute("INSERT INTO profit (id, balance) VALUES (%s, %s)", (id_num, balance))

    mydb.commit()
    return f"Inventory {item} added successfully."


def view_inventory_table():
    """View the inventory table"""
    mydb = connect_to_database()
    if not mydb:
        return "Error connecting to the database."
    
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM inventory")
    rows = cursor.fetchall()
    
    return rows


def view_profit_table():
    """View the profit table"""
    mydb = connect_to_database()
    if not mydb:
        return "Error connecting to the database."
    
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM profit ORDER BY balance DESC")
    rows = cursor.fetchall()
    
    return rows
