import sqlite3
from datetime import datetime
import os


class Database:
    def __init__(self, db="database.db"):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, db)
        self.db = db_path
        self.connection = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS Survey_response (
        timestamp DATETIME,
        question1 Integer,
        question2 Integer,
        question3 Integer,
        question4 Integer
        )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Robobt_telemetry(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                X REAL,
                Y REAL,
                Z REAL,
                VELOCITY_REAL,
                JOINT_POSITION TEXT,
                ADDITIONAL_DATA TEXT
                )""")
        
        self.connection.commit()

    def save_survey(self,answers):
        cursor = self.connection.cursor()
        cursor.execute("""
        INSERT INTO Survey_response (timestamp, question1, question2, question3, question4)
        values(?,?,?,?,?)
        """,
        (datetime.now(), *answers))
        self.connection.commit()
        return cursor.lastrowid
    
    def save_telemetry(self,data):
        cursor = self.connection.cursor()
        cursor.execute("""
        INSERT INTO Robobt_telemetry
        values(?,?,?,?,?,?,?,?)
        """,
        (datetime.now(),
         data.get('x',0),
         data.get('y',0),
         data.get('z',0),
         data.get('velocity',0),
         data.get('joint_positions',[]),
         data.get('additional_data',{})))
        
        self.connection.commit()
    
    def close(self):
        self.connection.close()


