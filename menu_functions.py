import mysql.connector

def add_new_employee(connection, cursor):
    """
    Accept input for all fields of employee to add new employee.
    (Values where NULL is acceptable may be set to None when nothing is given)
    Insert the new employee into EMPLOYEE table, commit if works, otherwise error and rollback.
    """
    first_name = input("Enter First Name (Required): ") or None
    middle_initial = input("Enter Middle Initial (Optional): ") or None
    last_name = input("Enter Last Name (Required): ") or None
    ssn = input("Enter SSN (Required - 9 digits): ") or None
    birth_date = input("Enter Birth Date (Optional - YYYY-MM-DD): ") or None
    address = input("Enter Address (Optional): ") or None
    sex = input("Enter Sex (Optional - M/F): ") or None
    salary = input("Enter Salary (Optional): ") or None
    supervisor_ssn = input("Enter Supervisor SSN (Optional): ") or None
    department_number = input("Enter Department Number (Required): ") or None

    try:
        query = "INSERT INTO EMPLOYEE (Fname, Minit, Lname, Ssn, Bdate, Address, Sex, Salary, Super_ssn, Dno) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (first_name, middle_initial, last_name, ssn, birth_date, address, sex, salary, supervisor_ssn, department_number))
        connection.commit()
        print("Employee added successfully.")
    except mysql.connector.Error as error:
        print(f"Constraint Violation Error: {error}")
        connection.rollback()

def view_employee(connection, cursor):
    """
    Given employee SSN, return all fields from employee as well as supervisor name,
    the department they are from, and dependents (if any).
    """
    employee_ssn = input("Enter Employee SSN: ") or None
    query = """
        SELECT e.*, s.Fname AS Super_Fname, s.Lname AS Super_Lname, d.Dname 
        FROM EMPLOYEE e 
        LEFT JOIN EMPLOYEE s ON e.Super_ssn = s.Ssn 
        JOIN DEPARTMENT d ON e.Dno = d.Dnumber 
        WHERE e.Ssn = %s
    """
    cursor.execute(query, (employee_ssn,))
    result = cursor.fetchone()
    if result:
        print("\n--- Employee Record ---")
        for key, value in result.items():
            print(f"{key}: {value}")
        cursor.execute("SELECT Dependent_name, Relationship FROM DEPENDENT WHERE Essn = %s", (employee_ssn,))
        dependents = cursor.fetchall()
        print("Dependents:", dependents if dependents else "None")
    else:
        print("Employee not found.")

def modify_employee(connection, cursor):
    """
    Given employee SSN, return employee info and allow user to update certain fields.
    (Address, sex, salary, super_ssn, dno)
    Record is locked upon retrieving employee SSN, preventing overlapping modification.
    """
    employee_ssn = input("Enter Employee SSN to modify: ") or None
    try:
        connection.start_transaction()
        cursor.execute("SELECT * FROM EMPLOYEE WHERE Ssn = %s FOR UPDATE", (employee_ssn,))
        employee = cursor.fetchone()
        if not employee:
            print("Employee not found.")
            connection.rollback()
            return
        print("Current Record:", employee)
        print("Enter new values (leave blank to keep current):")
        address = input(f"Address [{employee['Address']}]: ") or employee['Address']
        sex = input(f"Sex [{employee['Sex']}]: ") or employee['Sex']
        salary = input(f"Salary [{employee['Salary']}]: ") or employee['Salary']
        super_ssn = input(f"Super_ssn [{employee['Super_ssn']}]: ") or employee['Super_ssn']
        dno = input(f"Dno [{employee['Dno']}]: ") or employee['Dno']
        cursor.execute("UPDATE EMPLOYEE SET Address=%s, Sex=%s, Salary=%s, Super_ssn=%s, Dno=%s WHERE Ssn=%s", (address, sex, salary, super_ssn, dno, employee_ssn))
        connection.commit()
        print("Update successful.")
    except mysql.connector.Error as error:
        print(f"Error: {error}")
        connection.rollback()

