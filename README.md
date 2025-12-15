# 🏀 EuroLeague Stats Explorer

A comprehensive web application for exploring EuroLeague basketball statistics with advanced analytics, user authentication, favorites management, and admin capabilities.

## 🌟 Features

### For All Users
- **Real-time Search**: Search for players and teams instantly
- **Detailed Statistics**: View comprehensive player and team statistics
- **Match Box Scores**: Access detailed game information and player performances
- **EuroStat Rating**: Advanced performance rating calculation
- **Responsive Design**: Works seamlessly on desktop and mobile devices

### For Registered Users
- **Favorites System**: Save and manage favorite players and teams
- **Personalized Dashboard**: Quick access to your favorite content
- **Session Management**: Secure login/logout functionality

### For Administrators
- **Data Management**: Edit player and team statistics
- **Content Moderation**: Update information in real-time
- **Admin Dashboard**: Special access to management features

## 🛠 Tech Stack

### Backend
- **Framework**: Flask 3.0.0
- **Database**: 
  - MongoDB Atlas (Player, Team, Game, Boxscore data)
  - SQLite (User authentication, Favorites, Ratings)
- **Authentication**: Flask Sessions with Werkzeug password hashing
- **API**: RESTful API with JSON responses

### Frontend
- **Pure HTML5/CSS3/JavaScript**: No framework dependencies
- **Responsive Design**: Mobile-first approach
- **Modern UI**: Gradient backgrounds, smooth animations

### Libraries & Tools
- Flask-SQLAlchemy 3.1.1
- Flask-CORS 4.0.0
- PyMongo 4.6.1
- Certifi 2023.11.17
- Werkzeug (for password hashing)

## 📋 Prerequisites

- Python 3.8 or higher
- MongoDB Atlas account (free tier available)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection (for MongoDB Atlas)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone [your-repository-url]
cd euroleague-stats-explorer
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install flask flask-sqlalchemy flask-cors pymongo certifi werkzeug
```

Or use requirements.txt:
```bash
pip install -r requirements.txt
```

### 4. Configure MongoDB Atlas
1. Create a free MongoDB Atlas account at https://www.mongodb.com/cloud/atlas
2. Create a new cluster
3. Set up database access (username/password)
4. Whitelist your IP address (or use 0.0.0.0/0 for development)
5. Get your connection string
6. Update `atlas_connection_string` in `app.py` with your credentials

### 5. Initialize the Application
```bash
python app.py
```

This will:
- Create the SQLite database (`users.db`)
- Initialize 6 sample users (1 admin + 5 regular users)
- Start the Flask server on http://127.0.0.1:5000

### 6. Open the Frontend
Open `index.html` in your browser, or serve it using:
```bash
# Python 3
python -m http.server 8000

# Then visit: http://127.0.0.1:8000
```

## 👥 Default Users

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **Privileges**: Can edit player and team data

### Regular User Accounts
| Username | Password |
|----------|----------|
| john_doe | password1 |
| jane_smith | password2 |
| mike_jordan | password3 |
| sarah_lee | password4 |
| alex_brown | password5 |

## 📊 Statistics Calculated

### EuroStat Rating Formula
```
Rating = Points + 0.4(FG Made) - 0.7(FG Attempted) - 0.4(FT Missed) + 
         0.7(Off. Reb) + 0.3(Def. Reb) + Steals + 0.7(Assists) + 
         0.7(Blocks) - 0.4(Fouls) - Turnovers
