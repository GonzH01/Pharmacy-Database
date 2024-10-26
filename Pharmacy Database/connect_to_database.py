import mysql.connector
from mysql.connector import Error

def connect_to_database(username, password, db_name=None):
    """Connect to the MySQL server and optionally a specific database."""
    try:
        if db_name:
            mydb = mysql.connector.connect(
                host="localhost",
                user=username,
                password=password,
                database=db_name
            )
        else:
            mydb = mysql.connector.connect(
                host="localhost",
                user=username,
                password=password
            )
        return mydb
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def database_exists(username, password, db_name):
    """Check if a database exists."""
    mydb = connect_to_database(username, password)
    if not mydb:
        return False

    cursor = mydb.cursor()
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    cursor.close()

    return any(db[0] == db_name for db in databases)

def create_database(username, password, db_name):
    """Create a new database."""
    mydb = connect_to_database(username, password)
    if not mydb:
        return False

    cursor = mydb.cursor()
    try:
        cursor.execute(f"CREATE DATABASE {db_name}")
        print(f"Database '{db_name}' created successfully.")
        return True
    except Error as e:
        print(f"Error creating database: {e}")
        return False
    finally:
        cursor.close()
