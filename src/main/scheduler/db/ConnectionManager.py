import sqlite3
import os


class ConnectionManager:

    def __init__(self):
        self.db_path = os.getenv("DBPATH")
        if self.db_path is None:
            # Provide a default path if environment variable is not set
            self.db_path = "/Users/sashalai/cse414/hw6/vaccine-scheduler-python-main/src/main/resources/sqlite/hw6.db"
        self.conn = None

    def create_connection(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error as db_err:
            print("Database Programming Error in SQL connection processing!")
            print(db_err)
            self.conn = None  # Ensure conn is set to None on failure
        return self.conn

    def close_connection(self):
        try:
            self.conn.close()
        except sqlite3.Error as db_err:  # Use sqlite3.Error, not pymssql.Error
            print("Error while closing SQLite database connection!")
            print(db_err)