def remove_employee(connection, cursor):
    """
    Given employee SSN, return employee info and ask for confirmation for removal.
    If the employee has dependencies, request will be cancelled and user must first delete dependencies.
    If confirmation is provided and no dependencies exist, employee will be removed from DB.
    Record is locked upon retrieving employee SSN, preventing overlapping modifications.
    """
    employee_ssn = input("Enter Employee SSN to remove: ") or None
    try:
        connection.start_transaction()
        cursor.execute("SELECT * FROM EMPLOYEE WHERE Ssn = %s FOR UPDATE", (employee_ssn,))
        employee = cursor.fetchone()
        if not employee:
            print("Employee not found.")
            connection.rollback()
            return
        print("Record found:", employee)
        confirm = input("Are you sure you want to delete? (yes/no): ")
        if confirm.lower() == 'yes':
            cursor.execute("DELETE FROM EMPLOYEE WHERE Ssn = %s", (employee_ssn,))
            connection.commit()
            print("Employee removed.")
        else:
            connection.rollback()
    except mysql.connector.IntegrityError:
        print("Warning: Dependencies exist. Resolve referential integrity constraints first.")
        connection.rollback()
    except mysql.connector.Error as error:
        print(f"Error: {error}")
        connection.rollback()

def add_new_dependent(connection, cursor):
    """
    Given employee SSN, return dependent info for provided employee.
    Retrieves info for dependent, allowing empty entries for NULL-capable values.
    Uses info to create new dependent entry for given employee.
    Employee record is locked upon retrieving SSN, preventing overlapping modifications.
    """
    employee_ssn = input("Enter Employee SSN: ") or None
    try:
        connection.start_transaction()
        cursor.execute("SELECT * FROM EMPLOYEE WHERE Ssn = %s FOR UPDATE", (employee_ssn,))
        if not cursor.fetchone():
            print("Employee not found.")
            connection.rollback()
            return
        cursor.execute("SELECT Dependent_name FROM DEPENDENT WHERE Essn = %s", (employee_ssn,))
        print("Current Dependents:", cursor.fetchall())
        name = input("New Dependent Name (Required): ") or None
        sex = input("Sex (Optional - M/F): ") or None
        bdate = input("Birth Date (Optional - YYYY-MM-DD): ") or None
        relationship = input("Relationship (Optional): ") or None
        cursor.execute("INSERT INTO DEPENDENT VALUES (%s, %s, %s, %s, %s)", (employee_ssn, name, sex, bdate, relationship))
        connection.commit()
        print("Dependent added.")
    except mysql.connector.Error as error:
        print(f"Error: {error}")
        connection.rollback()

def remove_dependent(connection, cursor):
    """
    Given employee SSN, return dependent info for provided employee.
    Retrieves first name for dependent that is going to be removed.    
    Uses name to delete dependent from DB.
    Employee record is locked upon retrieving SSN, preventing overlapping modifications.
    """
    employee_ssn = input("Enter Employee SSN: ") or None
    try:
        connection.start_transaction()
        cursor.execute("SELECT * FROM EMPLOYEE WHERE Ssn = %s FOR UPDATE", (employee_ssn,))
        employee = cursor.fetchone()
        
        if not employee:
            print("Error: No employee found with that SSN.")
            connection.rollback()
            return

        cursor.execute("SELECT Dependent_name FROM DEPENDENT WHERE Essn = %s", (employee_ssn,))
        dependents = cursor.fetchall()
        
        if not dependents:
            print("This employee has no dependents.")
            connection.rollback()
            return
            
        print("Dependents:", dependents)
        target = input("Enter name of dependent to remove: ") or None
        
        cursor.execute("DELETE FROM DEPENDENT WHERE Essn = %s AND Dependent_name = %s", (employee_ssn, target))
        
        if cursor.rowcount > 0:
            connection.commit()
            print("Dependent removed.")
        else:
            print(f"Error: No dependent found with the name '{target}'.")
            connection.rollback()
            
    except mysql.connector.Error as error:
        print(f"Error: {error}")
        connection.rollback()

