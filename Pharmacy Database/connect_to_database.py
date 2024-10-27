import mysql.connector
from mysql.connector import Error

# Global variable to store the selected database name
selected_database = None

def connect_to_database(username, password, db_name=None):
    """Connect to the MySQL server and optionally a specific database."""
    global selected_database

    # Set the global selected_database if db_name is provided
    if db_name:
        selected_database = db_name

    try:
        # Attempt to connect to the MySQL server with the selected database
        mydb = mysql.connector.connect(
            host="localhost",
            user=username,
            password=password,
            database=selected_database
        )
        return mydb
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def database_exists(username, password, db_name):
    """Check if a database exists."""
    global selected_database
    mydb = connect_to_database(username, password)
    if not mydb:
        return False

    cursor = mydb.cursor()
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    cursor.close()

    # Check if the specified database exists
    if any(db[0] == db_name for db in databases):
        selected_database = db_name  # Set the global selected_database
        return True
    return False

def create_database(username, password, db_name):
    """Create a new database."""
    global selected_database
    mydb = connect_to_database(username, password)
    if not mydb:
        return False

    cursor = mydb.cursor()
    try:
        cursor.execute(f"CREATE DATABASE {db_name}")
        print(f"Database '{db_name}' created successfully.")
        selected_database = db_name  # Set the global selected_database
        return True
    except Error as e:
        print(f"Error creating database: {e}")
        return False
    finally:
        cursor.close()
