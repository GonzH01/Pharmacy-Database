from connect_to_database import connect_to_database
from io import StringIO
import csv


def connect_with_cleanup(username, password):
    """Securely establish a database connection with cleanup."""
    mydb = connect_to_database(username, password)
    if not mydb:
        raise Exception("Database connection failed.")
    return mydb

def get_drug_by_ndc(ndc, username=None, password=None):
    """Retrieve drug details by NDC from the inventory table securely."""
    try:
        with connect_with_cleanup(username, password) as mydb:
            with mydb.cursor(dictionary=True) as cursor:
                cursor.execute("SET SESSION innodb_lock_wait_timeout = 50")
                cursor.execute("""
                SELECT drug_name, unit_price, balance_on_hand
                FROM inventory WHERE ndc_number = %s
                LIMIT 1  -- Get one entry if multiple exist
                """, (ndc,))
                return cursor.fetchone()
    except Exception as e:
        print("Error retrieving drug by NDC:", e)
        return None


def create_tables(ndc, drug_name, strength, quantity, quantity_per_unit,
                  expiration_date, lot_number, manufacturer_name, unit_price, phone_number, 
                  email, fax, controlled_substance_status, username, password):
    """Ensure tables exist and insert/update medication entries while correctly updating inventory."""

    mydb = connect_to_database(username, password)
    
    if not mydb:
        print("❌ Error: Database connection failed!")
        return "Error: Database connection failed"

    try:
        with mydb.cursor() as cursor:
            cursor.execute("SET SESSION innodb_lock_wait_timeout = 50")

            # ✅ Ensure inventory table exists (Stores only unique NDCs)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    drug_name VARCHAR(15),
                    ndc_number VARCHAR(11) UNIQUE,
                    strength VARCHAR(50),
                    balance_on_hand INT DEFAULT 0,
                    inventory_value DECIMAL(10,2) DEFAULT 0.00,
                    unit_price DECIMAL(10,2) DEFAULT 0.00
                )
            """)

            # ✅ Ensure inventory_entry table exists (Tracks individual transactions)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory_entry (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    drug_name VARCHAR(15),
                    ndc_number VARCHAR(11),
                    manufacturer_name VARCHAR(15),
                    strength VARCHAR(50),
                    quantity INT,
                    quantity_per_unit INT,
                    expiration_date DATE,
                    lot_number VARCHAR(10),
                    unit_price DECIMAL(10,2),
                    phone_number BIGINT,
                    email VARCHAR(30),
                    fax BIGINT,
                    controlled_substance_status ENUM('Y','N'),
                    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # ✅ Ensure balance table exists (Tracks balance and inventory value)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS balance (
                balance_id INT AUTO_INCREMENT PRIMARY KEY,
                ndc_number VARCHAR(11) UNIQUE,
                balance_on_hand INT DEFAULT 0,
                inventory_value DECIMAL(10,2) DEFAULT 0.00,
                unit_cost DECIMAL(10,2) DEFAULT 0.00,
                FOREIGN KEY (ndc_number) REFERENCES inventory(ndc_number) ON DELETE CASCADE
            )
            """)

            print(f"✅ Tables ensured successfully for NDC {ndc}")

            # ✅ Insert into inventory_entry (Stores transaction details)
            cursor.execute("""
            INSERT INTO inventory_entry (drug_name, ndc_number, strength, quantity, 
                                         quantity_per_unit, expiration_date, lot_number, 
                                         manufacturer_name, unit_price, phone_number, email, fax, controlled_substance_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (drug_name, ndc, strength, quantity, quantity_per_unit, expiration_date, 
                  lot_number, manufacturer_name, unit_price, phone_number, email, fax, controlled_substance_status))

            print(f"✅ {drug_name} entry added successfully to inventory_entry.")

            # ✅ Update balance table using inventory_entry data
            cursor.execute("""
            SELECT 
                ndc_number,
                SUM(quantity * quantity_per_unit) AS total_balance,
                MAX(unit_price) AS latest_unit_price
            FROM inventory_entry
            GROUP BY ndc_number
            """)

            inventory_data = cursor.fetchall()

            for ndc, total_balance, latest_unit_price in inventory_data:
                latest_unit_price = latest_unit_price if latest_unit_price is not None else 0.00
                inventory_value = total_balance * latest_unit_price

                cursor.execute("""
                INSERT INTO balance (ndc_number, balance_on_hand, unit_cost, inventory_value)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    balance_on_hand = VALUES(balance_on_hand),
                    unit_cost = VALUES(unit_cost),
                    inventory_value = VALUES(inventory_value);
                """, (ndc, total_balance, latest_unit_price, inventory_value))

            print("✅ Balance table updated successfully!")

            # ✅ Update inventory table to reflect the latest balance and unit price
            cursor.execute("""
            INSERT INTO inventory (drug_name, ndc_number, strength, balance_on_hand, inventory_value, unit_price)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                balance_on_hand = VALUES(balance_on_hand),
                inventory_value = VALUES(inventory_value),
                unit_price = VALUES(unit_price);
            """, (drug_name, ndc, strength, total_balance, inventory_value, latest_unit_price))

            print(f"✅ Inventory table updated successfully for {drug_name}.")

            mydb.commit()
            return f"{drug_name} added successfully."

    except Exception as e:
        mydb.rollback()
        print(f"❌ Error adding medication: {e}")
        return f"Error: {e}"

    finally:
        mydb.close()




def check_ndc_in_inventory(ndc, username=None, password=None):
    """Check if the NDC exists in the inventory_entry table and return full details if it does."""
    mydb = connect_to_database(username, password)
    if not mydb:
        return None

    cursor = mydb.cursor(dictionary=True)
    cursor.execute("""
    SELECT drug_name, strength, dosage_form, manufacturer_name, 
           unit_price, phone_number, email, fax,
           controlled_substance_status
    FROM inventory_entry WHERE ndc_number = %s
    LIMIT 1
    """, (ndc,))
    result = cursor.fetchone()

    return result if result else None



def log_inventory_transaction(ndc_number, change_in_balance, transaction_type, username, password):
    """Logs inventory transactions and updates balance correctly."""
    mydb = connect_to_database(username, password)
    if not mydb:
        print("Error connecting to the database.")
        return

    try:
        with mydb.cursor() as cursor:
            # ✅ Log only the change in stock, not the total balance!
            cursor.execute("""
                INSERT INTO inventory_transactions (ndc_number, change_in_balance, transaction_type)
                VALUES (%s, %s, %s)
            """, (ndc_number, change_in_balance, transaction_type))

        mydb.commit()

        # ✅ Ensure balance is updated after each transaction
        update_balance_table(username, password)

        print(f"📌 Logged transaction: {ndc_number} {change_in_balance} {transaction_type}")
    except Exception as e:
        print(f"❌ Error logging inventory transaction: {e}")
    finally:
        mydb.close()


def add_inventory_entry(ndc, quantity, quantity_per_unit, expiration_date, lot_number, username, password):
    """Add a new inventory entry and update balance correctly."""
    try:
        with connect_with_cleanup(username, password) as mydb:
            with mydb.cursor() as cursor:
                # Insert new inventory entry
                cursor.execute("""
                INSERT INTO inventory_entry (ndc_number, quantity, quantity_per_unit, expiration_date, lot_number)
                VALUES (%s, %s, %s, %s, %s)
                """, (ndc, quantity, quantity_per_unit, expiration_date, lot_number))

                # ✅ Update the balance after insertion
                update_balance_table(username, password)

            mydb.commit()
            print("✅ Inventory entry added and balance updated!")

    except Exception as e:
        print(f"❌ Error adding inventory entry: {e}")


def update_balance_table(username, password):
    """Synchronize balance and inventory tables using summed quantities from inventory_entry."""
    mydb = connect_to_database(username, password)
    if not mydb:
        print("Error connecting to the database.")
        return

    try:
        with mydb.cursor() as cursor:
            cursor.execute("SET SESSION innodb_lock_wait_timeout = 50")

            # ✅ Ensure balance table exists
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS balance (
                balance_id INT AUTO_INCREMENT PRIMARY KEY,
                ndc_number VARCHAR(11) UNIQUE,
                balance_on_hand INT DEFAULT 0,
                unit_cost DECIMAL(10,2) DEFAULT 0.00,
                inventory_value DECIMAL(10,2) DEFAULT 0.00,
                FOREIGN KEY (ndc_number) REFERENCES inventory(ndc_number) ON DELETE CASCADE
            )
            """)

            # ✅ Update Balance Table using inventory_entry data
            cursor.execute("""
            SELECT 
                ndc_number,
                SUM(quantity * quantity_per_unit) AS total_balance,
                MAX(unit_price) AS latest_unit_cost
            FROM inventory_entry
            GROUP BY ndc_number
            """)

            inventory_items = cursor.fetchall()

            for item in inventory_items:
                ndc, new_balance, unit_cost = item
                unit_cost = unit_cost if unit_cost is not None else 0.00
                inventory_value = new_balance * unit_cost

                cursor.execute("""
                INSERT INTO balance (ndc_number, balance_on_hand, unit_cost, inventory_value)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    balance_on_hand = VALUES(balance_on_hand),
                    unit_cost = VALUES(unit_cost),
                    inventory_value = VALUES(inventory_value)
                """, (ndc, new_balance, unit_cost, inventory_value))

            # ✅ Update Inventory Table to reflect balance_on_hand and inventory_value
            cursor.execute("""
            UPDATE inventory i
            JOIN balance b ON i.ndc_number = b.ndc_number
            SET i.balance_on_hand = b.balance_on_hand,
                i.inventory_value = b.inventory_value
            """)

            mydb.commit()
            print("✅ Balance and Inventory tables updated successfully!")

    except Exception as e:
        mydb.rollback()
        print(f"❌ Error updating balance and inventory tables: {e}")
    finally:
        mydb.close()





