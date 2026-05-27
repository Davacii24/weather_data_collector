import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "weather.db")

def get_connection():
    """Returns a connection to the database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

