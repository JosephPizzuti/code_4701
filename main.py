import mysql.connector
from menu_functions import *

config = {
        'host': 'localhost',
        'database': 'Company',
        'user': 'root',
        'password': '9960241Jay',
        'autocommit': True
        }

def print_menu():
    print("\n### Company Menu ###")
    print("1. Add new employee")
    print("2. View employee")
    print("3. Modify employee")
    print("4. Remove employee")
    print("5. Add new dependent")
    print("6. Remove dependent")
    print("7. Add new department")
    print("8. View department")
    print("9. Remove department")
    print("10. Add department location")
    print("11. Remove department location")
    print("Enter 'q' to quit.\n")

def main():
    try:
        connection = mysql.connector.connect(**config)

        while True:
            print_menu()
            user_input = input("Enter your selection here: ").lower()

            cursor = connection.cursor(dictionary=True, buffered=True)
            
            match user_input:
                case '1': add_new_employee(connection, cursor)
                case '2': view_employee(connection, cursor)
                case '3': modify_employee(connection, cursor)
                case '4': remove_employee(connection, cursor)
                case '5': add_new_dependent(connection, cursor)
                case '6': remove_dependent(connection, cursor)
                case '7': add_new_department(connection, cursor)
                case '8': view_department(connection, cursor)
                case '9': remove_department(connection, cursor)
                case '10': add_department_location(connection, cursor)
                case '11': remove_department_location(connection, cursor)
                case 'q': break
                case _: print("Invalid choice. Please try again.")

    except Exception as error:
        print(f"Sorry, an error has occured: {error}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    main()
