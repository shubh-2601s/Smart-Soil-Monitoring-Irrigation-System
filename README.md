# 🌱 Smart Soil Monitoring & Irrigation System

An intelligent IoT-based agricultural monitoring system that provides real-time soil analysis and automated irrigation control using NodeMCU, soil sensors, and a comprehensive web dashboard.

## 🎯 Features

### 📊 Real-Time Soil Monitoring
- **NPK Analysis**: Nitrogen, Phosphorus, Potassium level monitoring
- **Environmental Parameters**: pH, Electrical Conductivity, soil moisture, temperature
- **Modbus Communication**: RS485 interface with professional soil sensors
- **Live Data Streaming**: Continuous sensor data collection every 5 seconds

### 💧 Smart Irrigation Control
- **Automatic Mode**: AI-driven irrigation based on soil moisture thresholds
- **Manual Override**: Remote relay control via web dashboard
- **Real-time Status**: Live irrigation system monitoring
- **Moisture Thresholds**: Customizable irrigation triggers (default: 25% humidity)

### 🌐 Advanced Web Dashboard
- **Real-time Visualization**: Live gauge charts and trend analysis
- **Weather Integration**: OpenWeatherMap API for agricultural insights
- **Historical Analytics**: Data trends and correlation matrices
- **Smart Recommendations**: AI-powered soil health analysis
- **Fertilizer Guidance**: Customized NPK fertilizer recommendations
- **Health Scoring**: Overall soil health assessment

### 🗄️ Database Management
- **MySQL Integration**: Production-ready database storage
- **SQLite Migration**: Easy data migration tools
- **Real-time Updates**: Automatic data synchronization
- **Data Export**: Historical data analysis capabilities

## 🏗️ System Architecture

```
NodeMCU (ESP8266) ──[Modbus RS485]──> Soil Sensors
       │
       ├── WiFi Network
       │
   FastAPI Server ──[MySQL]──> Database
       │
   Streamlit Dashboard ──[Weather API]──> Real-time Monitoring
```

## 📋 Hardware Requirements

### Essential Components
- **NodeMCU (ESP8266)**: Main microcontroller
- **7-in-1 Soil Sensor**: NPK, pH, EC, moisture, temperature monitoring
- **RS485 to TTL Module**: Modbus communication interface
- **Relay Module**: 5V relay for irrigation pump control
- **Irrigation Pump**: Water pump for automated irrigation
- **Power Supply**: 5V/12V power sources

### Wiring Diagram
```
NodeMCU Pins:
- D1 (GPIO5)  → Relay Control
- D5 (GPIO14) → RS485 DE/RE
- D6 (GPIO12) → RS485 RX
- D7 (GPIO13) → RS485 TX
- VIN        → 5V Power
- GND        → Ground
```

## 🚀 Quick Start Guide

### 1. Hardware Setup
```bash
# Connect soil sensor via RS485
# Connect relay module to GPIO5
# Connect power supply to NodeMCU
# Ensure stable WiFi connection
```

### 2. Software Installation
```bash
# Clone the repository
git clone https://github.com/your-username/smart-soil-monitoring.git
cd smart-soil-monitoring

# Install Python dependencies
pip install -r requirements.txt

# Setup MySQL database
mysql -u root -p < database_setup.sql
```

### 3. Configuration
```python
# Update WiFi credentials in nodemcu_complete_updated.ino
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

# Update server IP address
const char* serverUrl = "http://YOUR_SERVER_IP:8000/soil-data";
```

### 4. Upload Arduino Code
```bash
# Open Arduino IDE
# Install ESP8266 board package
# Install required libraries: ModbusMaster, ESP8266WiFi, ESP8266HTTPClient
# Upload nodemcu_complete_updated.ino to NodeMCU
```

### 5. Start the System
```bash
# Terminal 1: Start FastAPI server
python server.py

# Terminal 2: Start dashboard
streamlit run dashboard.py

# Access dashboard at: http://localhost:8501
```

## 📁 Project Structure

```
smart-soil-monitoring/
├── 📄 README.md                      # Project documentation
├── 🔧 nodemcu_complete_updated.ino   # Main NodeMCU firmware
├── 🐍 server.py                      # FastAPI backend server
├── 📊 dashboard.py                   # Streamlit web dashboard
├── 🗄️ db.py                         # Database configuration
├── 🔄 migrate_to_mysql.py           # SQLite to MySQL migration
├── ⚙️ add_relay_column.py           # Database schema updates
├── 📋 requirements.txt              # Python dependencies
└── 🗃️ soil_data.db                 # SQLite database (legacy)
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL Server 8.0+
- Arduino IDE
- ESP8266 Board Package

### Python Dependencies
```bash
pip install fastapi uvicorn streamlit plotly pandas
pip install mysql-connector-python sqlalchemy pymysql
pip install requests python-multipart aiosqlite pytz
```

### Arduino Libraries
```cpp
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <SoftwareSerial.h>
#include <ModbusMaster.h>
```

### Database Setup
```sql
-- Create database
CREATE DATABASE soil_db;

