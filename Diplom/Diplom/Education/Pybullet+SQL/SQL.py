import sqlite3
import time
from datetime import datetime
import numpy as np
import os

class RobotDatabase:
    def __init__(self, db_name = "RobotTelemetry.db"):
        self.db_name = db_name
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, db_name)
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS simulation_Session (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time DATETIME,
                end_time DATETIME,
                description TEXT
            )
            """)
        
        self.cursor.execute("""
            create table if not exists robot_telemetry(
                telemetry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                timestamp DATETIME,
                sim_time REAL,
                joint_positions TEXT,
                joint_velocities TEXT,
                joint_torques TEXT,
                end_effector_positions TEXT,
                end_effector_orn TEXT,
                FOREIGN KEY(session_id) REFERENCES simulation_Session(session_id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS control_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                timestamp DATETIME,
                key_pressed TEXT,
                action_description TEXT,
                FOREIGN KEY(session_id) REFERENCES simulation_Session(session_id)
            )
        """)

        self.conn.commit()
        print("Tables created successfully")
    
    def start_new_session(self,description: str = ""):
        self.cursor.execute("""
            INSERT INTO simulation_Session (description)
            VALUES (?)
            """,(description,))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def end_session(self,session_id):
        self.cursor.execute("""
            UPDATE simulation_Session
            SET end_time = DATETIME('now')
            WHERE session_id = ?
            """,(session_id,))

        self.conn.commit()

    def save_telemetry(self,
                        session_id,
                        sim_time,
                        joint_positions,
                        joint_velocities,
                        joint_torques,
                        end_effector_positions,
                        end_effector_orn):
        import json

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
            INSERT INTO robot_telemetry
            (session_id,timestamp,sim_time,joint_positions,joint_velocities,joint_torques,end_effector_positions,end_effector_orn)
            VALUES (?,?,?,?,?,?,?,?)
            """,(
                session_id,
                timestamp,
                sim_time,
                json.dumps([float(p) for p in joint_positions]),
                json.dumps([float(v) for v in joint_velocities]),
                json.dumps([float(t) for t in joint_torques]),
                json.dumps([float(p) for p in end_effector_positions]),
                json.dumps([float(o) for o in end_effector_orn]),
            ))

        self.conn.commit()
    
    def save_control_event(self,
                           session_id,
                           key_pressed,
                           action_description):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
            INSERT INTO control_events
            (session_id,timestamp,key_pressed,action_description)
            VALUES (?,?,?,?)
            """,(
                session_id,
                timestamp,
                key_pressed,
                action_description,
            ))

        self.conn.commit()

    def get_telemetry(self,
                      session_id,
                      limit = 100):
        import json

        self.cursor.execute("""
            SELECT * FROM robot_telemetry
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,(
                session_id,
                limit
            ))

        records = self.cursor.fetchall()

        result = []
        for record in records:
            rec_list = list(record)
            for i in range(4,9):
                rec_list[i] = json.loads(rec_list[i])
            result.append(tuple(rec_list))

        return result
    
    def close(self):
        self.conn.close()
    
    def __del__(self):
        self.close()