
import sqlite3
import os

DB_PATH = "stock_manager.db"

if not os.path.exists(DB_PATH):
    print(f"❌ Database file not found at {DB_PATH}")
    # Try looking in subfolder if we are in parent
    if os.path.exists(f"Projet-Blockchain-et-IoT-Suivi-intelligent-des-stocks-avec-RFID-et-Hashgraph-master/{DB_PATH}"):
        DB_PATH = f"Projet-Blockchain-et-IoT-Suivi-intelligent-des-stocks-avec-RFID-et-Hashgraph-master/{DB_PATH}"
        print(f"✅ Found DB at {DB_PATH}")
    else:
        exit(1)

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables found: {tables}")
    
    required_tables = ['transactions', 'taxes', 'formulaires']
    for table in required_tables:
        if table not in tables:
            print(f"❌ Missing table: {table}")
        else:
            print(f"✅ Table exists: {table}")
            # Check columns
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [c[1] for c in cursor.fetchall()]
            print(f"   Columns: {columns}")

    # Try specific query from dashboard
    print("\nTesting Dashboard Query 1...")
    try:
        cursor.execute("SELECT SUM(montant) FROM transactions WHERE type LIKE 'TAXE%' OR type LIKE 'ACTE%'")
        res = cursor.fetchone()
        print(f"✅ Query success. Result: {res}")
    except Exception as e:
        print(f"❌ Query failed: {e}")

    conn.close()

except Exception as e:
    print(f"❌ Database connection failed: {e}")
