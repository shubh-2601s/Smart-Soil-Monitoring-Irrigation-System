import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def add_relay_column():
    """Add relay column to existing soil_data table"""
    try:
        # Database connection using environment variables
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'soil_db'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'your_password')
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            # Check if relay column already exists
            cursor.execute("SHOW COLUMNS FROM soil_data LIKE 'relay'")
            if cursor.fetchone():
                print("✅ Relay column already exists")
                return
            
            # Add relay column
            alter_query = "ALTER TABLE soil_data ADD COLUMN relay VARCHAR(10) DEFAULT 'OFF'"
            cursor.execute(alter_query)
            connection.commit()
            
            print("✅ Successfully added relay column to soil_data table")
            
            # Verify the column was added
            cursor.execute("DESCRIBE soil_data")
            columns = cursor.fetchall()
            print("\n📋 Updated table structure:")
            for column in columns:
                print(f"  - {column[0]}: {column[1]}")

    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 MySQL connection closed")

if __name__ == "__main__":
    print("🔧 Adding relay column to soil_data table...")
    add_relay_column()