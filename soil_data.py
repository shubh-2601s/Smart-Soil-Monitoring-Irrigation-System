# soil_data.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
import mysql.connector
from datetime import datetime
import uvicorn

app = FastAPI()

# Pydantic model for validating incoming data
class SoilData(BaseModel):
    nitrogen: int
    phosphorous: int
    potassium: int
    moisture: float
    temperature: float

# Connect to MySQL/MariaDB
conn = mysql.connector.connect(
    host="localhost",
    user="your_username",
    password="your_password",
    database="soil_db"
)
cursor = conn.cursor()

@app.post("/soil-data")
async def receive_soil_data(data: SoilData):
    now = datetime.now()
    sql = "INSERT INTO soil_readings (nitrogen, phosphorous, potassium, moisture, temperature, timestamp) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (data.nitrogen, data.phosphorous, data.potassium, data.moisture, data.temperature, now)
    cursor.execute(sql, values)
    conn.commit()
    return {"message": "Data stored successfully"}

if __name__ == "__main__":
    uvicorn.run("soil_data:app", host="0.0.0.0", port=8000)