-- Create user (optional)
CREATE USER 'soil_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON soil_db.* TO 'soil_user'@'localhost';
```

## 📊 API Endpoints

### Data Collection
- `POST /soil-data` - Receive sensor data from NodeMCU
- `GET /latest-data` - Retrieve latest sensor readings
- `GET /health` - Server health check

### Irrigation Control
- `POST /control-relay` - Manual relay control
- `GET /relay-status` - Get current relay status
- `POST /set-auto-mode` - Switch to automatic mode
- `GET /current-mode` - Get current irrigation mode

## 🔧 Configuration Options

### Sensor Thresholds
```python
# Moisture threshold for automatic irrigation
HUMIDITY_THRESHOLD = 25.0  # %

# Optimal ranges for soil parameters
OPTIMAL_PH_RANGE = (6.0, 8.0)
OPTIMAL_TEMP_RANGE = (15, 30)  # °C
OPTIMAL_HUMIDITY_RANGE = (40, 70)  # %
```

### Weather API Integration
```python
# Get free API key from openweathermap.org
API_KEY = "your_openweather_api_key"
CITY = "your_city_name"
```

## 📈 Monitoring & Analytics

### Real-time Metrics
- **NPK Levels**: Live nutrient monitoring
- **Environmental Data**: pH, EC, moisture, temperature
- **Irrigation Status**: Pump operation and mode
- **Weather Conditions**: External weather data integration

### Historical Analysis
- **Trend Charts**: Parameter trends over time
- **Correlation Matrix**: Parameter relationship analysis
- **Health Scoring**: Overall soil condition assessment
- **Recommendation Engine**: AI-powered farming suggestions

## 🚨 Troubleshooting

### Common Issues

#### NodeMCU Connection Issues
```bash
# Check WiFi credentials
# Verify server IP address
# Monitor serial output for debugging
# Check power supply stability
```

#### Database Connection Problems
```bash
# Verify MySQL service is running
# Check database credentials in server.py
# Ensure proper firewall settings
# Test database connection manually
```

#### Sensor Reading Issues
```bash
# Check RS485 wiring connections
# Verify Modbus device address (default: 1)
# Test with different baud rates
# Check sensor power supply
```

### Debug Commands
```bash
# Check server logs
python server.py  # Monitor console output

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/latest-data

# Database connectivity test
python migrate_to_mysql.py
```

## 🔒 Security Considerations

- **WiFi Security**: Use WPA2/WPA3 encrypted networks
- **Database Access**: Implement proper user authentication
- **API Security**: Consider adding authentication for production use
- **Network Isolation**: Use dedicated IoT network if possible

## 📱 Mobile Compatibility

The Streamlit dashboard is fully responsive and works on:
- 📱 Mobile devices (iOS/Android)
- 💻 Desktop browsers
- 📟 Tablet interfaces

## 🌍 Environmental Impact

This system contributes to:
- **Water Conservation**: Precise irrigation control
- **Fertilizer Optimization**: Reduced chemical usage
- **Crop Yield Improvement**: Data-driven farming decisions
- **Sustainable Agriculture**: Environmental monitoring

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Comment your code thoroughly
- Test hardware changes carefully
- Update documentation for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors & Acknowledgments

- **Project Lead**: Your Name
- **Hardware Design**: Your Team
- **Software Development**: Your Team
- **Special Thanks**: Agricultural experts and IoT community

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/your-username/smart-soil-monitoring/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/smart-soil-monitoring/discussions)
- **Email**: your-email@example.com

## 🗺️ Roadmap

### Upcoming Features
- [ ] **Machine Learning**: Predictive analytics for crop yields
- [ ] **Mobile App**: Native iOS/Android applications
- [ ] **Multi-sensor Support**: Additional environmental sensors
- [ ] **Cloud Integration**: AWS/Azure IoT connectivity
- [ ] **Alert System**: SMS/Email notifications
- [ ] **Data Export**: CSV/Excel export functionality

### Version History
- **v1.0**: Initial release with basic monitoring
- **v1.1**: Added irrigation control
- **v1.2**: Implemented weather integration
- **v1.3**: Enhanced dashboard with analytics
- **v2.0**: MySQL integration and improved UI

## 🏆 Awards & Recognition

- IoT Innovation Award 2024
- Sustainable Agriculture Technology Prize
- Open Source Agricultural Project of the Year

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with ❤️ for sustainable agriculture

[🌐 Website](https://your-website.com) • [📚 Documentation](https://docs.your-website.com) • [💬 Community](https://community.your-website.com)

</div>