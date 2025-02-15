# **Pharmacy Management System**

## **Description**
A web-based application designed to manage patient information, medication records, and inventory in a pharmacy setting. This system provides functionality for adding, viewing, editing, and removing patient and prescription details, as well as tracking medication inventory with streamlined authentication features.


**Quick Demo**


https://github.com/user-attachments/assets/be7bddd0-1d69-4bc3-b446-d8234fa729e6




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
    - Integration of prescription demand orders from Rx's added to provide data for Monthly Inventory Movement.
  
- **Inventory**
    - **Edit Button** and **Delete Function** for medications on the inventory list.

----------------------------------------------------------------------------------
***Updates:*** 

The **Inventory Management Dashboard** has been introduced to provide a **visual representation** of key inventory metrics, helping pharmacists and administrators track stock levels and trends efficiently. 

### **New Features in the Dashboard:**
- **Total Inventory Value Over Time** 📈: A line graph that tracks total inventory value fluctuations, ensuring better financial oversight.
- **Monthly Inventory Movement** 📊: A horizontal bar chart visualizing net changes in stock balance over time.
- **Top 5 Priced Medications** 🍵: A **donut chart** showing the five most expensive medications, with an **"Others"** category for remaining inventory.
- **Top 5 Inventory by Quantity** 🏥: A **donut chart** displaying the five medications with the highest stock levels.
- **Price vs. Inventory Value** ⚖: A scatter plot illustrating the relationship between unit cost and total inventory value.
- **Monthly Statistics** 📊: Auto-updating percentage changes in **inventory stock** and **total inventory value**.

These enhancements enable a **data-driven approach** to inventory tracking, allowing better stock management, forecasting, and decision-making.

----------------------------------------------------------------------------------


- **Doctor**
    - Management similar to patients, with added fields: license number (DEA + NPI), expiration date, fax, license title.
    - Licenses will dictate the doctor’s ability to fill certain prescriptions (controls/non-controls).

## **Tech Stack**
- **Backend**: Python (Flask), SQL
- **Frontend**: HTML, CSS, JavaScript
- **Database**: MySQL
- **Environment**: Conda (pharmacy_env)

## **Getting Started**

###**Requirements**
Flask
mysql-connector-python
pymysql
flask-mysqldb
SQLAlchemy
pandas
numpy
matplotlib
chart.js
gunicorn
requests
python-dotenv
scipy
flask-wtf
flask-login
flask-bcrypt


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
- **Link to my original project:** [https://github.com/G-Hugo13/Pharmacy-Database/blob/main/README.md](https://github.com/G-Hugo13/Pharmacy-Database/tree/main)
  
**Feel free to submit issues, fork the repository, and create pull requests. Contributions are welcome! Star this repository if you wish to see more progress!**
