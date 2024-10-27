import mysql.connector
from connect_to_database import connect_to_database
import random
from datetime import datetime

def calculate_age(dob):
    """Calculate age from dob (YYYYMMDD format)"""
    try:
        dob = int(dob)  # Ensure dob is an integer
        dob_str = f"{dob:08d}"  # Pad dob to 8 digits if needed
        birth_date = datetime.strptime(dob_str, '%Y%m%d')
        today = datetime.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except (ValueError, TypeError):
        return None  # Return None if dob is invalid

def create_patient_profile(username, password, db_name, first_name, last_name, dob, gender, street, city, state, zip_code, delivery, phone, allergies, conditions):
    """Create a new patient profile and ensure the meds table exists"""
    mydb = connect_to_database(username, password, db_name)
    if not mydb:
        return "Error connecting to the database."

    patient_ID = str(random.randint(10000, 99999))
    mycursor = mydb.cursor()

    # Create the patients table if it doesn't exist
    mycursor.execute(f"""
        CREATE TABLE IF NOT EXISTS patients (
            patient_ID VARCHAR(5) PRIMARY KEY,
            first_name VARCHAR(15),
            last_name VARCHAR(15),
            dob INT(8),
            gender VARCHAR(5),
            street VARCHAR(30),
            city VARCHAR(10),
            state VARCHAR(2),
            zip_code INT(5),
            delivery VARCHAR(3),
            pt_phonenumber BIGINT(10),
            allergies TEXT,
            conditions TEXT
        )
    """)

    # Insert the new patient into the patients table
    sql = """
    INSERT INTO patients (patient_ID, first_name, last_name, dob, gender, street, city, state, zip_code, delivery, pt_phonenumber, allergies, conditions)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    val = (patient_ID, first_name, last_name, dob, gender, street, city, state, zip_code, delivery, phone, allergies, conditions)
    mycursor.execute(sql, val)

    # Create the meds table if it doesn't exist, including the sig column
    mycursor.execute(f"""
        CREATE TABLE IF NOT EXISTS meds (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_ID VARCHAR(5),
            drug VARCHAR(255),
            quantity INT,
            days_supply INT,
            refills INT,
            date_written DATE,
            date_expired DATE,
            date_filled DATE,
            ndc_number VARCHAR(11),
            sig VARCHAR(150),
            FOREIGN KEY (patient_ID) REFERENCES patients(patient_ID)
        )
    """)

    mydb.commit()
    return f"Patient {first_name} {last_name} has been added successfully and meds table is ready."

def search_patients(username, password, db_name, name=None, dob=None, phone=None):
    """Search patients based on name, dob, or phone number"""
    mydb = connect_to_database(username, password, db_name)
    if not mydb:
        return "Error connecting to the database."

    mycursor = mydb.cursor()

    # Build the query dynamically based on available criteria
    query = "SELECT patient_ID, first_name, last_name, dob, pt_phonenumber, street, city, state FROM patients WHERE 1=1"
    values = []

    if name:
        if ',' in name:  # Expecting 'Last, First' format
            last_name_part, first_name_part = name.split(',')
            if len(last_name_part.strip()) >= 3 and len(first_name_part.strip()) >= 3:
                query += " AND LOWER(last_name) LIKE %s AND LOWER(first_name) LIKE %s"
                values.append(f"{last_name_part.strip().lower()}%")
                values.append(f"{first_name_part.strip().lower()}%")
            else:
                return "Error: Please enter a last name and first name with at least 3 characters each."
        else:
            return "Error: Please enter name in 'Last, First' format."

    if dob:
        query += " AND dob = %s"
        values.append(dob)

    if phone:
        query += " AND pt_phonenumber = %s"
        values.append(phone)

    mycursor.execute(query, tuple(values))
    result = mycursor.fetchall()

    return result

def get_patient_profile(username, password, db_name, patient_id):
    """Retrieve patient details and medication report"""
    mydb = connect_to_database(username, password, db_name)
    if not mydb:
        return "Error connecting to the database.", None, None

    mycursor = mydb.cursor()

    # Fetch patient profile
    mycursor.execute("SELECT * FROM patients WHERE patient_ID = %s", (patient_id,))
    profile = mycursor.fetchone()

    if not profile:
        return "Patient not found.", None, None

    # Fetch patient medication report
    mycursor.execute("SELECT * FROM meds WHERE patient_ID = %s", (patient_id,))
    meds = mycursor.fetchall()

    dob = profile[3]  # Assuming dob is in profile[3]
    age = calculate_age(dob)

    return profile, meds, age
