import sqlite3
import mysql.connector
from datetime import datetime
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate_sqlite_to_mysql():
    """
    Migrate data from SQLite to MySQL database
    """
    # MySQL connection parameters from environment variables
    mysql_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'your_password'),
        'database': os.getenv('DB_NAME', 'soil_db')
    }
    
    try:
        # Connect to SQLite database
        print("📊 Connecting to SQLite database...")
        sqlite_conn = sqlite3.connect('d:/soil_sensor/soil_data.db')
        sqlite_cursor = sqlite_conn.cursor()
        
        # Connect to MySQL database
        print("🗄️ Connecting to MySQL database...")
        mysql_conn = mysql.connector.connect(**mysql_config)
        mysql_cursor = mysql_conn.cursor()
        
        # Create database if it doesn't exist
        mysql_cursor.execute("CREATE DATABASE IF NOT EXISTS soil_db")
        mysql_cursor.execute("USE soil_db")
        
        # Create table in MySQL (matching SQLAlchemy structure)
        print("🏗️ Creating MySQL table structure...")
        create_table_query = """
        CREATE TABLE IF NOT EXISTS soil_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nitrogen INT,
            phosphorus INT,
            potassium INT,
            ph FLOAT,
            ec INT,
            humidity FLOAT,
            temperature FLOAT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_timestamp (timestamp)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        mysql_cursor.execute(create_table_query)
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        mysql_cursor.execute("DELETE FROM soil_data")
        mysql_conn.commit()
        
        # Fetch all data from SQLite
        print("📥 Fetching data from SQLite...")
        sqlite_cursor.execute("SELECT * FROM soil_data ORDER BY id")
        sqlite_data = sqlite_cursor.fetchall()
        
        print(f"Found {len(sqlite_data)} records in SQLite database")
        
        # Insert data into MySQL
        print("📤 Transferring data to MySQL...")
        insert_query = """
        INSERT INTO soil_data (nitrogen, phosphorus, potassium, ph, ec, humidity, temperature, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        transferred_count = 0
        for row in sqlite_data:
            # SQLite row: (id, nitrogen, phosphorus, potassium, ph, ec, humidity, temperature, timestamp)
            # Skip the SQLite ID and let MySQL auto-generate new IDs
            mysql_data = (row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
            mysql_cursor.execute(insert_query, mysql_data)
            transferred_count += 1
            
            if transferred_count % 10 == 0:
                print(f"✅ Transferred {transferred_count} records...")
        
        # Commit the transaction
        mysql_conn.commit()
        
        # Verify the transfer
        mysql_cursor.execute("SELECT COUNT(*) FROM soil_data")
        mysql_count = mysql_cursor.fetchone()[0]
        
        print(f"\n🎉 Migration completed successfully!")
        print(f"📊 Total records transferred: {transferred_count}")
        print(f"✅ MySQL database now contains: {mysql_count} records")
        
        # Show sample of transferred data
        print("\n📋 Sample of transferred data:")
        mysql_cursor.execute("SELECT * FROM soil_data ORDER BY timestamp DESC LIMIT 5")
        sample_data = mysql_cursor.fetchall()
        
        print("ID | N   | P   | K   | pH   | EC  | Hum  | Temp | Timestamp")
        print("-" * 70)
        for row in sample_data:
            print(f"{row[0]:2} | {row[1]:3} | {row[2]:3} | {row[3]:3} | {row[4]:4.1f} | {row[5]:3} | {row[6]:4.1f} | {row[7]:4.1f} | {row[8]}")
        
    except mysql.connector.Error as mysql_err:
        print(f"❌ MySQL Error: {mysql_err}")
        if "Unknown database" in str(mysql_err):
            print("💡 Creating database 'soil_db'...")
            try:
                temp_conn = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='Shubh_26'
                )
                temp_cursor = temp_conn.cursor()
                temp_cursor.execute("CREATE DATABASE soil_db")
                temp_conn.commit()
                temp_conn.close()
                print("✅ Database 'soil_db' created successfully!")
                print("🔄 Please run the script again to complete the migration.")
            except Exception as db_err:
                print(f"❌ Failed to create database: {db_err}")
        return False
        
    except sqlite3.Error as sqlite_err:
        print(f"❌ SQLite Error: {sqlite_err}")
        return False
        
    except Exception as e:
        print(f"❌ General Error: {e}")
        return False
        
    finally:
        # Close connections
        if 'sqlite_conn' in locals():
            sqlite_conn.close()
        if 'mysql_conn' in locals():
            mysql_conn.close()
    
    return True

if __name__ == "__main__":
    print("🚀 Starting SQLite to MySQL migration...")
    print("=" * 50)
    success = migrate_sqlite_to_mysql()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("🔄 Next step: Update server.py to use MySQL")
    else:
        print("\n❌ Migration failed. Please check the errors above.")