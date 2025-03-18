from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from model.Reservation import Reservation
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import sqlite3
import os
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Create patient failed")
        return
    
    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again")
        return
    
    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save patient information to our database
    try:
        patient.save_to_db()
    except sqlite3.Error as e:
        print("Create patient failed")
        return
    except Exception as e:
        print("Create patient failed")
        return
    print("Created user", username)


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except sqlite3.Error as e:
        print("Failed to create user.")
        return
    except Exception as e:
        print("Failed to create user.")
        return
    print("Created user", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(select_username, (username,))
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            cm.close_connection()
            return row['Username'] is not None
    except sqlite3.Error as e:
        print("Error occurred when checking username")
        cm.close_connection()
        return True
    except Exception as e:
        print("Error occurred when checking username")
        cm.close_connection()
        return True
    cm.close_connection()
    return False


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(select_username, (username,))
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            cm.close_connection()
            return row['Username'] is not None
    except sqlite3.Error as e:
        print("Error occurred when checking username")
        cm.close_connection()
        return True
    except Exception as e:
        print("Error occurred when checking username")
        cm.close_connection()
        return True
    cm.close_connection()
    return False


def login_patient(tokens):
    # login_patien <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in, try again")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login patient failed")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except sqlite3.Error as e:
        print("Login patient failed")
        return
    except Exception as e:
        print("Login patient failed")
        return

    # check if the login was successful
    if patient is None:
        print("Login patient failed")
    else:
        print("Logged in as " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in, try again")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login caregiver failed")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except sqlite3.Error as e:
        print("Login caregiver failed")
        return
    except Exception as e:
        print("Login caregiver failed")
        return

    # check if the login was successful
    if caregiver is None:
        print("Login caregiver failed")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    # search_caregiver_schedule <date>
    # check 1: check if user is logged in
    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return
    
    # check 2: check the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again")
        return

    date = tokens[1]
    
    try:
        date_tokens = date.split("-")
        if len(date_tokens) != 3:
            print("Please try again")
            return
            
        # Check if first token is a 4-digit year
        if len(date_tokens[0]) != 4:
            print("Please try again")
            return
        
        year = int(date_tokens[0])
        month = int(date_tokens[1])
        day = int(date_tokens[2])

        if month < 1 or month > 12 or day < 1 or day > 31:
            print("Please try again")
            return
        
        # Format with time component to match database format
        d = f"{year}-{month:02d}-{day:02d} 00:00:00"
    
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        available_caregiver_query = """
            SELECT A.Username
            FROM Availabilities AS A
            WHERE A.Time = ? 
            AND A.Username NOT IN (
                SELECT R.Cusername
                FROM Reservations AS R
                WHERE R.Time = ?
            )
            ORDER BY A.Username
        """
        cursor.execute(available_caregiver_query, (d, d))
        available_caregivers = cursor.fetchall()

        print('Caregivers:')
        if not available_caregivers:
            print("No caregivers available")
        else:
            for row in available_caregivers:
                print(row["Username"])

        get_vaccines = "SELECT * FROM Vaccines"
        cursor.execute(get_vaccines)
        vaccines = cursor.fetchall()

        print('Vaccines:')
        if not vaccines:
            print("No vaccines available")
        else:
            for row in vaccines:
                print(f"{row['Name']} {row['Doses']}")

        cm.close_connection()

        #return available_caregivers

    except sqlite3.Error as e:
        print("Please try again")
        return
    except ValueError:
        print("Please try again")
        return
    except Exception as e:
        print("Please try again")
        return



def reserve(tokens):
    # reserve <date> <vaccine>
    # check 1: check if the current logged-in user is a patient
    if current_caregiver:
        print("Please login as a patient")
        return
    if current_patient is None:
        print("Please login first")
        return
    
    # check 2: the length for tokens need to be exactly 3
    if len(tokens) != 3:
        print("Please try again")
        return

    date = tokens[1]
    vaccine_name = tokens[2]
    
    date_tokens = date.split("-")

    try:
        # Make sure we have the right format
        if len(date_tokens) != 3:
            print("Please try again")
            return
            
        year = int(date_tokens[0])
        month = int(date_tokens[1])
        day = int(date_tokens[2])
        d = f"{year}-{month:02d}-{day:02d} 00:00:00"
        
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        
        # Check if there's any available caregiver
        available_caregiver_query = """
            SELECT A.Username
            FROM Availabilities AS A
            WHERE A.Time = ?
            AND A.Username NOT IN (
                SELECT R.Cusername
                FROM Reservations AS R
                WHERE R.Time = ?
            )
            ORDER BY A.Username
            LIMIT 1
        """
        cursor.execute(available_caregiver_query, (d, d))
        caregiver_row = cursor.fetchone()
        
        if caregiver_row is None:
            print("No caregiver is available")
            cm.close_connection()
            return
        
        caregiver_username = caregiver_row['Username']
        
        # Check if the vaccine exists and has available doses
        vaccine = None
        try:
            vaccine = Vaccine(vaccine_name, 0).get()
                
            if vaccine is None or vaccine.get_available_doses() <= 0:
                print("Not enough available doses")
                cm.close_connection()
                return
                
        except sqlite3.Error as e:
            print("Please try again")
            cm.close_connection()
            return
        except Exception as e:
            print("Please try again")
            cm.close_connection()
            return
        
        patient_username = current_patient.get_username()

        # If we get here, we have an available caregiver and vaccine doses
        # Make the reservation
        try:
            reservation = Reservation(time=d, cusername=caregiver_username, pusername=patient_username, vname=vaccine_name)
            reservation.save_to_db()

            # Decrease vaccine doses by 1
            vaccine.decrease_available_doses(1)

            print(f"Appointment ID {reservation.get_id()}, Caregiver username {caregiver_username}")

        except sqlite3.Error as e:
            print("Please try again")
            cm.close_connection()
            return
        except Exception as e:
            print("Please try again")
            cm.close_connection()
            return
                
        cm.close_connection()
    
    except ValueError:
        print("Please try again")
        return
    except Exception as e:
        print("Please try again")
        return



def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format yyyy-mm-dd
    date_tokens = date.split("-")
    year = int(date_tokens[0])
    month = int(date_tokens[1])
    day = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except sqlite3.Error as e:
        print("Upload Availability Failed")
        return
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        return
    print("Availability uploaded!")


def cancel(tokens):
    # cancel <appointment_id>
    # Check if a user is logged in
    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return
        
    # Check the token length
    if len(tokens) != 2:
        print("Please try again")
        return
    
    try:
        appointment_id = int(tokens[1])
    except ValueError:
        print("Please try again")
        return
        
    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        
        # First, check if the appointment exists
        check_appointment = "SELECT * FROM Reservations WHERE Id = ?"
        cursor.execute(check_appointment, (appointment_id,))
        appointment = cursor.fetchone()
        
        if appointment is None:
            print(f"Appointment ID {appointment_id} does not exist")
            cm.close_connection()
            return
            
        # Store appointment details
        appointment_time = appointment['Time']
        appointment_caregiver = appointment['Cusername']
        appointment_patient = appointment['Pusername']
        appointment_vaccine = appointment['Vname']
        
        # Check if current user is authorized to cancel
        is_authorized = False
        if current_caregiver and current_caregiver.get_username() == appointment_caregiver:
            is_authorized = True
        elif current_patient and current_patient.get_username() == appointment_patient:
            is_authorized = True
            
        if not is_authorized:
            print("Please try again")
            cm.close_connection()
            return
            
        # 1. Delete the appointment
        delete_appointment = "DELETE FROM Reservations WHERE Id = ?"
        cursor.execute(delete_appointment, (appointment_id,))
        
        # 2. Update the vaccine doses directly with SQL
        update_vaccine = "UPDATE Vaccines SET Doses = Doses + 1 WHERE Name = ?"
        cursor.execute(update_vaccine, (appointment_vaccine,))
        
        # 3. Make the caregiver available again
        check_availability = "SELECT * FROM Availabilities WHERE Time = ? AND Username = ?"
        cursor.execute(check_availability, (appointment_time, appointment_caregiver))
        existing_availability = cursor.fetchone()
        
        if not existing_availability:
            add_availability = "INSERT INTO Availabilities VALUES (?, ?)"
            cursor.execute(add_availability, (appointment_time, appointment_caregiver))
            
        # Commit transaction
        conn.commit()
        print(f"Appointment ID {appointment_id} has been successfully canceled")
    
    except sqlite3.Error as e:
        print("Please try again")
        cm.close_connection()
        return
    except ValueError:
        print("Please try again")
        cm.close_connection()
        return
    except Exception as e:
        print("Please try again")
        cm.close_connection()
        return

    cm.close_connection()


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except sqlite3.Error as e:
        print("Error occurred when adding doses")
        return
    except Exception as e:
        print("Error occurred when adding doses")
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except sqlite3.Error as e:
            print("Error occurred when adding doses")
            return
        except Exception as e:
            print("Error occurred when adding doses")
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except sqlite3.Error as e:
            print("Error occurred when adding doses")
            return
        except Exception as e:
            print("Error occurred when adding doses")
            return
    print("Doses updated!")


def show_appointments(tokens):
    # show_appointments
    # check if user is logged in
    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return
    
    # check if tokens is 1
    if len(tokens) != 1:
        print("Please try again")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    try:
        # for caregivers
        if current_caregiver:
            get_caregiver_appointments = """
                SELECT R.Id, R.Vname, R.Time, R.Pusername
                FROM Reservations AS R
                WHERE R.Cusername = ?
                ORDER BY R.Id
            """
            cursor.execute(get_caregiver_appointments, (current_caregiver.get_username(),))
            caregiver_appointments = cursor.fetchall()

            if not caregiver_appointments:
                print("No appointments scheduled")
                return
            
            for row in caregiver_appointments:
                id, vname, time, cusername = row
                formatted_date = time[:10]
                print(f"{id} {vname} {formatted_date} {cusername}")

        # for patients
        elif current_patient:
            get_patient_appointments = """
                SELECT R.Id, R.Vname, R.Time, R.Cusername 
                FROM Reservations R 
                WHERE R.Pusername = ? 
                ORDER BY R.Id
            """
            cursor.execute(get_patient_appointments, (current_patient.get_username(),))
            patient_appointments = cursor.fetchall()

            if not patient_appointments:
                print("No appointments scheduled")
                return
            
            for row in patient_appointments:
                id, vname, time, cusername = row
                formatted_date = time[:10]
                print(f"{id} {vname} {formatted_date} {cusername}")

    except sqlite3.Error as e:
        print("Please try again db")
        cm.close_connection()
        return
    except Exception as e:
        print("Please try again e")
        cm.close_connection()
        return 
    
    cm.close_connection()
        


def logout(tokens):
    global current_caregiver, current_patient

    if len(tokens) != 1:
        print("Please try again")
        return
    
    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return
    try: 
        current_caregiver = current_patient = None
        print("Successfully logged out")
    except Exception as e:
        print("Please try again")
        return


def start():
    stop = False
    print("*** Please enter one of the following commands ***")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    # checks if tables exist in the SQLite database and runs create.sql if they don’t
    cm = ConnectionManager()
    conn = cm.create_connection()
    sql_file_path = os.path.join(os.path.dirname(__file__), "..", "resources", "sqlite", "create.sql")
    try:
        cursor = conn.cursor()
        # Query for tables in the database information schema
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        if not cursor.fetchone():  # No tables exist
            with open(sql_file_path, 'r') as sql_file:
                sql_script = sql_file.read()
            # Run create.sql script against the database
            cursor.executescript(sql_script)
            conn.commit()
    except sqlite3.Error as e:
        print("Error initializing database tables:", e)
    except FileNotFoundError:
        print(f"Error: {sql_file_path} not found.")
    finally:
        cm.close_connection()

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
