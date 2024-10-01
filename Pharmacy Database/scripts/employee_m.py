from connect_to_database import connect_to_database

def create_employee_table(employee_ID, name, phone_number, return_amount, date_hired):
    """Create an employee profile and return record in the database"""
    mydb = connect_to_database()
    if not mydb:
        return "Error connecting to the database."
    
    mycursor = mydb.cursor()
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS employee (
            employee_ID INT(5) UNSIGNED PRIMARY KEY,
            name VARCHAR(25),
            phone_number VARCHAR(20)
        )
    """)

    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS amount_returns (
            employee_ID INT(5) UNSIGNED,
            return_amount DECIMAL(10, 2),
            date_hired VARCHAR(10),
            FOREIGN KEY (employee_ID) REFERENCES employee(employee_ID)
        )
    """)
    
    mycursor.execute("INSERT INTO employee (employee_ID, name, phone_number) VALUES (%s, %s, %s)", (employee_ID, name, phone_number))
    mycursor.execute("INSERT INTO amount_returns (employee_ID, return_amount, date_hired) VALUES (%s, %s, %s)", (employee_ID, return_amount, date_hired))
    
    mydb.commit()
    return f"Employee {name} added successfully."


def view_employee():
    """Retrieve all employee records"""
    mydb = connect_to_database()
    if not mydb:
        return "Error connecting to the database."
    
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM employee")
    rows = mycursor.fetchall()
    
    return rows


def view_cash_returns():
    """Retrieve employee returns records"""
    mydb = connect_to_database()
    if not mydb:
        return "Error connecting to the database."
    
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM amount_returns ORDER BY return_amount DESC")
    rows = mycursor.fetchall()
    
    return rows
