import time
import streamlit as st
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Smart Soil Dashboard", 
    layout="wide",
    page_icon="🌱",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for modern UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    .metric-card {
        background: linear-gradient(145deg, #ffffff, #f0f0f0);
        padding: 1.5rem;
        border-radius: 15px;
        border: none;
        margin: 0.5rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 45px rgba(0,0,0,0.15);
    }
    
    .status-indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    .status-online { 
        background: linear-gradient(45deg, #4CAF50, #45a049);
        box-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
    }
    
    .status-offline { 
        background: linear-gradient(45deg, #f44336, #d32f2f);
        box-shadow: 0 0 10px rgba(244, 67, 54, 0.5);
    }
    
    .custom-metric {
        background: linear-gradient(145deg, #f8f9ff, #e3f2fd);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #2196F3;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    .critical-alert {
        background: linear-gradient(145deg, #ffebee, #ffcdd2);
        border-left: 4px solid #f44336;
        animation: shake 0.5s ease-in-out;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    .warning-alert {
        background: linear-gradient(145deg, #fff3e0, #ffe0b2);
        border-left: 4px solid #ff9800;
    }
    
    .success-alert {
        background: linear-gradient(145deg, #e8f5e8, #c8e6c8);
        border-left: 4px solid #4caf50;
    }
    
    .sidebar .stSelectbox, .sidebar .stSlider {
        margin-bottom: 1rem;
    }
    
    .weather-widget {
        background: linear-gradient(135deg, #74b9ff, #0984e3);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .quick-stats {
        display: flex;
        justify-content: space-around;
        background: linear-gradient(145deg, #ffffff, #f5f5f5);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .stat-item {
        text-align: center;
        padding: 0.5rem;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2196F3;
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: #666;
        margin-top: 5px;
    }
    
    /* Enhanced Recommendation Cards */
    .recommendation-card {
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 4px solid;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .recommendation-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .critical-rec {
        background: linear-gradient(135deg, #ffebee, #ffcdd2);
        border-left-color: #f44336;
        border: 1px solid #ffcdd2;
    }
    
    .warning-rec {
        background: linear-gradient(135deg, #fff3e0, #ffe0b2);
        border-left-color: #ff9800;
        border: 1px solid #ffe0b2;
    }
    
    .good-rec {
        background: linear-gradient(135deg, #e8f5e8, #c8e6c8);
        border-left-color: #4caf50;
        border: 1px solid #c8e6c8;
    }
    
    .rec-header {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .rec-message {
        font-size: 0.95rem;
        color: #555;
        margin-bottom: 0.8rem;
        line-height: 1.4;
    }
    
    .rec-action {
        font-size: 0.9rem;
        font-weight: 500;
        color: #2c3e50;
        background: rgba(255,255,255,0.7);
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        border-left: 3px solid #3498db;
    }
    
    .health-score-container {
        background: linear-gradient(135deg, #f8f9ff, #e8f4f8);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #e3f2fd;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    .fertilizer-container {
        background: linear-gradient(135deg, #f1f8e9, #e8f5e8);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #c8e6c8;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced sidebar with more options
st.sidebar.header("⚙ Dashboard Controls")

# Theme selector
theme_option = st.sidebar.selectbox(
    "🎨 Dashboard Theme",
    ["Modern Blue", "Nature Green", "Professional Dark"],
    help="Choose your preferred dashboard theme"
)

# Auto-refresh slider with more options
refresh_interval = st.sidebar.slider(
    "🔄 Auto-refresh interval",
    min_value=5,
    max_value=300,
    value=30,
    step=5,
    help="Set how often the dashboard updates (5-300 seconds)"
)

# Data retention settings
data_retention = st.sidebar.slider(
    "📊 Historical data points",
    min_value=10,
    max_value=100,
    value=20,
    step=5,
    help="Number of historical readings to keep for charts"
)

# Alert thresholds customization
with st.sidebar.expander("🚨 Custom Alert Thresholds"):
    custom_ph_min = st.number_input("Min pH", value=6.0, step=0.1)
    custom_ph_max = st.number_input("Max pH", value=8.0, step=0.1)
    custom_temp_max = st.number_input("Max Temperature (°C)", value=30, step=1)
    custom_humidity_max = st.number_input("Max Humidity (%)", value=70, step=1)

# Export options
with st.sidebar.expander("📤 Export Options"):
    if st.button("💾 Export Current Data", use_container_width=True):
        st.success("Data export feature coming soon!")
    if st.button("📈 Generate Report", use_container_width=True):
        st.success("Report generation feature coming soon!")

# Manual refresh button with enhanced styling
if st.sidebar.button("🔄 Refresh Now", use_container_width=True):
    st.success("🔄 Dashboard refreshed!")
    time.sleep(1)
    st.rerun()

# Connection status with enhanced display
st.sidebar.markdown("### 📡 System Status")

# Initialize session state for data history with custom retention
if 'data_history' not in st.session_state:
    st.session_state.data_history = []

# Initialize weather data session state with hourly refresh
if 'weather_data' not in st.session_state:
    st.session_state.weather_data = None
if 'weather_last_updated' not in st.session_state:
    st.session_state.weather_last_updated = None

# Function to check if weather data needs refresh (every hour)
def should_refresh_weather():
    if st.session_state.weather_last_updated is None:
        return True
    
    time_diff = datetime.now() - st.session_state.weather_last_updated
    return time_diff.total_seconds() >= 3600  # 3600 seconds = 1 hour

# Function to get cached or fresh weather data
def get_cached_weather_data():
    if should_refresh_weather():
        # Fetch fresh weather data
        fresh_weather = get_weather_data()
        st.session_state.weather_data = fresh_weather
        st.session_state.weather_last_updated = datetime.now()
        return fresh_weather
    else:
        # Return cached weather data
        return st.session_state.weather_data if st.session_state.weather_data else get_weather_data()

# Function to get data from server
def get_soil_data():
    try:
        response = requests.get("http://localhost:8000/latest-data", timeout=10)
        response.raise_for_status()
        return response.json(), True
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to server"}, False
    except requests.exceptions.Timeout:
        return {"error": "Request timeout"}, False
    except Exception as e:
        return {"error": str(e)}, False

# Get current data
data, is_connected = get_soil_data()

# Enhanced connection status display
if is_connected and 'message' not in data:
    st.sidebar.markdown(
        '<div><span class="status-indicator status-online"></span><strong>Server Online</strong></div>',
        unsafe_allow_html=True
    )
    st.sidebar.success("✅ Connected to sensors")
    st.sidebar.info(f"🕒 Last ping: {datetime.now().strftime('%H:%M:%S')}")
else:
    st.sidebar.markdown(
        '<div><span class="status-indicator status-offline"></span><strong>Server Offline</strong></div>',
        unsafe_allow_html=True
    )
    st.sidebar.error("❌ Connection failed")
    st.sidebar.warning("⚠ Check server status")

# System info in sidebar
st.sidebar.markdown("### 📊 System Info")
if st.session_state.data_history:
    st.sidebar.metric("📈 Data Points", len(st.session_state.data_history))
    st.sidebar.metric("🕒 Session Duration", f"{len(st.session_state.data_history) * refresh_interval // 60} min")

# Weather refresh status in sidebar
st.sidebar.markdown("### 🌤 Weather Status")
if st.session_state.weather_last_updated:
    time_since_weather_update = datetime.now() - st.session_state.weather_last_updated
    minutes_since_update = int(time_since_weather_update.total_seconds() // 60)
    
    if minutes_since_update < 60:
        st.sidebar.success(f"☀️ Updated {minutes_since_update}m ago")
        next_update = 60 - minutes_since_update
        st.sidebar.info(f"⏰ Next update in {next_update}m")
    else:
        st.sidebar.warning("🔄 Updating weather...")
else:
    st.sidebar.info("🌤 Loading weather data...")

# Enhanced soil analysis function
def get_soil_recommendations(nitrogen, phosphorus, potassium, ec, moisture, humidity, temperature):
    """
    Generate comprehensive soil health recommendations based on sensor parameters.
    
    Args:
        nitrogen (int): Nitrogen level in mg/kg
        phosphorus (int): Phosphorus level in mg/kg  
        potassium (int): Potassium level in mg/kg
        ec (int): Electrical conductivity in µS/cm
        moisture (float): Soil moisture percentage
        humidity (float): Humidity percentage
        temperature (float): Temperature in °C
        
    Returns:
        list: List of recommendation strings with priority levels
    """
    recommendations = []
    
    # Nitrogen recommendations
    if nitrogen < 20:
        recommendations.append({
            "type": "critical",
            "icon": "🚨",
            "parameter": "Nitrogen",
            "message": "Nitrogen level is low. Consider adding nitrogen fertilizers such as urea or organic manure.",
            "action": "Add nitrogen-rich fertilizers immediately"
        })
    elif 20 <= nitrogen <= 50:
        recommendations.append({
            "type": "good",
            "icon": "✅",
            "parameter": "Nitrogen",
            "message": "Nitrogen level is adequate.",
            "action": "Continue current nitrogen management"
        })
    else:  # nitrogen > 50
        recommendations.append({
            "type": "warning",
            "icon": "⚠",
            "parameter": "Nitrogen",
            "message": "Nitrogen level is high. Avoid excess nitrogen to prevent nutrient runoff.",
            "action": "Reduce nitrogen fertilizer application"
        })
    
    # Phosphorus recommendations
    if phosphorus < 15:
        recommendations.append({
            "type": "critical",
            "icon": "🚨",
            "parameter": "Phosphorus",
            "message": "Phosphorus level is low. Add phosphorus fertilizers like bone meal or rock phosphate.",
            "action": "Apply phosphate fertilizers or organic amendments"
        })
    elif 15 <= phosphorus <= 40:
        recommendations.append({
            "type": "good",
            "icon": "✅",
            "parameter": "Phosphorus",
            "message": "Phosphorus level is adequate.",
            "action": "Maintain current phosphorus levels"
        })
    else:  # phosphorus > 40
        recommendations.append({
            "type": "warning",
            "icon": "⚠",
            "parameter": "Phosphorus",
            "message": "Phosphorus level is high. Excess phosphorus can inhibit micronutrient uptake.",
            "action": "Avoid additional phosphorus fertilizers"
        })
    
    # Potassium recommendations
    if potassium < 100:
        recommendations.append({
            "type": "critical",
            "icon": "🚨",
            "parameter": "Potassium",
            "message": "Potassium level is low. Add potassium fertilizers like potassium sulfate or muriate of potash.",
            "action": "Apply potassium-rich fertilizers"
        })
    elif 100 <= potassium <= 200:
        recommendations.append({
            "type": "good",
            "icon": "✅",
            "parameter": "Potassium",
            "message": "Potassium level is adequate.",
            "action": "Continue current potassium management"
        })
    else:  # potassium > 200
        recommendations.append({
            "type": "warning",
            "icon": "⚠",
            "parameter": "Potassium",
            "message": "Potassium level is high. Excess potassium may interfere with magnesium and calcium uptake.",
            "action": "Reduce potassium fertilizer application"
        })
    
    # Electrical Conductivity recommendations
    if ec < 100:
        recommendations.append({
            "type": "warning",
            "icon": "🔍",
            "parameter": "Electrical Conductivity",
            "message": "Soil salinity is low; nutrients may be deficient.",
            "action": "Consider adding balanced fertilizers to improve nutrient availability"
        })
    elif 100 <= ec <= 1400:
        recommendations.append({
            "type": "good",
            "icon": "✅",
            "parameter": "Electrical Conductivity",
            "message": "Soil salinity is normal.",
            "action": "Maintain current soil management practices"
        })
    else:  # ec > 1400
        recommendations.append({
            "type": "critical",
            "icon": "🚨",
            "parameter": "Electrical Conductivity",
            "message": "High soil salinity detected. Consider leaching or soil amendments.",
            "action": "Implement soil leaching or add gypsum to reduce salinity"
        })
    
    # Soil Moisture recommendations
    if moisture < 20:
        recommendations.append({
            "type": "critical",
            "icon": "💧",
            "parameter": "Soil Moisture",
            "message": "Soil moisture is low. Irrigation is recommended.",
            "action": "Increase irrigation frequency and consider mulching"
        })
    elif 20 <= moisture <= 60:
        recommendations.append({
            "type": "good",
            "icon": "✅",
            "parameter": "Soil Moisture",
            "message": "Soil moisture is adequate.",
            "action": "Continue current irrigation schedule"
        })
    else:  # moisture > 60
        recommendations.append({
            "type": "warning",
            "icon": "🌊",
            "parameter": "Soil Moisture",
            "message": "Soil moisture is high. Risk of waterlogging; improve drainage.",
            "action": "Reduce irrigation and improve soil drainage"
        })
    
    # Humidity recommendations
    if humidity < 40:
        recommendations.append({
            "type": "warning",
            "icon": "🏜",
            "parameter": "Humidity",
            "message": "Humidity is low. Increase irrigation or mulching to retain moisture.",
            "action": "Apply mulch and increase watering frequency"
        })
    elif 40 <= humidity <= 70:
        recommendations.append({
            "type": "good",
            "icon": "✅",
            "parameter": "Humidity",
            "message": "Humidity is optimal.",
            "action": "Maintain current moisture management"
        })
    else:  # humidity > 70
        recommendations.append({
            "type": "critical",
            "icon": "🍄",
            "parameter": "Humidity",
            "message": "Humidity is high. Risk of fungal diseases; improve air circulation.",
            "action": "Improve ventilation and reduce watering to prevent fungal growth"
        })
    
    # Temperature recommendations
    if temperature < 15:
        recommendations.append({
            "type": "warning",
            "icon": "🧊",
            "parameter": "Temperature",
            "message": "Soil temperature is low. Consider warming methods for better crop growth.",
            "action": "Use row covers, mulch, or greenhouse protection"
        })
    elif 15 <= temperature <= 30:
        recommendations.append({
            "type": "good",
            "icon": "✅",
            "parameter": "Temperature",
            "message": "Soil temperature is optimal.",
            "action": "Continue current temperature management"
        })
    else:  # temperature > 30
        recommendations.append({
            "type": "critical",
            "icon": "🔥",
            "parameter": "Temperature",
            "message": "Soil temperature is high. Consider mulching or shading to reduce heat stress.",
            "action": "Apply cooling mulch and provide shade protection"
        })
    
    return recommendations

# Function to create a gauge chart
def create_gauge_chart(value, title, min_val, max_val, optimal_min, optimal_max, unit, delta=None, delta_ref=None):
    # Define color ranges
    critical_color = "#f44336"  # Red
    warning_color = "#ff9800"   # Yellow
    optimal_color = "#4CAF50"   # Green

    # Determine color based on value
    if value < optimal_min or value > optimal_max:
        gauge_color = critical_color
    elif optimal_min <= value <= optimal_max:
        gauge_color = optimal_color
    else:
        gauge_color = warning_color

    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number" + (f"+delta" if delta is not None else ""),
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"{title} ({unit})", 'font': {'size': 16}},
        delta={'reference': delta_ref, 'increasing': {'color': "#4CAF50"}, 'decreasing': {'color': "#f44336"}} if delta is not None else None,
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1, 'tickcolor': "black"},
            'bar': {'color': gauge_color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [min_val, optimal_min], 'color': critical_color},
                {'range': [optimal_min, optimal_max], 'color': optimal_color},
                {'range': [optimal_max, max_val], 'color': warning_color}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "black", 'family': "Roboto"}
    )
    return fig

# Function to control relay
def control_relay(command):
    try:
        response = requests.post(
            "http://localhost:8000/control-relay", 
            json={"command": command},
            timeout=5
        )
        response.raise_for_status()
        return response.json(), True
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to server"}, False
    except requests.exceptions.Timeout:
        return {"error": "Request timeout"}, False
    except Exception as e:
        return {"error": str(e)}, False

# Function to get weather data from OpenWeatherMap API
def get_weather_data():
    """
    Get current weather data from OpenWeatherMap API
    You'll need to get a free API key from: https://openweathermap.org/api
    """
    # Get API key and city from environment variables
    API_KEY = os.getenv('OPENWEATHER_API_KEY', 'your_openweather_api_key_here')
    CITY = os.getenv('CITY', 'Chennai')
    
    # For demo purposes, return mock data if no API key is set
    if API_KEY == "your_openweather_api_key_here":
        return {
            "temperature": 28.5,
            "humidity": 65,
            "description": "Partly Cloudy",
            "wind_speed": 12.5,
            "pressure": 1013,
            "visibility": 10,
            "icon": "02d",
            "city": "Demo City",
            "country": "IN",
            "demo": True
        }
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"].title(),
            "wind_speed": data["wind"]["speed"],
            "pressure": data["main"]["pressure"],
            "visibility": data.get("visibility", 0) / 1000,  # Convert to km
            "icon": data["weather"][0]["icon"],
            "city": data["name"],
            "country": data["sys"]["country"],
            "demo": False
        }
    except Exception as e:
        # Return fallback data if API fails
        return {
            "temperature": "N/A",
            "humidity": "N/A",
            "description": "Weather data unavailable",
            "wind_speed": "N/A",
            "pressure": "N/A",
            "visibility": "N/A",
            "icon": "01d",
            "city": "Unknown",
            "country": "",
            "demo": True,
            "error": str(e)
        }

# Enhanced main dashboard content
if is_connected and 'message' not in data and 'error' not in data:
    # Manage data history with custom retention
    if len(st.session_state.data_history) >= data_retention:
        st.session_state.data_history.pop(0)
    
    data_with_time = {**data, 'reading_time': datetime.now()}
    st.session_state.data_history.append(data_with_time)
    
    # Enhanced status bar
    col_status1, col_status2, col_status3 = st.columns(3)
    with col_status1:
        st.markdown(f'<div class="custom-metric">🕒 <strong>{datetime.now().strftime("%H:%M:%S")}</strong></div>', unsafe_allow_html=True)
    with col_status2:
        # Display current irrigation mode
        current_mode = data.get('mode', 'auto')
        mode_icon = "🤖" if current_mode == "auto" else "🎛"
        mode_color = "#4CAF50" if current_mode == "auto" else "#FF9800"
        st.markdown(f'<div class="custom-metric" style="border-left-color: {mode_color};">{mode_icon} <strong>{current_mode.upper()} Mode</strong></div>', unsafe_allow_html=True)
    with col_status3:
        st.markdown(f'<div class="custom-metric">🔄 <strong>{refresh_interval}s Refresh</strong></div>', unsafe_allow_html=True)

    # Weather Information Widget
    st.markdown("## 🌤 Current Weather Conditions")
    weather_data = get_cached_weather_data()
    
    # Create weather display columns
    weather_col1, weather_col2, weather_col3 = st.columns([2, 2, 2])
    
    with weather_col1:
        # Main weather info
        demo_text = " (Demo Data)" if weather_data.get('demo', False) else ""
        st.markdown(f"""
        <div class="weather-widget">
            <h3 style="margin: 0;">🌡 {weather_data['temperature']}°C</h3>
            <p style="margin: 0.5rem 0; font-size: 1.1rem;">{weather_data['description']}</p>
            <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">📍 {weather_data['city']}, {weather_data['country']}{demo_text}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with weather_col2:
        # Additional weather details
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #00c851, #007e33); color: white; 
                    padding: 1rem; border-radius: 10px; margin: 1rem 0; text-align: center;">
            <h4 style="margin: 0;">💧 Humidity</h4>
            <h3 style="margin: 0.5rem 0;">{weather_data['humidity']}%</h3>
            <p style="margin: 0; font-size: 0.9rem;">Atmospheric</p>
        </div>
        """, unsafe_allow_html=True)
    
    with weather_col3:
        # Wind and pressure info
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ff6b6b, #ee5a24); color: white; 
                    padding: 1rem; border-radius: 10px; margin: 1rem 0; text-align: center;">
            <h4 style="margin: 0;">🌬 Wind</h4>
            <h3 style="margin: 0.5rem 0;">{weather_data['wind_speed']} m/s</h3>
            <p style="margin: 0; font-size: 0.9rem;">Pressure: {weather_data['pressure']} hPa</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Weather insights for agriculture
    if not weather_data.get('demo', False):
        st.markdown("### 🌾 Weather Impact on Agriculture")
        
        # Analyze weather for farming recommendations
        temp = weather_data.get('temperature', 0)
        humidity = weather_data.get('humidity', 0)
        wind = weather_data.get('wind_speed', 0)
        
        weather_insights = []
        
        if isinstance(temp, (int, float)):
            if temp > 35:
                weather_insights.append("🔥 **High Temperature Alert**: Consider providing shade for crops and increase irrigation frequency.")
            elif temp < 10:
                weather_insights.append("🧊 **Low Temperature Warning**: Protect sensitive crops from frost damage.")
            elif 20 <= temp <= 30:
                weather_insights.append("✅ **Optimal Temperature**: Good conditions for most crop growth.")
        
        if isinstance(humidity, (int, float)):
            if humidity > 85:
                weather_insights.append("🍄 **High Humidity**: Monitor for fungal diseases and improve air circulation.")
            elif humidity < 30:
                weather_insights.append("🏜 **Low Humidity**: Increase irrigation and consider mulching to retain moisture.")
        
        if isinstance(wind, (int, float)):
            if wind > 15:
                weather_insights.append("💨 **Strong Wind**: Secure tall plants and check for wind damage.")
        
        if weather_insights:
            for insight in weather_insights:
                st.markdown(f"• {insight}")
        else:
            st.markdown("✅ **Favorable Conditions**: Current weather is suitable for normal agricultural activities.")
    
    # Irrigation Relay Status Display - MOVED TO TOP
    st.markdown("## 💧 Irrigation Control System")
    
    relay_status = data.get('relay', 'Unknown')
    current_mode = data.get('mode', 'auto')
    
    # Create control layout
    control_col1, control_col2, control_col3 = st.columns([2, 2, 2])
    
    with control_col1:
        # Mode Toggle Button
        if current_mode == "auto":
            if st.button("🤖 AUTO MODE", use_container_width=True, type="primary", key="mode_toggle"):
                # Switch to Manual Mode
                try:
                    result, success = control_relay("OFF")  # Force to manual mode
                    if success:
                        st.success("🎛 Switched to Manual Mode!")
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            if st.button("🎛 MANUAL MODE", use_container_width=True, key="mode_toggle"):
                # Switch to Auto Mode
                try:
                    response = requests.post("http://localhost:8000/set-auto-mode", timeout=5)
                    if response.status_code == 200:
                        st.success("🤖 Switched to Auto Mode!")
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with control_col2:
        # Relay Status Display - Use session state if available for immediate feedback
        current_relay_status = st.session_state.get('current_relay_status', relay_status)
        
        if current_relay_status.upper() == 'ON':
            st.markdown("""
            <div style="background: linear-gradient(135deg, #4CAF50, #45a049); color: white; 
                        padding: 1rem; border-radius: 15px; text-align: center; margin: 0.2rem 0;
                        box-shadow: 0 4px 20px rgba(76, 175, 80, 0.4);">
                <h3 style="margin: 0;">💧 RELAY ON</h3>
            </div>
            """, unsafe_allow_html=True)
        elif current_relay_status.upper() == 'OFF':
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f44336, #d32f2f); color: white; 
                        padding: 1rem; border-radius: 15px; text-align: center; margin: 0.2rem 0;
                        box-shadow: 0 4px 20px rgba(244, 67, 54, 0.4);">
                <h3 style="margin: 0;">⭕ RELAY OFF</h3>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #ff9800, #f57c00); color: white; 
                        padding: 1rem; border-radius: 15px; text-align: center; margin: 0.2rem 0;
                        box-shadow: 0 4px 20px rgba(255, 152, 0, 0.4);">
                <h3 style="margin: 0;">❓ UNKNOWN</h3>
            </div>
            """, unsafe_allow_html=True)
    
    with control_col3:
        # Manual Controls (only show when in manual mode)
        if current_mode == "manual":
            manual_col_a, manual_col_b = st.columns(2)
            
            with manual_col_a:
                if st.button("🟢 ON", use_container_width=True, type="primary", key="manual_on"):
                    result, success = control_relay("ON")
                    if success:
                        st.success("✅ Relay turned ON")
                        # Update relay status immediately in session state
                        if 'current_relay_status' not in st.session_state:
                            st.session_state.current_relay_status = 'ON'
                        else:
                            st.session_state.current_relay_status = 'ON'
                        
                        time.sleep(0.5)  # Brief pause for server to update
                        st.rerun()
                    else:
                        st.error("❌ Failed to control relay")
            
            with manual_col_b:
                if st.button("🔴 OFF", use_container_width=True, key="manual_off"):
                    result, success = control_relay("OFF")
                    if success:
                        st.success("✅ Relay turned OFF")
                        # Update relay status immediately in session state
                        if 'current_relay_status' not in st.session_state:
                            st.session_state.current_relay_status = 'OFF'
                        else:
                            st.session_state.current_relay_status = 'OFF'
                        
                        time.sleep(0.5)  # Brief pause for server to update
                        st.rerun()
                    else:
                        st.error("❌ Failed to control relay")
        else:
            # Show current auto mode status
            st.markdown("""
            <div style="background: linear-gradient(135deg, #2196F3, #1976D2); color: white; 
                        padding: 1rem; border-radius: 15px; text-align: center; margin: 0.2rem 0;
                        box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);">
                <h3 style="margin: 0;">🤖 AUTO ACTIVE</h3>
            </div>
            """, unsafe_allow_html=True)
    
    # Quick stats overview
    if len(st.session_state.data_history) > 1:
        df = pd.DataFrame(st.session_state.data_history)
        st.markdown("""
        <div class="quick-stats">
            <div class="stat-item">
                <div class="stat-value">🌡 {:.1f}°C</div>
                <div class="stat-label">Avg Temp</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">💧 {:.1f}%</div>
                <div class="stat-label">Avg Humidity</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">🧪 {:.1f}</div>
                <div class="stat-label">Avg pH</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">📈 {}</div>
                <div class="stat-label">Trend</div>
            </div>
        </div>
        """.format(
            df['temperature'].mean(),
            df['humidity'].mean(),
            df['ph'].mean(),
            "📈 Rising" if df['temperature'].iloc[-1] > df['temperature'].mean() else "📉 Falling"
        ), unsafe_allow_html=True)

    # Enhanced metrics display with gauge charts
    st.markdown("## 📊 Real-Time Soil Parameters")
    
    # NPK Row with gauge charts
    col1, col2, col3 = st.columns(3)
    
    with col1:
        nitrogen_fig = create_gauge_chart(
            value=data['nitrogen'],
            title="Nitrogen (N)",
            min_val=0,
            max_val=100,
            optimal_min=20,
            optimal_max=50,
            unit="mg/kg",
            delta=data['nitrogen'] - 25 if len(st.session_state.data_history) > 1 else None,
            delta_ref=25 if len(st.session_state.data_history) > 1 else None
        )
        st.plotly_chart(nitrogen_fig, use_container_width=True)
        
    with col2:
        phosphorus_fig = create_gauge_chart(
            value=data['phosphorus'],
            title="Phosphorus (P)",
            min_val=0,
            max_val=80,
            optimal_min=15,
            optimal_max=40,
            unit="mg/kg",
            delta=data['phosphorus'] - 27 if len(st.session_state.data_history) > 1 else None,
            delta_ref=27 if len(st.session_state.data_history) > 1 else None
        )
        st.plotly_chart(phosphorus_fig, use_container_width=True)
        
    with col3:
        potassium_fig = create_gauge_chart(
            value=data['potassium'],
            title="Potassium (K)",
            min_val=0,
            max_val=300,
            optimal_min=100,
            optimal_max=200,
            unit="mg/kg",
            delta=data['potassium'] - 150 if len(st.session_state.data_history) > 1 else None,
            delta_ref=150 if len(st.session_state.data_history) > 1 else None
        )
        st.plotly_chart(potassium_fig, use_container_width=True)
    
    # Environmental parameters row with gauge charts - now including temperature
    col4, col5, col6, col7 = st.columns(4)
    
    with col4:
        ph_fig = create_gauge_chart(
            value=data['ph'],
            title="pH Level",
            min_val=0,
            max_val=14,
            optimal_min=custom_ph_min,
            optimal_max=custom_ph_max,
            unit="",
            delta=data['ph'] - 7.0 if len(st.session_state.data_history) > 1 else None,
            delta_ref=7.0 if len(st.session_state.data_history) > 1 else None
        )
        st.plotly_chart(ph_fig, use_container_width=True)
        
    with col5:
        ec_fig = create_gauge_chart(
            value=data['ec'],
            title="Electrical Conductivity",
            min_val=0,
            max_val=2000,
            optimal_min=100,
            optimal_max=1400,
            unit="µS/cm",
            delta=data['ec'] - 750 if len(st.session_state.data_history) > 1 else None,
            delta_ref=750 if len(st.session_state.data_history) > 1 else None
        )
        st.plotly_chart(ec_fig, use_container_width=True)
        
    with col6:
        humidity_fig = create_gauge_chart(
            value=data['humidity'],
            title="Soil Moisture",
            min_val=0,
            max_val=100,
            optimal_min=40,
            optimal_max=custom_humidity_max,
            unit="%",
            delta=data['humidity'] - 55 if len(st.session_state.data_history) > 1 else None,
            delta_ref=55 if len(st.session_state.data_history) > 1 else None
        )
        st.plotly_chart(humidity_fig, use_container_width=True)
    
    with col7:
        temp_fig = create_gauge_chart(
            value=data['temperature'],
            title="Temperature",
            min_val=0,
            max_val=50,
            optimal_min=15,
            optimal_max=custom_temp_max,
            unit="°C",
            delta=data['temperature'] - 25 if len(st.session_state.data_history) > 1 else None,
            delta_ref=25 if len(st.session_state.data_history) > 1 else None
        )
        st.plotly_chart(temp_fig, use_container_width=True)

    # Enhanced charts with more visualization options
    if len(st.session_state.data_history) > 1:
        st.markdown("## 📈 Advanced Analytics & Trends")
        
        # Chart type selector
        chart_type = st.selectbox(
            "📊 Select Chart Type",
            ["Multi-Parameter View", "Individual Parameters", "Correlation Matrix", "Trend Analysis"]
        )
        
        df = pd.DataFrame(st.session_state.data_history)
        df['reading_time'] = pd.to_datetime(df['reading_time'])
        
        if chart_type == "Multi-Parameter View":
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('NPK Levels', 'pH & EC', 'Environmental', 'Soil Moisture'),
                specs=[[{"secondary_y": False}, {"secondary_y": True}],
                       [{"secondary_y": True}, {"secondary_y": False}]]
            )
            
            # NPK Chart
            fig.add_trace(
                go.Scatter(x=df['reading_time'], y=df['nitrogen'], name='Nitrogen', line=dict(color='green')),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=df['reading_time'], y=df['phosphorus'], name='Phosphorus', line=dict(color='orange')),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=df['reading_time'], y=df['potassium'], name='Potassium', line=dict(color='purple')),
                row=1, col=1
            )
            
            # pH & EC Chart
            fig.add_trace(
                go.Scatter(x=df['reading_time'], y=df['ph'], name='pH', line=dict(color='blue')),
                row=1, col=2
            )
            fig.add_trace(
                go.Scatter(x=df['reading_time'], y=df['ec'], name='EC', line=dict(color='red')),
                row=1, col=2, secondary_y=True
            )
            
            # Environmental Chart (Temperature retained here)
            fig.add_trace(
                go.Scatter(x=df['reading_time'], y=df['temperature'], name='Temperature', line=dict(color='orange')),
                row=2, col=1
            )
            
            # Humidity Chart
            fig.add_trace(
                go.Scatter(x=df['reading_time'], y=df['humidity'], name='Humidity', line=dict(color='lightblue')),
                row=2, col=2
            )
            
            fig.update_layout(height=600, showlegend=True)
            fig.update_xaxes(title_text="Time")
            fig.update_yaxes(title_text="mg/kg", row=1, col=1)
            fig.update_yaxes(title_text="pH", row=1, col=2)
            fig.update_yaxes(title_text="µS/cm", row=1, col=2, secondary_y=True)
            fig.update_yaxes(title_text="°C", row=2, col=1)
            fig.update_yaxes(title_text="%", row=2, col=2)
            
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Individual Parameters":
            param_choice = st.selectbox("Select Parameter", 
                                      ["nitrogen", "phosphorus", "potassium", "ph", "ec", "humidity", "temperature"])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['reading_time'], 
                y=df[param_choice], 
                mode='lines+markers',
                name=param_choice.title(),
                line=dict(width=3)
            ))
            fig.update_layout(
                title=f"{param_choice.title()} Trend Over Time",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
        elif chart_type == "Correlation Matrix":
            numeric_cols = ['nitrogen', 'phosphorus', 'potassium', 'ph', 'ec', 'humidity', 'temperature']
            corr_matrix = df[numeric_cols].corr()
            
            fig = px.imshow(corr_matrix, 
                          text_auto=True, 
                          aspect="auto",
                          title="Parameter Correlation Matrix")
            st.plotly_chart(fig, use_container_width=True)
            
        elif chart_type == "Trend Analysis":
            # Simple trend indicators
            st.markdown("### 📊 Trend Indicators")
            trend_cols = st.columns(4)
            
            for i, param in enumerate(['nitrogen', 'phosphorus', 'potassium', 'temperature']):
                if len(df) >= 3:
                    recent_trend = df[param].tail(3).diff().mean()
                    trend_icon = "📈" if recent_trend > 0 else "📉" if recent_trend < 0 else "➡"
                    trend_cols[i].metric(f"{trend_icon} {param.title()}", 
                                       f"{recent_trend:.2f}", 
                                       "Trend Direction")

    # Enhanced Recommendations based on soil data
    st.markdown('<div class="section-header"><h2>💡 Advanced Soil Health Analysis & Recommendations</h2></div>', unsafe_allow_html=True)
    
    # Get comprehensive recommendations
    recommendations = get_soil_recommendations(
        data['nitrogen'], 
        data['phosphorus'], 
        data['potassium'],
        data['ec'], 
        data['humidity'],  # Using humidity as soil moisture proxy
        data['humidity'], 
        data['temperature']
    )
    
    # Categorize recommendations by type
    critical_recs = [r for r in recommendations if r['type'] == 'critical']
    warning_recs = [r for r in recommendations if r['type'] == 'warning']
    good_recs = [r for r in recommendations if r['type'] == 'good']
    
    # Create columns for better layout
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Critical Issues Section
        if critical_recs:
            st.markdown("### 🚨 Critical Issues Requiring Immediate Attention")
            for rec in critical_recs:
                st.markdown(f"""
                <div class="recommendation-card critical-rec">
                    <div class="rec-header">
                        {rec['icon']} <strong>{rec['parameter']}</strong>
                    </div>
                    <div class="rec-message">
                        {rec['message']}
                    </div>
                    <div class="rec-action">
                        💡 <strong>Recommended Action:</strong> {rec['action']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Warning Issues Section
        if warning_recs:
            st.markdown("### ⚠ Optimization Recommendations")
            for rec in warning_recs:
                st.markdown(f"""
                <div class="recommendation-card warning-rec">
                    <div class="rec-header">
                        {rec['icon']} <strong>{rec['parameter']}</strong>
                    </div>
                    <div class="rec-message">
                        {rec['message']}
                    </div>
                    <div class="rec-action">
                        💡 <strong>Recommended Action:</strong> {rec['action']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with col_right:
        # Overall Soil Health Score
        st.markdown('<div class="health-score-container">', unsafe_allow_html=True)
        st.markdown("### 📊 Overall Soil Health Score")
        
        # Create a progress bar for health score
        optimal_count = len(good_recs)
        total_params = len(recommendations)
        health_score = (optimal_count / total_params) * 100
        
        # Health score display with color coding
        if health_score >= 80:
            st.success(f"🌟 *Excellent:* {health_score:.0f}% optimal")
            score_color = "#4CAF50"
        elif health_score >= 60:
            st.info(f"👍 *Good:* {health_score:.0f}% optimal")
            score_color = "#2196F3"
        elif health_score >= 40:
            st.warning(f"⚠ *Fair:* {health_score:.0f}% optimal")
            score_color = "#FF9800"
        else:
            st.error(f"🚨 *Poor:* {health_score:.0f}% optimal")
            score_color = "#f44336"
        
        # Custom progress bar
        st.markdown(f"""
        <div style="background: #e0e0e0; border-radius: 10px; overflow: hidden; margin: 1rem 0;">
            <div style="background: {score_color}; height: 25px; width: {health_score}%; 
                        display: flex; align-items: center; justify-content: center; 
                        color: white; font-weight: bold; font-size: 0.9rem;">
                {health_score:.0f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Parameters summary
        st.markdown("*Parameter Status:*")
        st.markdown(f"✅ Optimal: *{optimal_count}* parameters")
        st.markdown(f"⚠ Needs Attention: *{len(warning_recs)}* parameters")
        st.markdown(f"🚨 Critical: *{len(critical_recs)}* parameters")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Good Parameters (Collapsible)
        if good_recs:
            with st.expander("✅ Parameters in Optimal Range", expanded=False):
                for rec in good_recs:
                    st.markdown(f"""
                    <div class="recommendation-card good-rec">
                        <div class="rec-header">
                            {rec['icon']} <strong>{rec['parameter']}</strong>
                        </div>
                        <div class="rec-message">
                            {rec['message']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Fertilizer Recommendations Section
    st.markdown('<div class="fertilizer-container">', unsafe_allow_html=True)
    st.markdown("### 🌿 Smart Fertilizer Recommendations")
    
    fertilizer_needs = []
    if data['nitrogen'] < 20:
        fertilizer_needs.append({
            "nutrient": "Nitrogen (N)",
            "products": "Urea (46-0-0) or Ammonium Nitrate (34-0-0)",
            "icon": "🟢",
            "current": data['nitrogen'],
            "target": "20-50 mg/kg"
        })
    if data['phosphorus'] < 15:
        fertilizer_needs.append({
            "nutrient": "Phosphorus (P)",
            "products": "Triple Superphosphate (0-46-0) or Bone Meal",
            "icon": "🟠",
            "current": data['phosphorus'],
            "target": "15-40 mg/kg"
        })
    if data['potassium'] < 100:
        fertilizer_needs.append({
            "nutrient": "Potassium (K)",
            "products": "Muriate of Potash (0-0-60) or Potassium Sulfate",
            "icon": "🟣",
            "current": data['potassium'],
            "target": "100-200 mg/kg"
        })
    
    if fertilizer_needs:
        st.markdown("📋 *Based on current soil analysis, your soil requires:*")
        
        # Create fertilizer recommendation cards
        for fert in fertilizer_needs:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.8); border-radius: 10px; padding: 1rem; 
                        margin: 0.5rem 0; border-left: 4px solid #4CAF50;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{fert['icon']} {fert['nutrient']}</strong><br>
                        <span style="color: #666; font-size: 0.9rem;">
                            Current: {fert['current']} mg/kg | Target: {fert['target']}
                        </span>
                    </div>
                    <div style="text-align: right; color: #2c3e50;">
                        <strong>Recommended:</strong><br>
                        <span style="font-size: 0.9rem;">{fert['products']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Application timing recommendations
        st.markdown("⏰ *Application Timing:*")
        st.markdown("• Apply fertilizers during early morning or late evening")
        st.markdown("• Water thoroughly after application")
        st.markdown("• Wait 7-14 days between applications")
        
    else:
        st.markdown("""
        <div style="background: rgba(76, 175, 80, 0.1); border-radius: 10px; padding: 1.5rem; 
                    text-align: center; border: 2px solid #4CAF50;">
            <h3 style="color: #4CAF50; margin: 0;">🎉 Excellent Soil Nutrition!</h3>
            <p style="margin: 0.5rem 0;">All major nutrients are within optimal ranges. 
            Continue with your current soil management practices.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
elif 'message' in data and data['message'] == "No data found":
    st.markdown("""
    <div style="text-align: center; padding: 3rem; background: linear-gradient(145deg, #fff9c4, #fff59d); border-radius: 15px; margin: 2rem 0;">
        <h2>⏳ Waiting for Sensor Data</h2>
        <p>No readings available yet. Your NodeMCU should start sending data shortly.</p>
        <div style="margin-top: 2rem;">
            <strong>✅ Checklist:</strong><br>
            • NodeMCU powered on<br>
            • Connected to WiFi (SEED-IOT-LAB)<br>
            • Server IP correctly configured (192.168.0.106:8000)<br>
            • Soil sensors connected via Modbus
        </div>
    </div>
    """, unsafe_allow_html=True)
    
else:
    st.markdown("""
    <div style="text-align: center; padding: 3rem; background: linear-gradient(145deg, #ffcdd2, #ef9a9a); border-radius: 15px; margin: 2rem 0;">
        <h2>❌ Connection Error</h2>
        <p>Cannot connect to the FastAPI server.</p>
        <div style="margin-top: 2rem;">
            <strong>🔧 Troubleshooting:</strong><br>
            • Check if server.py is running<br>
            • Verify port 8000 is available<br>
            • Restart the FastAPI server<br>
            • Check firewall settings
        </div>
    </div>
    """, unsafe_allow_html=True)

# Enhanced auto-refresh with countdown
if refresh_interval > 0:
    # Wait for refresh interval without showing countdown
    time.sleep(refresh_interval)
    st.rerun()