import mysql.connector
from connect_to_database import connect_to_database
import random
from datetime import datetime

def calculate_age(dob):
    """Calculate age from dob (YYYYMMDD format)"""
    dob_str = str(dob)
    birth_date = datetime.strptime(dob_str, '%Y%m%d')
    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

def create_patient_profile(username, password, first_name, last_name, dob, gender, street, city, state, zip_code, delivery, phone):
    """Create a new patient profile in the database"""
    mydb = connect_to_database(username, password)
    if not mydb:
        return "Error connecting to the database."

    patient_ID = str(random.randint(10000, 99999))

    mycursor = mydb.cursor()

    # Create table if it doesn't exist with updated columns for city, state, and zip_code
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_ID VARCHAR(5) PRIMARY KEY,
            first_name VARCHAR(15),
            last_name VARCHAR(15),
            dob INT(8),
            gender VARCHAR(5),
            street VARCHAR(15),
            city VARCHAR(10),
            state VARCHAR(2),
            zip_code INT(5),
            delivery VARCHAR(3),
            pt_phonenumber BIGINT(10)
        )
    """)

    sql = """
    INSERT INTO patients (patient_ID, first_name, last_name, dob, gender, street, city, state, zip_code, delivery, pt_phonenumber)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    val = (patient_ID, first_name, last_name, dob, gender, street, city, state, zip_code, delivery, phone)
    mycursor.execute(sql, val)

    mydb.commit()

    return f"Patient {first_name} {last_name} has been added successfully."

def search_patients(username, password, name=None, dob=None, phone=None):
    """Search patients based on name, dob, or phone number"""
    mydb = connect_to_database(username, password)
    if not mydb:
        return "Error connecting to the database."

    mycursor = mydb.cursor()

    # Build the query dynamically based on available criteria
    query = "SELECT patient_ID, first_name, last_name, dob, pt_phonenumber, street, city, state FROM patients WHERE 1=1"
    values = []

    if name:
        last_name_part, first_name_part = name.split(',')
        query += " AND LOWER(first_name) LIKE %s AND LOWER(last_name) LIKE %s"
        values.append(f"{first_name_part.strip().lower()}%")
        values.append(f"{last_name_part.strip().lower()}%")

    if dob:
        query += " AND dob = %s"
        values.append(dob)

    if phone:
        query += " AND pt_phonenumber = %s"
        values.append(phone)

    mycursor.execute(query, tuple(values))
    result = mycursor.fetchall()

    return result

def get_patient_profile(username, password, patient_id):
    """Retrieve patient details and medication report"""
    mydb = connect_to_database(username, password)
    if not mydb:
        return "Error connecting to the database."

    mycursor = mydb.cursor()

    # Fetch patient profile
    mycursor.execute("SELECT * FROM patients WHERE patient_ID = %s", (patient_id,))
    profile = mycursor.fetchone()

    # Fetch patient medication report (assuming meds table exists)
    mycursor.execute("SELECT * FROM meds WHERE patient_ID = %s", (patient_id,))
    meds = mycursor.fetchall()

    # Calculate age
    dob = profile[3]  # Assuming dob is the 4th element
    age = calculate_age(dob)

    return profile, meds, age
