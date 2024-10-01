import mysql.connector
from mysql.connector import Error

def connect_to_database(username, password):
    """Connect to the MySQL database and return the connection object."""
    try:
        mydb = mysql.connector.connect(
            host="localhost",         # Your MySQL server hostname (e.g., localhost)
            user=username,            # Use the provided username
            password=password,        # Use the provided password
            database="pharmacy"       # The database you're connecting to
        )
        return mydb
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