```

### Field Goal Percentage
```
FG% = ((2PT Made + 3PT Made) / (2PT Attempted + 3PT Attempted)) × 100
```

### Statistics Displayed
- **Points Per Game (PPG)**
- **Assists Per Game (APG)**
- **Rebounds Per Game (RPG)**
- **Steals Per Game (SPG)**
- **Field Goal Percentage (FG%)**
- **EuroStat Rating**
- **Plus/Minus (+/-)**
- **Games Played (GP)**

## 🗂 Project Structure
```
euroleague-stats-explorer/
│
├── app.py                 # Flask backend application
├── index.html             # Frontend interface
├── users.db              # SQLite database (auto-generated)
├── requirements.txt      # Python dependencies
├── README.md            # This file
│
├── docs/                # Documentation (recommended)
│   ├── API_DOCS.md
│   ├── DATABASE.md
│   ├── USER_GUIDE.md
│   └── DEVELOPER.md
│
└── venv/               # Virtual environment (not committed)
```

## 🔒 Security Features

- **Password Hashing**: All passwords stored with Werkzeug's security functions
- **Session Management**: Secure Flask sessions with secret key
- **CORS Protection**: Configured for specific origins
- **Admin Authorization**: Protected routes for administrative functions
- **SQL Injection Prevention**: SQLAlchemy ORM protection
- **NoSQL Injection Prevention**: PyMongo parameterized queries

## 🌐 API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `GET /api/current_user` - Check login status

### Data Retrieval
- `GET /api/home` - Get top players and teams
- `GET /api/search?q={query}` - Search players/teams
- `GET /api/player/{player_id}` - Get player details
- `GET /api/team/{team_id}` - Get team details
- `GET /api/match/{game_id}` - Get match details

### Favorites
- `GET /api/favorites` - Get user's favorites
- `POST /api/favorites/add` - Add to favorites
- `POST /api/favorites/remove` - Remove from favorites
- `GET /api/favorites/check` - Check if favorited

### Admin (Requires Admin Access)
- `PUT /api/admin/player/{player_id}` - Edit player
- `PUT /api/admin/team/{team_id}` - Edit team

## 🎨 Features in Detail

### Search Functionality
- Real-time search with 300ms debounce
- Searches both players and teams
- Case-insensitive matching
- Displays results in categorized dropdown

### Favorites System
- Add/remove players and teams to favorites
- Visual indicators (heart icons)
- Dedicated favorites page
- Persistent across sessions

### Admin Features
- Edit modal for updating statistics
- Real-time data updates
- Visual admin badge
- Protected routes

### Match Details
- Full box scores for both teams
- Player statistics with EuroStat rating
- Starter indicators (★)
- Team totals
- Color-coded plus/minus values

## 🔧 Configuration

### Change Secret Key (Important for Production!)
In `app.py`, update:
```python
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production-12345'
```

### Change MongoDB Connection
In `app.py`, update:
```python
atlas_connection_string = "your-mongodb-atlas-connection-string"
```

### Change CORS Origins
In `app.py`, update allowed origins:
```python
CORS(app, supports_credentials=True, origins=[
    'http://your-domain.com',
    'https://your-domain.com'
])
```

## 🐛 Troubleshooting

### "Error loading data" Message
- **Issue**: Flask server not running or MongoDB connection failed
- **Solution**: Check if Flask is running on port 5000 and MongoDB Atlas connection is valid

### "Not logged in" Error
- **Issue**: Session expired or cookies blocked
- **Solution**: Log in again, ensure browser allows cookies

### CORS Errors
- **Issue**: Frontend and backend on different ports/domains
- **Solution**: Update CORS origins in `app.py`

### MongoDB Connection Timeout
- **Issue**: IP not whitelisted or wrong credentials
- **Solution**: Check MongoDB Atlas network access settings

## 📈 Future Enhancements

- [ ] User registration system
- [ ] Password reset functionality
- [ ] Advanced statistics filtering
- [ ] Data visualization charts
- [ ] Export data to CSV/PDF
- [ ] Player comparison tool
- [ ] Team season history
- [ ] Mobile app version
- [ ] Real-time game updates
- [ ] Social sharing features

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

Yigit Kosar
Acar Ozbahceci


## 🙏 Acknowledgments

- EuroLeague for the inspiration
- MongoDB Atlas for database hosting
- Flask community for excellent documentation
- All contributors and users

## 📞 Support

For issues, questions, or suggestions:
- Contact: yk8290@g.rit.edu


---

**Note**: This is a development version. For production deployment, ensure you:
- Change the secret key
- Use environment variables for sensitive data
- Enable HTTPS
- Implement rate limiting
- Add proper error logging
- Set up monitoring