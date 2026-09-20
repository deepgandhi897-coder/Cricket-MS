"""
db.py — Oracle Database Connection Helper
Cricket Management System

Uses python-oracledb in THIN mode (no Oracle Instant Client required).
Credentials are loaded from .env file.
"""

import oracledb
import os
from dotenv import load_dotenv

# Load environment variables from .env (fallback to .env.example if needed)
load_dotenv()
if not os.getenv("ORACLE_USER"):
    load_dotenv(".env.example")


def get_connection():
    """
    Create and return an Oracle Database connection.
    Uses thin mode — works without Oracle Client installation.
    """
    try:
        connection = oracledb.connect(
            user=os.getenv("ORACLE_USER"),
            password=os.getenv("ORACLE_PASSWORD"),
            dsn=os.getenv("ORACLE_DSN")
        )
        return connection
    except oracledb.DatabaseError as e:
        error_obj, = e.args
        raise ConnectionError(
            f"Oracle Connection Failed: {error_obj.message}\n"
            f"Check ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN in your .env file."
        )


def fetch_all(cursor):
    """
    Fetch all rows from a cursor and return as a list of dicts.
    Column names are lowercased for easy Jinja2 access.
    Demonstrates: SELECT, JOIN, GROUP BY results
    """
    if cursor.description is None:
        return []
    columns = [col[0].lower() for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def fetch_one(cursor):
    """
    Fetch one row from cursor and return as dict.
    Returns None if no row found.
    """
    row = cursor.fetchone()
    if row is None or cursor.description is None:
        return None
    columns = [col[0].lower() for col in cursor.description]
    return dict(zip(columns, row))
