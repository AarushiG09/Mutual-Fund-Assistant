import sqlite3
import logging
from datetime import datetime
from typing import List, Optional
from src.config import SQLITE_DB_PATH
from src.data.models import MutualFundScheme, FundManager

logger = logging.getLogger(__name__)

def get_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the SQLite database tables."""
    logger.info("Initializing database tables...")
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create schemes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schemes (
            url TEXT PRIMARY KEY,
            scheme_name TEXT NOT NULL,
            expense_ratio REAL,
            exit_load TEXT,
            benchmark_name TEXT,
            nav REAL,
            nav_date TEXT,
            launch_date TEXT,
            min_sip_amount REAL,
            riskometer TEXT,
            last_updated TEXT
        )
    """)
    
    # Create managers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS managers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scheme_url TEXT,
            name TEXT NOT NULL,
            experience TEXT,
            education TEXT,
            date_from TEXT,
            FOREIGN KEY (scheme_url) REFERENCES schemes (url) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully.")

def save_scheme(scheme: MutualFundScheme):
    """
    Saves a parsed scheme and its managers to the database.
    Updates the scheme details if the URL already exists (upsert).
    """
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.now().isoformat()
    
    try:
        # Upsert the scheme details
        cursor.execute("""
            INSERT INTO schemes (
                url, scheme_name, expense_ratio, exit_load, benchmark_name, 
                nav, nav_date, launch_date, min_sip_amount, riskometer, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                scheme_name = excluded.scheme_name,
                expense_ratio = excluded.expense_ratio,
                exit_load = excluded.exit_load,
                benchmark_name = excluded.benchmark_name,
                nav = excluded.nav,
                nav_date = excluded.nav_date,
                launch_date = excluded.launch_date,
                min_sip_amount = excluded.min_sip_amount,
                riskometer = excluded.riskometer,
                last_updated = excluded.last_updated
        """, (
            scheme.url, scheme.scheme_name, scheme.expense_ratio, scheme.exit_load,
            scheme.benchmark_name, scheme.nav, scheme.nav_date, scheme.launch_date,
            scheme.min_sip_amount, scheme.riskometer, now_iso
        ))
        
        # Remove old managers for this scheme
        cursor.execute("DELETE FROM managers WHERE scheme_url = ?", (scheme.url,))
        
        # Insert new managers
        for manager in scheme.managers:
            cursor.execute("""
                INSERT INTO managers (scheme_url, name, experience, education, date_from)
                VALUES (?, ?, ?, ?, ?)
            """, (scheme.url, manager.name, manager.experience, manager.education, manager.date_from))
            
        conn.commit()
        logger.info(f"Successfully saved scheme: {scheme.scheme_name}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error saving scheme {scheme.scheme_name} to database: {e}")
        raise e
    finally:
        conn.close()

def get_all_schemes() -> List[MutualFundScheme]:
    """Retrieves all mutual fund schemes along with their managers from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM schemes")
    rows = cursor.fetchall()
    
    schemes = []
    for row in rows:
        url = row["url"]
        
        # Get managers for this scheme
        cursor.execute("SELECT * FROM managers WHERE scheme_url = ?", (url,))
        mgr_rows = cursor.fetchall()
        managers = []
        for mr in mgr_rows:
            managers.append(FundManager(
                name=mr["name"],
                experience=mr["experience"],
                education=mr["education"],
                date_from=mr["date_from"]
            ))
            
        schemes.append(MutualFundScheme(
            scheme_name=row["scheme_name"],
            expense_ratio=row["expense_ratio"],
            exit_load=row["exit_load"],
            benchmark_name=row["benchmark_name"],
            nav=row["nav"],
            nav_date=row["nav_date"],
            launch_date=row["launch_date"],
            min_sip_amount=row["min_sip_amount"],
            riskometer=row["riskometer"],
            url=row["url"],
            managers=managers
        ))
        
    conn.close()
    return schemes
