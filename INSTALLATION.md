# Installation Guide - EuroLeague Stats Explorer

This guide will walk you through setting up the EuroLeague Stats Explorer on your local machine.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** ([Download here](https://www.python.org/downloads/))
- **pip** (Python package manager, usually comes with Python)
- **Git** ([Download here](https://git-scm.com/downloads))
- **MongoDB Atlas Account** (Free tier available at [mongodb.com](https://www.mongodb.com/cloud/atlas))
- A modern web browser (Chrome, Firefox, Safari, or Edge)

## 🔧 Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd euroleague-stats-explorer
```

### 2. Set Up Python Virtual Environment (Recommended)

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask
- Flask-SQLAlchemy
- Flask-CORS
- PyMongo
- Werkzeug
- certifi

### 4. Configure MongoDB Atlas

#### 4.1 Create MongoDB Atlas Cluster

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Sign up or log in
3. Create a free cluster (M0 tier)
4. Wait for cluster creation (takes 3-5 minutes)

#### 4.2 Set Up Database Access

1. In Atlas dashboard, go to **Database Access**
2. Click **Add New Database User**
3. Create username and password (save these!)
4. Set privileges to **Read and write to any database**

#### 4.3 Configure Network Access

1. Go to **Network Access**
2. Click **Add IP Address**
3. Choose **Allow Access from Anywhere** (0.0.0.0/0)
   - For production, use specific IPs only

#### 4.4 Get Connection String

1. Click **Connect** on your cluster
2. Choose **Connect your application**
3. Copy the connection string
4. Replace `<password>` with your database user password

#### 4.5 Update app.py

Open `app.py` and update the connection string (around line 21):

```python
atlas_connection_string = "mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority"
```

### 5. Import Data to MongoDB

You need to import your EuroLeague data into MongoDB. You have two options:

#### Option A: Using MongoDB Compass (GUI)

1. Download [MongoDB Compass](https://www.mongodb.com/products/compass)
2. Connect using your Atlas connection string
3. Create database named `Eurostat`
4. Create four collections: `players`, `teams`, `games`, `boxscores`
5. Import your JSON data files into each collection

#### Option B: Using mongoimport (Command Line)

```bash
# Replace with your connection string
CONNECTION_STRING="mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/"

# Import players
mongoimport --uri="${CONNECTION_STRING}Eurostat" --collection=players --file=players.json --jsonArray

# Import teams
mongoimport --uri="${CONNECTION_STRING}Eurostat" --collection=teams --file=teams.json --jsonArray

# Import games
mongoimport --uri="${CONNECTION_STRING}Eurostat" --collection=games --file=games.json --jsonArray

# Import boxscores
mongoimport --uri="${CONNECTION_STRING}Eurostat" --collection=boxscores --file=boxscores.json --jsonArray
```

### 6. Initialize SQLite Database

The SQLite database will be automatically created when you first run the application. Sample users will also be initialized automatically.

### 7. Configure Flask Secret Key (Important for Production)

In `app.py`, change the secret key (line 9):

```python
app.config['SECRET_KEY'] = 'your-unique-secret-key-here-change-this-in-production'
```

Generate a secure key:
```python
import secrets
print(secrets.token_hex(32))
```

## 🚀 Running the Application

### 1. Start the Flask Backend

```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Pinged your deployment. You successfully connected to MongoDB Atlas!
 * Sample users initialized!
```

### 2. Open the Frontend

You have several options:

#### Option A: Using Live Server (VS Code)
1. Install "Live Server" extension in VS Code
2. Right-click `index.html`
3. Select "Open with Live Server"

#### Option B: Using Python HTTP Server
```bash
# In a new terminal, in the project directory
python -m http.server 8000
```
Then open: http://localhost:8000

#### Option C: Direct File Access
Simply open `index.html` in your browser (may have CORS issues)

### 3. Test the Application

1. Navigate to the frontend URL
2. You should see the login page
3. Try logging in with demo credentials:
   - Username: `admin`
   - Password: `admin123`

## 🔍 Troubleshooting

### MongoDB Connection Issues

**Error:** `ServerSelectionTimeoutError`
- **Solution**: Check your internet connection and MongoDB Atlas network access settings
- Ensure IP address 0.0.0.0/0 is whitelisted

**Error:** `Authentication failed`
- **Solution**: Verify username and password in connection string
- Ensure database user has correct privileges

### CORS Errors

**Error:** `Access-Control-Allow-Origin`
- **Solution**: Update CORS origins in `app.py` (line 8):
```python
CORS(app, supports_credentials=True, origins=['http://127.0.0.1:8000', 'http://localhost:8000'])
```
Add your frontend URL if different

### Port Already in Use

**Error:** `Address already in use`
- **Solution**: Kill the process using port 5000:

**On Windows:**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**On macOS/Linux:**
```bash
lsof -ti:5000 | xargs kill -9
```

Or change the port in `app.py`:
```python
app.run(debug=True, port=5001)
```

### SQLite Database Issues

**Error:** `no such table: user`
- **Solution**: Delete `users.db` file and restart Flask (it will recreate)

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'flask'`
- **Solution**: Ensure virtual environment is activated and dependencies are installed:
```bash
pip install -r requirements.txt
```

## 🔐 Security Configuration for Production

If deploying to production, ensure you:

1. **Change SECRET_KEY** to a strong random value
2. **Use environment variables** for sensitive data:
```python
import os
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
```

3. **Restrict CORS origins** to your domain only
4. **Use HTTPS** for all connections
5. **Restrict MongoDB network access** to specific IPs
6. **Set Flask debug mode to False**:
```python
app.run(debug=False)
```

## 📦 Dependency Versions

The application has been tested with:
- Flask 2.3.x
- Flask-SQLAlchemy 3.0.x
- PyMongo 4.5.x
- Python 3.8, 3.9, 3.10, 3.11

## 🆘 Getting Help

If you encounter issues not covered here:

1. Check the [GitHub Issues](link-to-issues)
2. Review Flask documentation: https://flask.palletsprojects.com/
3. Review MongoDB documentation: https://docs.mongodb.com/
4. Contact support: yk8290@g.rit.edu

## ✅ Verification Checklist

Before considering installation complete, verify:

- [ ] Flask server starts without errors
- [ ] MongoDB connection successful (check console for "Pinged your deployment")
- [ ] SQLite database created (`users.db` exists)
- [ ] Sample users initialized (check console)
- [ ] Frontend loads in browser
- [ ] Can log in with demo credentials
- [ ] Search functionality works
- [ ] Can view player/team details
- [ ] Favorites can be added/removed (when logged in)
- [ ] Admin can edit data (when logged in as admin)

## 🔄 Updating the Application

To update to the latest version:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

Then restart the Flask server.

---

**Next Steps:** After successful installation, see [USER_GUIDE.md](USER_GUIDE.md) for how to use the application.