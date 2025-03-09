import sqlite3
import sys
sys.path.append("../db/*")
from db.ConnectionManager import ConnectionManager


class Reservation:
    def __init__(self, id=None, time=None, cusername=None, pusername=None, vname=None):
        self.id = id
        self.time = time
        self.cusername = cusername
        self.pusername = pusername
        self.vname = vname
    
    def get_id(self):
        return self.id

    def get_time(self):
        return self.time
    
    def get_cusername(self):
        return self.cusername
    
    def get_pusername(self):
        return self.pusername

    def get_vname(self):
        return self.vname

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        
        add_reservation = "\
            INSERT INTO Reservations (Time, Cusername, Pusername, Vname)\
            VALUES (?, ?, ?, ?)\
        "
        try:
            cursor.execute(add_reservation, (self.time, self.cusername, self.pusername, self.vname))
            conn.commit()
            
            # Get the ID of the newly created reservation
            cursor.execute("SELECT last_insert_rowid()")
            self.id = cursor.fetchone()[0]
            
        except sqlite3.Error:
            conn.rollback()
            raise
        finally:
            cm.close_connection()