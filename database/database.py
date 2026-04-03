# database/database.py
import sqlite3
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

def get_ist_time():
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")

def connect():
    conn = sqlite3.connect("patients.db")
    return conn

def init_db():
    conn = connect()
    cur  = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS patients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT,
        name TEXT,
        age INTEGER,
        gender TEXT,
        phone TEXT,
        address TEXT,
        created TEXT DEFAULT (datetime('now','+5 hours 30 minutes'))
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS diagnosis(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT,
        result TEXT,
        confidence REAL,
        created TEXT DEFAULT (datetime('now','+5 hours 30 minutes'))
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS risk_assessment(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT,
        age_factor INTEGER,
        family_history INTEGER,
        hormone_therapy INTEGER,
        dense_breast INTEGER,
        previous_biopsy INTEGER,
        alcohol_use INTEGER,
        obesity INTEGER,
        late_menopause INTEGER,
        risk_score INTEGER,
        risk_level TEXT,
        created TEXT DEFAULT (datetime('now','+5 hours 30 minutes'))
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS doctor_notes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT,
        diagnosis_id INTEGER,
        doctor_name TEXT,
        note TEXT,
        recommendation TEXT,
        follow_up_date TEXT,
        created TEXT DEFAULT (datetime('now','+5 hours 30 minutes'))
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_log(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT,
        user TEXT,
        details TEXT,
        created TEXT DEFAULT (datetime('now','+5 hours 30 minutes'))
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS symptoms_log(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT,
        symptoms TEXT,
        notes TEXT,
        created TEXT DEFAULT (datetime('now','+5 hours 30 minutes'))
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS appointments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT,
        patient_name TEXT,
        doctor TEXT,
        date TEXT,
        time TEXT,
        complaint TEXT,
        notes TEXT,
        meeting_id TEXT,
        meeting_link TEXT,
        status TEXT DEFAULT 'Scheduled',
        created TEXT DEFAULT (datetime('now','+5 hours 30 minutes'))
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS consent_forms(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT,
        patient_name TEXT,
        phone TEXT,
        signature TEXT,
        relationship TEXT,
        timestamp TEXT
    )""")

    conn.commit()
    conn.close()

def log_audit(action, user, details):
    conn = connect()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO audit_log(action,user,details,created) VALUES(?,?,?,?)",
        (action, user, details, get_ist_time())
    )
    conn.commit()
    conn.close()

init_db()
