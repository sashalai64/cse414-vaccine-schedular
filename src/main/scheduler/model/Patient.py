import sqlite3
import sys
sys.path.append("../util/*")
sys.path.append("../db/*")
from util.Util import Util
from db.ConnectionManager import ConnectionManager


class Patient:
    def __init__(self, username, password = None, salt = None, hash = None):
        self.username = username
        self.password = password
        self.salt = salt
        self.hash = hash
    
    # getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        get_patient_details = "SELECT Salt, Hash FROM Patients WHERE Username = ?"
        try:
            cursor.execute(get_patient_details, (self.username,))
            for row in cursor:
                curr_salt = row['Salt']
                curr_hash = row['Hash']
                calculated_hash = Util.generate_hash(self.password, curr_salt)
                if not curr_hash == calculated_hash:
                    # print("Incorrect password")
                    cm.close_connection()
                    return None
                else:
                    self.salt = curr_salt
                    self.hash = calculated_hash
                    cm.close_connection()
                    return self
        except sqlite3.Error as e:
            raise e
        finally:
            cm.close_connection()
        return None
    
    def get_username(self):
        return self.username

    def get_salt(self):
        return self.salt

    def get_hash(self):
        return self.hash
    
    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_patients = "INSERT INTO Patients VALUES (?, ?, ?)"
        try:
            cursor.execute(add_patients, (self.username, self.salt, self.hash))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except sqlite3.Error:
            raise
        finally:
            cm.close_connection()

    def show_appointments(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        
        get_appointments = """
            SELECT R.Id, R.Time, R.Cusername, R.Vname 
            FROM Reservations R 
            WHERE R.Pusername = ? 
            ORDER BY R.Time
        """

        appointments = []
        try:
            cursor.execute(get_appointments, (self.username,))
            for row in cursor:
                appointment = {
                'id': row['Id'],
                'date': row['Time'],
                'caregiver': row['Cusername'],
                'vaccine': row['Vname']
            }
            appointments.append(appointment)

        except sqlite3.Error:
            raise
        finally:
            cm.close_connection()

        return appointments