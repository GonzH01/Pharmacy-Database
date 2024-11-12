# **Pharmacy Management System**

## **Description**
A web-based application designed to manage patient information, medication records, and inventory in a pharmacy setting. This system provides functionality for adding, viewing, editing, and removing patient and prescription details, as well as tracking medication inventory with streamlined authentication features.


**Quick Demo**

https://github.com/user-attachments/assets/59e16c11-83f3-4b63-8e25-a11016afbdc8



## **Features**
- **Patient Management**
    - Add, view, and search patient profiles.
    - Record allergies, conditions, and personal information.
  
- **Medication Management**
    - Add new prescriptions with details such as drug name, strength, quantity, days' supply, refills, and expiration dates.
    - Edit existing prescriptions and paginate through medication lists (9 per page).
  
- **Inventory Management**
    - Track inventory levels and update stock for medications.
    - Check and auto-populate NDC details based on pre-existing records.

- **Authentication**
    - Secure access with a 4-digit credential system to manage actions like adding and editing records.

## **Coming Soon**
- **Employee Management**
    - On first login, the admin will sign in with MySQL database credentials to enable employee management features.
    - **Add New Employee**: Allows admins to add employees with specific privileges. Once configured, only admins will see this button.
  
- **Patient**
    - **Add Edit Patient** as an option to the patient search results.
    - **Add Doctor** to the medication list table.
    - **Inactive Option (I#)**: View-only mode that greys out medications without allowing edits or deletions.
    - **Delete Function (D#)** and **View Details Function (V#)** options in the patient profile search bar, along with **Edit Function (E#)**.
    - For **View Profile**: Additional columns for refills remaining and quantity remaining (prescribed + dispensed quantity).
  
- **Inventory**
    - **Edit Button** and **Delete Function** for medications on the inventory list.

- **Doctor**
    - Management similar to patients, with added fields: license number (DEA + NPI), expiration date, fax, license title.
    - Licenses will dictate the doctor’s ability to fill certain prescriptions (controls/non-controls).

## **Tech Stack**
- **Backend**: Python (Flask), SQL
- **Frontend**: HTML, CSS, JavaScript
- **Database**: MySQL
- **Environment**: Conda (pharmacy_env)

## **Getting Started**

### **Installation**
1. Clone the repository.
2. Set up a virtual environment.
3. Install dependencies.
4. Configure the `connect_to_database.py` file with your MySQL database credentials.

### **Running the Application**
1. Start the Flask server.
2. Open your web browser and navigate to the provided local server URL.

## **Usage**

- **Patient Page**: Use the Add Patient form to enter new patient data. Search and Edit options are available in the main patient view.
- **Inventory Management**: Access the Inventory tab to add and manage medications.
- **Prescription Management**: Add or edit prescriptions directly from the patient's profile page, with the option to paginate through medications.

## **Contributing**
1. Fork the repository.
2. Create a new branch for your feature.
3. Commit changes.
4. Push to the branch.
5. Open a Pull Request.

## **Acknowledgments**
- Flask documentation
- SQLAlchemy for database management

Feel free to submit issues, fork the repository, and create pull requests. Contributions are welcome! Star this repository if you wish to see more progress!
