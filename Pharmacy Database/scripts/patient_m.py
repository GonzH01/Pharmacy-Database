import mysql.connector
import random
from connect_to_database import connect_to_database

def create_patient_profile(username, password, name, dob, gender, address, delivery, pt_pn):
    """Create a new patient profile in the database"""
    mydb = connect_to_database(username, password)
    if not mydb:
        return "Error connecting to the database."

    patient_ID = str(random.randint(10000, 99999))

    mycursor = mydb.cursor()
    # Create table if it doesn't exist
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_ID VARCHAR(5) PRIMARY KEY,
            pt_name VARCHAR(255),
            dob VARCHAR(10),
            gender VARCHAR(5),
            address VARCHAR(255),
            delivery VARCHAR(3),
            pt_phonenumber VARCHAR(15)
        )
    """)

    sql = """
    INSERT INTO patients (patient_ID, pt_name, dob, gender, address, delivery, pt_phonenumber)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    val = (patient_ID, name, dob, gender, address, delivery, pt_pn)
    mycursor.execute(sql, val)

    mydb.commit()

    return f"Patient {name} has been added successfully."


def view_all_patients(username, password):
    """Retrieve all patients from the database"""
    mydb = connect_to_database(username, password)
    if not mydb:
        return "Error connecting to the database."

    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM patients")
    rows = mycursor.fetchall()

    return rows
