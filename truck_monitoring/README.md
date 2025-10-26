# Truck Monitoring System

A comprehensive backend portal for monitoring truck traffic with user authentication, statistics, and detailed truck information.

## 🚀 Features

- **User Authentication**: Secure login with JWT tokens
- **Dashboard**: Real-time statistics and trends
- **Truck List**: Paginated list with images and details
- **Truck Details**: Complete information including video links
- **Statistics**: Daily, weekly, and hourly analytics
- **Search**: Find trucks by license plate or date
- **Fake Data**: Pre-populated with 30 days of sample data

## 📋 Requirements

- Python 3.9+
- MySQL 5.7+ or MariaDB 10.3+
- pip

## 🛠️ Installation

### 1. Install MySQL

Make sure MySQL is installed and running on your system.

```bash
# macOS (using Homebrew)
brew install mysql
brew services start mysql

# Ubuntu/Debian
sudo apt-get install mysql-server
sudo systemctl start mysql

# Windows
# Download and install from https://dev.mysql.com/downloads/mysql/
```

### 2. Create Database

```bash
# Log into MySQL
mysql -u root -p

# Run the init script
source database/init.sql

# Or manually create database
CREATE DATABASE truck_monitoring CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env file with your database credentials
nano .env
```

Update the `DATABASE_URL` in `.env`:
```
DATABASE_URL=mysql+pymysql://your_username:your_password@localhost:3306/truck_monitoring
```

### 4. Install Python Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Run the Server

```bash
# Make sure you're in the backend directory
cd backend

# Run with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8095 --reload

# Or run directly
python -m app.main
```

The server will start at **http://localhost:8095**

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8095/docs
- **ReDoc**: http://localhost:8095/redoc

## 🔐 Default Users

The system comes with two pre-created users:

| Username | Password | Role  |
|----------|----------|-------|
| admin    | admin123 | Admin |
| user     | user123  | User  |

## 📊 API Endpoints

### Authentication

```
POST /api/auth/register    - Register new user
POST /api/auth/login       - Login and get token
GET  /api/auth/me          - Get current user info
```

### Trucks

```
GET  /api/trucks/                    - List trucks (paginated)
GET  /api/trucks/{truck_id}          - Get truck details
GET  /api/trucks/search/by-plate/{plate} - Search by license plate
GET  /api/trucks/search/by-date/{date}   - Get trucks by date
```

### Statistics

```
GET  /api/statistics/dashboard    - Dashboard statistics
GET  /api/statistics/daily        - Daily statistics (last N days)
GET  /api/statistics/hourly/{date} - Hourly distribution
GET  /api/statistics/weekly       - Weekly trend
GET  /api/statistics/types        - Statistics by truck type
```

## 💾 Database Schema

### Users Table
```sql
- id (primary key)
- username (unique)
- email (unique)
- hashed_password
- full_name
- is_active
- is_admin
- created_at
```

### Trucks Table
```sql
- id (primary key)
- truck_number
- license_plate
- truck_type (Container, Flatbed, Tanker, etc.)
- length_meters
- weight_tons
- speed_kmh
- location
- direction
- pass_time
- date
- image_url
- video_url
- thumbnail_url
- company_name
- driver_name
- cargo_description
- notes
- created_at
- updated_at
```

### Daily Statistics Table
```sql
- id (primary key)
- date (unique)
- total_trucks
- avg_length
- avg_speed
- peak_hour
- peak_hour_count
- container_count
- flatbed_count
- tanker_count
- other_count
- created_at
- updated_at
```

## 🧪 Sample Data

The system automatically seeds fake data on first run:
- **2 Users**: admin and regular user
- **~1500 Truck Records**: Across 31 days (20-80 trucks per day)
- **31 Daily Statistics**: One for each day

## 📱 Usage Examples

### 1. Login

```bash
curl -X POST "http://localhost:8095/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Get Dashboard Statistics

```bash
curl -X GET "http://localhost:8095/api/statistics/dashboard" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. List Trucks

```bash
curl -X GET "http://localhost:8095/api/trucks/?page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Get Truck Details

```bash
curl -X GET "http://localhost:8095/api/trucks/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🎨 Frontend Integration

To integrate with a frontend:

1. **Login Flow**:
   - POST to `/api/auth/login` with username/password
   - Store the `access_token` in localStorage
   - Include token in all subsequent requests

2. **Example Header**:
```javascript
headers: {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
}
```

3. **Dashboard Example**:
```javascript
// Fetch dashboard stats
const response = await fetch('http://localhost:8095/api/statistics/dashboard', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const stats = await response.json();
```

## 🔧 Configuration

### Environment Variables

```env
# Database
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/truck_monitoring

# JWT Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server
HOST=0.0.0.0
PORT=8095
```

### Customization

- **Truck Types**: Edit `TRUCK_TYPES` in `seed_data.py`
- **Locations**: Edit `LOCATIONS` in `seed_data.py`
- **Images/Videos**: Replace URLs in `TRUCK_IMAGES` and `VIDEO_URLS`
- **Token Expiry**: Change `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env`

## 📁 Project Structure

```
truck_monitoring/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── database.py          # Database configuration
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── auth.py              # Authentication utilities
│   │   ├── seed_data.py         # Fake data generator
│   │   └── api/
│   │       ├── auth_routes.py   # Auth endpoints
│   │       ├── trucks.py        # Truck endpoints
│   │       └── statistics.py    # Statistics endpoints
│   ├── requirements.txt         # Python dependencies
│   └── env.example             # Environment template
├── database/
│   └── init.sql                # Database initialization
└── README.md                   # This file
```

## 🐛 Troubleshooting

### MySQL Connection Error

```
Error: Can't connect to MySQL server
```

**Solution**:
- Check if MySQL is running: `mysql.server status` (macOS) or `systemctl status mysql` (Linux)
- Verify credentials in `.env` file
- Check if database exists: `mysql -u root -p -e "SHOW DATABASES;"`

### Import Error

```
Error: No module named 'app'
```

**Solution**:
- Make sure you're in the `backend` directory
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### Port Already in Use

```
Error: Address already in use
```

**Solution**:
- Check what's using port 8095: `lsof -i :8095`
- Kill the process: `kill -9 PID`
- Or use a different port: `uvicorn app.main:app --port 8096`

## 📈 Performance

- **Pagination**: All list endpoints support pagination
- **Database Indexing**: Key columns are indexed for fast queries
- **Connection Pooling**: SQLAlchemy connection pooling enabled
- **CORS**: Configured for cross-origin requests

## 🔒 Security

- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: Signed tokens with expiry
- **SQL Injection**: Protected by SQLAlchemy ORM
- **Authentication**: All endpoints require valid token (except login/register)

## 📝 License

This project is for educational/demonstration purposes.

## 🤝 Support

For issues or questions, please check:
1. API documentation at `/docs`
2. This README file
3. Server logs for error messages

---

**Happy Monitoring! 🚛📊**

