import mysql.connector
from connect_to_database import connect_to_database
from datetime import datetime, date
import random

def connect_with_cleanup(username, password, db_name):
    """Establish and return a secure database connection with auto cleanup."""
    mydb = connect_to_database(username, password, db_name)
    if not mydb:
        raise Exception("Error connecting to the database.")
    return mydb


def calculate_age(dob):
    """Calculate age from dob (datetime.date format)"""
    if isinstance(dob, date):
        today = datetime.today().date()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    return "N/A"


def create_patient_profile(username, password, db_name, first_name, last_name, dob, gender, street, city, state, zip_code, delivery, phone, allergies, conditions):
    try:
        with connect_with_cleanup(username, password, db_name) as mydb:
            patient_ID = str(random.randint(10000, 99999))
            with mydb.cursor() as mycursor:
                # Create the patients table if it doesn't exist
                mycursor.execute("""
                    CREATE TABLE IF NOT EXISTS patients (
                        patient_ID VARCHAR(5) PRIMARY KEY,
                        first_name VARCHAR(15),
                        last_name VARCHAR(15),
                        dob DATE,
                        gender VARCHAR(5),
                        street VARCHAR(30),
                        city VARCHAR(10),
                        state VARCHAR(2),
                        zip_code INT,
                        delivery VARCHAR(3),
                        pt_phonenumber BIGINT,
                        allergies TEXT,
                        conditions TEXT
                    )
                """)
                
                # Insert the new patient profile securely
                sql = """
                INSERT INTO patients (patient_ID, first_name, last_name, dob, gender, street, city, state, zip_code, delivery, pt_phonenumber, allergies, conditions)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                mycursor.execute(sql, (patient_ID, first_name, last_name, dob, gender, street, city, state, zip_code, delivery, phone, allergies, conditions))

                # Create the meds table if it doesn't exist
                mycursor.execute("""
                    CREATE TABLE IF NOT EXISTS meds (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        patient_ID VARCHAR(5),
                        drug VARCHAR(255),
                        strength VARCHAR(50),  
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
        return f"Patient {first_name} {last_name} has been added successfully."
    except Exception as e:
        print("Error adding patient:", e)
        return "Failed to add patient due to a system error."



def search_patients(username, password, db_name, name=None, dob=None, phone=None):
    try:
        with connect_with_cleanup(username, password, db_name) as mydb:
            with mydb.cursor() as mycursor:
                query = "SELECT patient_ID, first_name, last_name, dob, pt_phonenumber, street, city, state FROM patients WHERE 1=1"
                values = []

                if name:
                    last_name_part, first_name_part = name.split(',')
                    if len(last_name_part.strip()) >= 3 and len(first_name_part.strip()) >= 3:
                        query += " AND LOWER(last_name) LIKE %s AND LOWER(first_name) LIKE %s"
                        values.append(f"{last_name_part.strip().lower()}%")
                        values.append(f"{first_name_part.strip().lower()}%")
                    else:
                        return []

                if dob:
                    query += " AND dob = %s"
                    values.append(dob)

                if phone:
                    query += " AND pt_phonenumber = %s"
                    values.append(phone)

                mycursor.execute(query, tuple(values))
                result = mycursor.fetchall()
                return result
    except Exception as e:
        print("Error during patient search:", e)
        return []


def get_patient_profile(username, password, db_name, patient_id, limit=9, offset=0):
    try:
        with connect_with_cleanup(username, password, db_name) as mydb:
            with mydb.cursor() as mycursor:
                # Fetch patient profile
                mycursor.execute("SELECT * FROM patients WHERE patient_ID = %s", (patient_id,))
                profile = mycursor.fetchone()
                if not profile:
                    return None, None, None

                # Calculate age securely without exposing dob
                age = calculate_age(profile[3]) if profile[3] else "N/A"

                # Fetch medication report with pagination
                mycursor.execute(
                    """
                    SELECT * FROM meds
                    WHERE patient_ID = %s
                    ORDER BY date_filled DESC
                    LIMIT %s OFFSET %s
                    """,
                    (patient_id, limit, offset)
                )
                meds = mycursor.fetchall()

            return profile, meds, age
    except Exception as e:
        print("Error retrieving patient profile:", e)
        return None, None, None


