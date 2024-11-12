from connect_to_database import connect_to_database
from io import StringIO
import csv
import time

def connect_with_cleanup(username, password):
    """Securely establish a database connection with cleanup."""
    mydb = connect_to_database(username, password)
    if not mydb:
        raise Exception("Database connection failed.")
    return mydb


def create_tables_and_input_data(ndc, drug_name, dosage_form, strength, quantity, quantity_per_unit,
                                 expiration_date, lot_number, manufacturer_name, unit_price, phone_number, email, fax,
                                 controlled_substance_status, username, password):
    try:
        with connect_with_cleanup(username, password) as mydb:
            with mydb.cursor() as cursor:
                cursor.execute("SET SESSION innodb_lock_wait_timeout = 50")
                
                # Create the inventory table with specified column constraints
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    drug_name VARCHAR(10),  -- Limit drug name to 10 characters
                    ndc_number VARCHAR(11),
                    dosage_form ENUM('tablet/capsule','liquid(ml)','each'),
                    strength VARCHAR(50),
                    quantity INT,
                    quantity_per_unit INT,
                    expiration_date DATE,
                    lot_number VARCHAR(10),  -- Limit lot number to 10 characters
                    manufacturer_name VARCHAR(15),  -- Limit manufacturer name to 15 characters
                    unit_price DECIMAL(10,2),
                    phone_number BIGINT,
                    email VARCHAR(30),  -- Limit email to 30 characters
                    fax BIGINT,
                    controlled_substance_status ENUM('Y','N'),
                    UNIQUE KEY unique_ndc_lot_exp (ndc_number, lot_number, expiration_date),
                    INDEX idx_ndc_number (ndc_number)  -- Index for faster lookups
                )
                """)
                # Note: Removed UNIQUE constraint on ndc_number and added composite unique key

                # Check if the medication already exists with same NDC, lot number, and expiration date
                cursor.execute("""
                SELECT quantity FROM inventory
                WHERE ndc_number = %s AND lot_number = %s AND expiration_date = %s
                """, (ndc, lot_number, expiration_date))
                existing_med = cursor.fetchone()

                if existing_med:
                    # If exists, update the quantity
                    new_quantity = existing_med[0] + quantity
                    cursor.execute("""
                    UPDATE inventory
                    SET quantity = %s
                    WHERE ndc_number = %s AND lot_number = %s AND expiration_date = %s
                    """, (new_quantity, ndc, lot_number, expiration_date))

                    # Update balance table after modifying the inventory
                    update_balance_table(username, password)
                    mydb.commit()
                    return f"{drug_name} updated successfully."
                else:
                    # If not exists, insert a new row
                    cursor.execute("""
                    INSERT INTO inventory (drug_name, ndc_number, dosage_form, strength, quantity, quantity_per_unit,
                                           expiration_date, lot_number, manufacturer_name, unit_price, phone_number, email, fax,
                                           controlled_substance_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (drug_name, ndc, dosage_form, strength, quantity, quantity_per_unit, expiration_date, lot_number,
                          manufacturer_name, unit_price, phone_number, email, fax, controlled_substance_status))

                    # Update balance table after adding new inventory
                    update_balance_table(username, password)
                    mydb.commit()
                    return f"{drug_name} added successfully."
    except Exception as e:
        print("Error adding inventory:", e)
        return "Inventory addition failed due to a system error."


