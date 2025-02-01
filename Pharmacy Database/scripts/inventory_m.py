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
    """Handles new medication insertions while properly updating balances."""
    try:
        with connect_with_cleanup(username, password) as mydb:
            with mydb.cursor() as cursor:
                cursor.execute("SET SESSION innodb_lock_wait_timeout = 50")

                # ✅ Ensure inventory table exists
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    drug_name VARCHAR(10),
                    ndc_number VARCHAR(11),
                    dosage_form ENUM('tablet/capsule','liquid(ml)','each'),
                    strength VARCHAR(50),
                    quantity INT,
                    quantity_per_unit INT,
                    expiration_date DATE,
                    lot_number VARCHAR(10),
                    manufacturer_name VARCHAR(15),
                    unit_price DECIMAL(10,2),
                    phone_number BIGINT,
                    email VARCHAR(30),
                    fax BIGINT,
                    controlled_substance_status ENUM('Y','N'),
                    UNIQUE KEY unique_ndc_lot_exp (ndc_number, lot_number, expiration_date),
                    INDEX idx_ndc_number (ndc_number)
                )
                """)

                # ✅ Ensure transactions table exists
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

                # Check if the medication already exists
                cursor.execute("""
                SELECT quantity FROM inventory
                WHERE ndc_number = %s AND lot_number = %s AND expiration_date = %s
                """, (ndc, lot_number, expiration_date))
                existing_med = cursor.fetchone()

                if existing_med:
                    # If exists, update quantity
                    new_quantity = existing_med[0] + quantity
                    cursor.execute("""
                    UPDATE inventory
                    SET quantity = %s
                    WHERE ndc_number = %s AND lot_number = %s AND expiration_date = %s
                    """, (new_quantity, ndc, lot_number, expiration_date))

                    log_inventory_transaction(ndc, quantity, "restock", username, password)

                else:
                    # Insert new medication
                    cursor.execute("""
                    INSERT INTO inventory (drug_name, ndc_number, dosage_form, strength, quantity, quantity_per_unit,
                                           expiration_date, lot_number, manufacturer_name, unit_price, phone_number, email, fax,
                                           controlled_substance_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (drug_name, ndc, dosage_form, strength, quantity, quantity_per_unit, expiration_date, lot_number,
                          manufacturer_name, unit_price, phone_number, email, fax, controlled_substance_status))

                    log_inventory_transaction(ndc, quantity, "restock", username, password)

            mydb.commit()
            return f"{drug_name} added successfully."
    except Exception as e:
        print("Error adding inventory:", e)
        return "Inventory addition failed due to a system error."




def update_balance_table(username, password):
    """Correctly synchronize the balance table using inventory transactions instead of just inventory."""
    mydb = connect_to_database(username, password)
    if not mydb:
        print("Error connecting to the database.")
        return

    try:
        with mydb.cursor() as cursor:
            cursor.execute("SET SESSION innodb_lock_wait_timeout = 50")

            # Ensure balance table exists
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS balance (
                balance_id INT AUTO_INCREMENT PRIMARY KEY,
                ndc_number VARCHAR(11) UNIQUE,
                balance_on_hand INT DEFAULT 0,
                unit_cost DECIMAL(10, 2) DEFAULT 0.00,
                inventory_value DECIMAL(10, 2) DEFAULT 0.00,
                FOREIGN KEY (ndc_number) REFERENCES inventory(ndc_number) ON DELETE CASCADE
            )
            """)

            # Get the total balance per NDC from transactions
            cursor.execute("""
            SELECT t.ndc_number, 
                   COALESCE(SUM(t.change_in_balance), 0) AS total_balance, 
                   (SELECT i.unit_price 
                    FROM inventory i 
                    WHERE i.ndc_number = t.ndc_number 
                    ORDER BY i.expiration_date DESC 
                    LIMIT 1) AS latest_unit_cost
            FROM inventory_transactions t
            GROUP BY t.ndc_number
            """)

            inventory_items = cursor.fetchall()

            for item in inventory_items:
                ndc, new_balance, unit_cost = item
                unit_cost = unit_cost if unit_cost is not None else 0.00
                inventory_value = new_balance * unit_cost

                # Update balance table using ON DUPLICATE KEY UPDATE
                cursor.execute("""
                INSERT INTO balance (ndc_number, balance_on_hand, unit_cost, inventory_value)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    balance_on_hand = VALUES(balance_on_hand),
                    unit_cost = VALUES(unit_cost),
                    inventory_value = VALUES(inventory_value)
                """, (ndc, new_balance, unit_cost, inventory_value))

            mydb.commit()
    except Exception as e:
        mydb.rollback()
        print(f"Error updating balance table: {e}")
    finally:
        mydb.close()






def log_inventory_transaction(ndc_number, change_in_balance, transaction_type, username, password):
    """Logs inventory transactions and updates balance correctly."""
    mydb = connect_to_database(username, password)
    if not mydb:
        print("Error connecting to the database.")
        return

    try:
        with mydb.cursor() as cursor:
            # Insert transaction record
            cursor.execute("""
                INSERT INTO inventory_transactions (ndc_number, change_in_balance, transaction_type)
                VALUES (%s, %s, %s)
            """, (ndc_number, change_in_balance, transaction_type))

        mydb.commit()

        # ✅ Update the balance table immediately after logging the transaction
        update_balance_table(username, password)

        print(f"📌 Logged transaction: {ndc_number} {change_in_balance} {transaction_type}")
    except Exception as e:
        print(f"❌ Error logging inventory transaction: {e}")
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


def view_inventory_table(username, password, sort_by='inventory_value', sort_order='desc'):
    """View inventory with correct balance, price, and transaction data."""
    try:
        with connect_with_cleanup(username, password) as mydb:
            with mydb.cursor() as cursor:
                update_balance_table(username, password)

                # ✅ FIX: Ensure 'boh' is mapped to a real column name
                sort_column = {
                    'boh': 'balance_on_hand',   # Fix 'boh' issue
                    'unit_price': 'unit_cost',
                    'inventory_value': 'inventory_value'
                }.get(sort_by, 'balance_on_hand')

                sort_order = 'ASC' if sort_order.lower() == 'asc' else 'DESC'

                # ✅ FIX: Ensure correct GROUP BY syntax
                query = f"""
                SELECT 
                    MAX(i.drug_name) AS drug_name,
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

                total_inventory_value = sum(row[5] for row in rows if row[5] is not None)
                inventory_items_count = len(rows)

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
    """
    Generate CSV content from inventory data.
    """
    try:
        # Create a CSV output in memory
        output = StringIO()
        writer = csv.writer(output)
        
        # Write the CSV headers
        writer.writerow(["Drug Name", "NDC Number", "Strength", "Balance on Hand", "Unit Cost", "Inventory Value"])
        
        # Write the CSV rows, ensuring no NoneType values cause formatting errors
        for row in inventory_data:
            drug_name = row[0] if row[0] is not None else "N/A"
            ndc_number = row[1] if row[1] is not None else "N/A"
            strength = row[2] if row[2] is not None else "N/A"
            balance_on_hand = row[3] if row[3] is not None else 0
            unit_cost = float(row[4]) if row[4] is not None else 0.00
            inventory_value = float(row[5]) if row[5] is not None else 0.00

            writer.writerow([drug_name, ndc_number, strength, balance_on_hand, f"{unit_cost:.2f}", f"{inventory_value:.2f}"])

        return output.getvalue()
    
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return None

