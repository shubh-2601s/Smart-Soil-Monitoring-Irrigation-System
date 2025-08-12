# db.py
import aiosqlite

DB_NAME = "soil_data.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS soil_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nitrogen REAL,
                phosphorus REAL,
                potassium REAL,
                ph REAL,
                ec REAL,
                humidity REAL,
                temperature REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

async def insert_data(data):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO soil_data (nitrogen, phosphorus, potassium, ph, ec, humidity, temperature)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['nitrogen'], data['phosphorus'], data['potassium'],
            data['ph'], data['ec'], data['humidity'], data['temperature']
        ))
        await db.commit()