def add_new_department(connection, cursor):
    """
    Requests values for new department entry, allowing empty for NULL where possible.
    Uses values to insert new department entry into DB.
    """
    name = input("Department Name (Required): ") or None
    number = input("Department Number (Required): ") or None
    manager_ssn = input("Manager SSN (Required): ") or None
    manager_start_date = input("Manager Start Date (Optional - YYYY-MM-DD): ") or None
    try:
        cursor.execute("INSERT INTO DEPARTMENT VALUES (%s, %s, %s, %s)", (name, number, manager_ssn, manager_start_date))
        connection.commit()
        print("Department created.")
    except mysql.connector.Error as error:
        print(f"Constraint Violation: {error}")
        connection.rollback()

def view_department(connection, cursor):
    """
    Requests dnumber.
    Using this, returns list of departments, manager names, and all possible locations of department.
    """
    dnumber = input("Enter Dnumber: ") or None
    cursor.execute("SELECT d.*, e.Fname, e.Lname FROM DEPARTMENT d JOIN EMPLOYEE e ON d.Mgr_ssn = e.Ssn WHERE d.Dnumber = %s", (dnumber,))
    dept = cursor.fetchone()
    if dept:
        print(f"Dept: {dept['Dname']}, Manager: {dept['Fname']} {dept['Lname']}")
        cursor.execute("SELECT Dlocation FROM DEPT_LOCATIONS WHERE Dnumber = %s", (dnumber,))
        print("Locations:", [loc['Dlocation'] for loc in cursor.fetchall()])
    else:
        print("Department not found.")

def remove_department(connection, cursor):
    """
    Requests dnumber and shows information for that department.
    Requests confirmation to remove department from DB.
    Checks for dependencies that need to be removed and errors out if anything is found.
    Removes entry from DB if no errors occur.
    Locks department record to prevent overlapping access.
    """
    dnumber = input("Enter Dnumber to remove: ") or None
    try:
        connection.start_transaction()
        cursor.execute("SELECT * FROM DEPARTMENT WHERE Dnumber = %s FOR UPDATE", (dnumber,))
        dept = cursor.fetchone()
        if not dept:
            print("Department not found.")
            connection.rollback()
            return
        print("Record:", dept)
        if input("Confirm delete? (yes/no): ").lower() == 'yes':
            cursor.execute("DELETE FROM DEPARTMENT WHERE Dnumber = %s", (dnumber,))
            connection.commit()
            print("Department removed.")
        else:
            connection.rollback()
    except mysql.connector.IntegrityError:
        print("Warning: Dependencies exist. Resolve referential integrity constraints first.")
        connection.rollback()

def add_department_location(connection, cursor):
    """
    Requests dnumber, and displays all locations for said department.
    Will ask for new location to enter and add it to the DB once provided.
    Locks department record to prevent overlapping access.
    """
    dnumber = input("Enter Dnumber: ") or None
    try:
        connection.start_transaction()
        cursor.execute("SELECT * FROM DEPARTMENT WHERE Dnumber = %s FOR UPDATE", (dnumber,))
        cursor.execute("SELECT Dlocation FROM DEPT_LOCATIONS WHERE Dnumber = %s", (dnumber,))
        print("Current Locations:", cursor.fetchall())
        new_loc = input("New Location: ") or None
        cursor.execute("INSERT INTO DEPT_LOCATIONS VALUES (%s, %s)", (dnumber, new_loc))
        connection.commit()
        print("Location added.")
    except mysql.connector.Error as error:
        print(f"Error: {error}")
        connection.rollback()

def remove_department_location(connection, cursor):
    """
    Requests dnumber, and displays all locations for said department.
    Will ask for a location to enter and remove it if a matching location exists.
    Locks department record to prevent overlapping access.
    """
    dnumber = input("Enter Dnumber: ") or None
    try:
        connection.start_transaction()
        cursor.execute("SELECT * FROM DEPARTMENT WHERE Dnumber = %s FOR UPDATE", (dnumber,))
        cursor.execute("SELECT Dlocation FROM DEPT_LOCATIONS WHERE Dnumber = %s", (dnumber,))
        print("Locations:", cursor.fetchall())
        target = input("Location to remove: ") or None
        cursor.execute("DELETE FROM DEPT_LOCATIONS WHERE Dnumber = %s AND Dlocation = %s", (dnumber, target))
        connection.commit()
        print("Location removed.")
    except mysql.connector.Error as error:
        print(f"Error: {error}")
        connection.rollback()