def view_inventory_table(username, password, sort_by='inventory_value', sort_order='desc'):
    """Retrieve unique NDC inventory data while summing balance_on_hand and inventory_value."""
    try:
        with connect_with_cleanup(username, password) as mydb:
            with mydb.cursor(dictionary=True) as cursor:
                update_balance_table(username, password)

                # Define correct column mapping
                sort_column = {
                    'boh': 'b.balance_on_hand',
                    'unit_price': 'i.unit_price',
                    'inventory_value': 'b.inventory_value'
                }.get(sort_by, 'b.balance_on_hand')

                sort_order = 'ASC' if sort_order.lower() == 'asc' else 'DESC'

                # ✅ **Fix: Ensure only unique NDCs are displayed while summing balance**
                query = f"""
                SELECT 
                    MAX(i.drug_name) AS drug_name,  -- Ensures one name per NDC
                    i.ndc_number,
                    MAX(i.strength) AS strength,  -- Ensures one strength per NDC
                    COALESCE(SUM(b.balance_on_hand), 0) AS balance_on_hand,  -- Summing balance
                    MAX(i.unit_price) AS unit_price,  -- Use the latest unit price
                    COALESCE(SUM(b.inventory_value), 0) AS inventory_value  -- Summing total inventory value
                FROM inventory i
                LEFT JOIN balance b ON i.ndc_number = b.ndc_number
                GROUP BY i.ndc_number
                ORDER BY {sort_column} {sort_order}
                """

                cursor.execute(query)
                rows = cursor.fetchall()

                # Calculate total inventory value correctly
                total_inventory_value = sum(row["inventory_value"] for row in rows if row["inventory_value"] is not None)
                inventory_items_count = len(rows)

                return rows, total_inventory_value, inventory_items_count
    except Exception as e:
        print(f"❌ Error viewing inventory: {e}")
        return [], 0, 0





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
            drug_name = row["drug_name"] if row["drug_name"] is not None else "N/A"
            ndc_number = row["ndc_number"] if row["ndc_number"] is not None else "N/A"
            strength = row["strength"] if row["strength"] is not None else "N/A"
            balance_on_hand = row["balance_on_hand"] if row["balance_on_hand"] is not None else 0
            unit_cost = float(row["unit_cost"]) if row["unit_cost"] is not None else 0.00
            inventory_value = float(row["inventory_value"]) if row["inventory_value"] is not None else 0.00

            writer.writerow([drug_name, ndc_number, strength, balance_on_hand, f"{unit_cost:.2f}", f"{inventory_value:.2f}"])

        return output.getvalue()
    
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return None