def update_balance_table(username, password):
    """Synchronize the balance table with the latest inventory quantities."""
    mydb = connect_to_database(username, password)
    if not mydb:
        return "Error connecting to the database."

    try:
        with mydb.cursor() as cursor:
            cursor.execute("SET SESSION innodb_lock_wait_timeout = 50")

            # Create the balance table if it doesn't exist
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS balance (
                balance_id INT AUTO_INCREMENT PRIMARY KEY,
                ndc_number VARCHAR(11) UNIQUE,
                balance_on_hand INT,
                unit_cost DECIMAL(10, 2),
                inventory_value DECIMAL(10, 2),
                FOREIGN KEY (ndc_number) REFERENCES inventory(ndc_number),
                INDEX idx_balance_ndc_number (ndc_number)
            )
            """)

            # Fetch total balance for each ndc_number
            cursor.execute("""
            SELECT ndc_number, SUM(quantity * quantity_per_unit) as total_balance, AVG(unit_price) as avg_unit_cost
            FROM inventory
            GROUP BY ndc_number
            """)
            inventory_items = cursor.fetchall()

            for item in inventory_items:
                ndc, balance_on_hand, unit_cost = item
                inventory_value = balance_on_hand * unit_cost

                # Update or insert the balance entry for each ndc_number
                cursor.execute("""
                INSERT INTO balance (ndc_number, balance_on_hand, unit_cost, inventory_value)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    balance_on_hand = VALUES(balance_on_hand),
                    unit_cost = VALUES(unit_cost),
                    inventory_value = VALUES(inventory_value)
                """, (ndc, balance_on_hand, unit_cost, inventory_value))

            mydb.commit()
    except Exception as e:
        mydb.rollback()
        print("Error updating balance table:", e)
    finally:
        mydb.close()


def check_ndc_in_inventory(ndc, username=None, password=None):
    """Check if the NDC exists in the inventory and return full details if it does."""
    mydb = connect_to_database(username, password)
    if not mydb:
        return None

    cursor = mydb.cursor(dictionary=True)
    cursor.execute("""
    SELECT drug_name, strength, dosage_form, manufacturer_name, 
           unit_price, phone_number, email, fax,
           controlled_substance_status
    FROM inventory WHERE ndc_number = %s
    LIMIT 1  -- Get one entry if multiple exist
    """, (ndc,))
    result = cursor.fetchone()

    return result if result else None


def view_inventory_table(username, password, sort_by='boh', sort_order='desc'):
    """View inventory with secure connection handling, sorting, and unique NDCs, including strength."""
    try:
        with connect_with_cleanup(username, password) as mydb:
            with mydb.cursor() as cursor:
                # Define the sorting column based on user input
                sort_column = {
                    'boh': 'balance_on_hand',
                    'unit_price': 'unit_cost',
                    'inventory_value': 'inventory_value'
                }.get(sort_by, 'balance_on_hand')

                # Ensure sort_order is valid
                sort_order = 'ASC' if sort_order.lower() == 'asc' else 'DESC'

                # Correct the column order for Drug Name and NDC Number
                query = f"""
                SELECT MAX(i.drug_name) AS drug_name,
                       i.ndc_number,
                       MAX(i.strength) AS strength,
                       COALESCE(SUM(b.balance_on_hand), 0) AS balance_on_hand, 
                       MAX(b.unit_cost) AS unit_cost, 
                       COALESCE(SUM(b.inventory_value), 0) AS inventory_value
                FROM inventory i
                LEFT JOIN balance b ON i.ndc_number = b.ndc_number
                GROUP BY i.ndc_number
                ORDER BY {sort_column} {sort_order}
                """
                
                cursor.execute(query)
                rows = cursor.fetchall()

                # Calculate total inventory value and item count for display
                total_inventory_value = sum(row[5] for row in rows if row[5] is not None)
                inventory_items_count = len(rows)

                # Debugging output for confirmation
                if not rows:
                    print("No inventory data retrieved or issue with query.")
                else:
                    print(f"Inventory Data Retrieved: {len(rows)} items")

                return rows, total_inventory_value, inventory_items_count
    except Exception as e:
        print("Error viewing inventory:", e)
        return [], 0, 0




def get_drug_by_ndc(ndc, username=None, password=None):
    """Retrieve drug details by NDC from the inventory table securely."""
    try:
        with connect_with_cleanup(username, password) as mydb:
            with mydb.cursor(dictionary=True) as cursor:
                cursor.execute("SET SESSION innodb_lock_wait_timeout = 50")
                cursor.execute("""
                SELECT drug_name, unit_price, (quantity * quantity_per_unit) AS balance_on_hand
                FROM inventory WHERE ndc_number = %s
                LIMIT 1  -- Get one entry if multiple exist
                """, (ndc,))
                return cursor.fetchone()
    except Exception as e:
        print("Error retrieving drug by NDC:", e)
        return None


def export_inventory_to_csv(inventory_data):
    """Export inventory data to a CSV format in memory."""
    try:
        # Create an in-memory file
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(["Drug Name", "NDC Number", "Strength", "Balance on Hand", "Unit Cost", "Inventory Value"])
        
        # Write data rows
        for med in inventory_data:
            writer.writerow([med[0], med[1], med[2], med[3], f"{med[4]:.2f}", f"{med[5]:.2f}"])
        
        # Return the CSV content
        return output.getvalue()
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return None
