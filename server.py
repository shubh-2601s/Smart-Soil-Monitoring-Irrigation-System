import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Float, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pytz
import logging

app = FastAPI()

# Set your local timezone (India Standard Time)
LOCAL_TZ = pytz.timezone('Asia/Kolkata')

# Add CORS middleware to allow ESP8266 requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base = declarative_base()

# MySQL Connection using environment variables
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_password')
DB_NAME = os.getenv('DB_NAME', 'soil_db')

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_local_time():
    """Get current time in local timezone"""
    return datetime.now(LOCAL_TZ).replace(tzinfo=None)  # Remove timezone info for MySQL compatibility

class SoilData(Base):
    __tablename__ = "soil_data"
    id = Column(Integer, primary_key=True, index=True)
    nitrogen = Column(Integer)
    phosphorus = Column(Integer)
    potassium = Column(Integer)
    ph = Column(Float)
    ec = Column(Integer)
    humidity = Column(Float)
    temperature = Column(Float)
    relay = Column(String(10))  # Added relay status field
    timestamp = Column(DateTime, default=get_local_time)

# Note: Don't create tables here since they already exist in MySQL
# Base.metadata.create_all(bind=engine)

class SoilInput(BaseModel):
    nitrogen: int
    phosphorus: int
    potassium: int
    ph: float
    ec: int
    humidity: float
    temperature: float
    relay: str  # Added relay field to input model

class RelayCommand(BaseModel):
    command: str

# Store the latest relay command and mode (in production, use Redis or database)
latest_relay_command = {"command": "OFF", "mode": "auto", "timestamp": get_local_time()}

@app.post("/soil-data")
async def receive_soil_data(data: SoilInput):
    db = SessionLocal()
    try:
        # Log incoming data for debugging
        logger.info(f"Received data from ESP8266: {data.dict()}")
        
        soil = SoilData(**data.dict())
        db.add(soil)
        db.commit()
        db.refresh(soil)
        
        logger.info(f"Soil data saved successfully with ID: {soil.id}")
        return {"status": "success", "id": soil.id, "message": "Data saved successfully"}
    except ValueError as e:
        db.rollback()
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Invalid data format: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        db.close()

@app.get("/latest-data")
def get_latest_data():
    db = SessionLocal()
    try:
        data = db.query(SoilData).order_by(SoilData.timestamp.desc()).first()
        if data:
            return {
                "id": data.id,
                "nitrogen": data.nitrogen,
                "phosphorus": data.phosphorus,
                "potassium": data.potassium,
                "ph": data.ph,
                "ec": data.ec,
                "humidity": data.humidity,
                "temperature": data.temperature,
                "relay": data.relay,  # Added relay status to response
                "timestamp": data.timestamp,
                "mode": latest_relay_command.get("mode", "auto"),  # Add current mode to response
                "last_command": latest_relay_command.get("command", "OFF")  # Add last command
            }
        return {"message": "No data found"}
    except Exception as e:
        logger.error(f"Error retrieving data: {str(e)}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

# Add a health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": get_local_time()}

@app.post("/control-relay")
async def control_relay(command: RelayCommand):
    """
    Endpoint to control the relay from dashboard
    """
    global latest_relay_command
    
    try:
        if command.command.upper() not in ["OFF", "ON"]:
            raise HTTPException(status_code=400, detail="Command must be 'ON' or 'OFF'")
        
        latest_relay_command = {
            "command": command.command.upper(),
            "mode": "manual",  # When dashboard controls, switch to manual mode
            "timestamp": get_local_time()
        }
        
        logger.info(f"Relay command received: {command.command.upper()}")
        return {
            "status": "success", 
            "command": command.command.upper(),
            "mode": "manual",
            "message": f"Relay turned {command.command.upper()}",
            "timestamp": latest_relay_command["timestamp"]
        }
    except Exception as e:
        logger.error(f"Error controlling relay: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/relay-command")
async def get_relay_command():
    """
    Endpoint for NodeMCU to check for relay commands (legacy endpoint)
    """
    return latest_relay_command

@app.get("/relay-status")
async def get_relay_status():
    """
    Endpoint for NodeMCU to check for relay commands (matches your NodeMCU code)
    """
    global latest_relay_command
    
    # Return response in format expected by NodeMCU
    response = f"{latest_relay_command['mode']} {latest_relay_command['command'].lower()}"
    
    logger.info(f"NodeMCU requested relay status: {response}")
    return response

@app.post("/set-auto-mode")
async def set_auto_mode():
    """
    Endpoint to switch back to auto mode
    """
    global latest_relay_command
    
    latest_relay_command["mode"] = "auto"
    latest_relay_command["timestamp"] = get_local_time()
    
    logger.info("Switched to auto mode")
    return {
        "status": "success",
        "mode": "auto",
        "message": "Switched to automatic irrigation mode"
    }

@app.get("/current-mode")
async def get_current_mode():
    """
    Endpoint to get current irrigation mode
    """
    return {
        "mode": latest_relay_command.get("mode", "auto"),
        "command": latest_relay_command.get("command", "OFF"),
        "timestamp": latest_relay_command.get("timestamp", get_local_time())
    }

if __name__ == "__main__":
    import uvicorn
    # Make server accessible from network (not just localhost)
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

