# API Documentation - EuroLeague Stats Explorer

Complete API reference for the EuroLeague Stats Explorer backend.

**Base URL:** `http://127.0.0.1:5000/api`

## 📑 Table of Contents

1. [Authentication](#authentication)
2. [Favorites](#favorites)
3. [Admin Operations](#admin-operations)
4. [Data Retrieval](#data-retrieval)
5. [Error Responses](#error-responses)

---

## 🔐 Authentication

All authentication endpoints use session-based authentication with cookies.

### POST `/api/login`

Authenticates a user and creates a session.

**Request:**
```http
POST /api/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "admin",
    "is_admin": true
  }
}
```

**Error Response (401):**
```json
{
  "success": false,
  "message": "Invalid credentials"
}
```

**Example:**
```javascript
const response = await fetch('http://127.0.0.1:5000/api/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
});
const data = await response.json();
```

---

### POST `/api/logout`

Clears the user session and logs out.

**Request:**
```http
POST /api/logout
```

**Success Response (200):**
```json
{
  "success": true
}
```

**Example:**
```javascript
await fetch('http://127.0.0.1:5000/api/logout', {
  method: 'POST',
  credentials: 'include'
});
```

---

### GET `/api/current_user`

Returns information about the currently logged-in user.

**Request:**
```http
GET /api/current_user
```

**Success Response (200) - Logged In:**
```json
{
  "logged_in": true,
  "user": {
    "id": 1,
    "username": "admin",
    "is_admin": true
  }
}
```

**Success Response (200) - Not Logged In:**
```json
{
  "logged_in": false
}
```

---

## ❤️ Favorites

All favorites endpoints require authentication.

### GET `/api/favorites`

Retrieves all favorites for the logged-in user with enhanced statistics.

**Authentication:** Required

**Request:**
```http
GET /api/favorites
```

**Success Response (200):**
```json
{
  "players": [
    {
      "_id": "693849ec19d1dea64511d259",
      "player_id": "P011948",
      "player": "DOE, JOHN",
      "team_id": "BAS",
      "games_played": 31,
      "points_per_game": 15.3,
      "assists_per_game": 4.2,
      "total_rebounds_per_game": 6.8,
      "steals_per_game": 1.5,
      "fg_percentage": 45.6,
      "eurostat_rating": 12.5
    }
  ],
  "teams": [
    {
      "_id": "69384ba519d1dea64511ec1d",
      "team_id": "BAS",
      "team_name": "SAMPLE TEAM",
      "games_played": 39,
      "points_per_game": 82.1,
      "assists_per_game": 20.3,
      "total_rebounds_per_game": 36.5,
      "steals_per_game": 7.2,
      "fg_percentage": 48.2
    }
  ]
}
```

**Error Response (401):**
```json
{
  "error": "Not logged in"
}
```

---

### POST `/api/favorites/add`

Adds a player or team to the user's favorites.

**Authentication:** Required

**Request:**
```http
POST /api/favorites/add
Content-Type: application/json

{
  "target_id": "P011948",
  "target_type": "player"
}
```

**Parameters:**
- `target_id` (string, required): Player ID or Team ID
- `target_type` (string, required): Either "player" or "team"

**Success Response (200):**
```json
{
  "success": true,
  "message": "Added to favorites"
}
```

**Error Response (400) - Already Favorited:**
```json
{
  "message": "Already in favorites"
}
```

**Error Response (401):**
```json
{
  "error": "Not logged in"
}
```

---

### POST `/api/favorites/remove`

Removes a player or team from the user's favorites.

**Authentication:** Required

**Request:**
```http
POST /api/favorites/remove
Content-Type: application/json

{
  "target_id": "P011948",
  "target_type": "player"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Removed from favorites"
}
```

**Error Response (404):**
```json
{
  "error": "Favorite not found"
}
```

---

### GET `/api/favorites/check`

Checks if a specific player or team is in the user's favorites.

**Authentication:** Optional (returns false if not logged in)

**Request:**
```http
GET /api/favorites/check?target_id=P011948&target_type=player
```

**Query Parameters:**
- `target_id` (string, required): Player ID or Team ID
- `target_type` (string, required): Either "player" or "team"

**Success Response (200):**
```json
{
  "is_favorite": true
}
```

---

## 👨‍💼 Admin Operations

All admin endpoints require authentication with admin privileges.

### PUT `/api/admin/player/<player_id>`

Updates player statistics and information.

**Authentication:** Required (Admin only)

**Request:**
```http
PUT /api/admin/player/P011948
Content-Type: application/json

{
  "player": "UPDATED NAME",
  "points_per_game": 20.5,
  "assists_per_game": 5.2,
  "total_rebounds_per_game": 8.1,
  "steals_per_game": 1.5
}
```

**Allowed Fields:**
- `player` (string): Player name
- `points_per_game` (float): Points per game
- `assists_per_game` (float): Assists per game
- `total_rebounds_per_game` (float): Rebounds per game
- `steals_per_game` (float): Steals per game

**Success Response (200):**
```json
{
  "success": true,
  "message": "Player updated successfully"
}
```

**Error Response (403):**
```json
{
  "error": "Admin access required"
}
```

**Error Response (400) - No Changes:**
```json
{
  "success": false,
  "message": "No changes made"
}
```

---

### PUT `/api/admin/team/<team_id>`

Updates team statistics and information.

**Authentication:** Required (Admin only)

**Request:**
```http
PUT /api/admin/team/BAS
Content-Type: application/json

{
  "team_name": "UPDATED TEAM NAME",
  "points_per_game": 85.2,
  "assists_per_game": 22.1,
  "total_rebounds_per_game": 38.5,
  "steals_per_game": 7.8
}
```

**Allowed Fields:**
- `team_name` (string): Team name
- `points_per_game` (float): Points per game
- `assists_per_game` (float): Assists per game
- `total_rebounds_per_game` (float): Rebounds per game
- `steals_per_game` (float): Steals per game

**Success Response (200):**
```json
{
  "success": true,
  "message": "Team updated successfully"
}
```

**Error Response (403):**
```json
{
  "error": "Admin access required"
}
```

---

## 📊 Data Retrieval

Public endpoints for retrieving basketball statistics.

### GET `/api/home`

Returns dashboard data with top players and teams.

**Request:**
```http
GET /api/home
```

**Success Response (200):**
```json
{
  "top_players": [
    {
      "_id": "693849ec19d1dea64511d259",
      "player": "SMITH, JOHN",
      "player_id": "P003527",
      "team_id": "VIR",
      "points_per_game": 18.5
    }
  ],
  "best_teams": [
    {
      "_id": "69384ba519d1dea64511ec1d",
      "team_id": "BAR",
      "points_per_game": 81.1
    }
  ]
}
```

**Notes:**
- Returns top 5 players by points per game
- Returns top 5 teams by points per game

---

### GET `/api/search`

Searches for players and teams by name.

**Request:**
```http
GET /api/search?q=john
```

**Query Parameters:**
- `q` (string, required): Search query (case-insensitive)

**Success Response (200):**
```json
{
  "players": [
    {
      "_id": "693849ec19d1dea64511d259",
      "player": "SMITH, JOHN",
      "player_id": "P003527",
      "team_id": "VIR"
    }
  ],
  "teams": [
    {
      "_id": "69384ba519d1dea64511ec1d",
      "team_name": "JOHN'S TEAM",
      "team_id": "JOH"
    }
  ]
}
```

**Notes:**
- Empty query returns empty arrays
- Returns up to 10 players and 10 teams
- Uses regex for case-insensitive matching

---

### GET `/api/player/<player_id>`

Returns detailed player statistics, team information, and match history.

**Request:**
```http
GET /api/player/P003527
```

**Success Response (200):**
```json
{
  "player_details": {
    "_id": "693849ec19d1dea64511d259",
    "player_id": "P003527",
    "player": "SMITH, JOHN",
    "season_code": "E2023",
    "team_id": "VIR",
    "games_played": 31,
    "games_started": 2,
    "minutes": 398.6,
    "points": 136,
    "points_per_game": 4.39,
    "assists": 13,
    "assists_per_game": 0.42,
    "rebounds_per_game": 1.68,
    "steals_per_game": 0.39,
    "two_points_percentage": 0.581,
    "three_points_percentage": 0.316,
    "free_throws_percentage": 0.846,
    "fg_percentage": 45.6,
    "eurostat_rating": 12.5,
    "plus_minus": -74,
    "plus_minus_per_game": -2.39
  },
  "team_link": {
    "_id": "69384ba519d1dea64511ec1c",
    "team_id": "VIR"
  },
  "match_history": [
    {
      "game_id": "E2023_316",
      "game": "MCO-ULK",
      "round": 38,
      "points": 10,
      "assists": 1,
      "rebounds": 6,
      "steals": 2,
      "minutes": "29:09",
      "plus_minus": -5,
      "fg_percentage": 50.0,
      "eurostat_rating": 8.3
    }
  ],
  "user_rating": 4.5
}
```

**Error Response (404):**
```json
{
  "error": "Player not found"
}
```

**Notes:**
- `fg_percentage`: Calculated from 2PT + 3PT makes/attempts
- `eurostat_rating`: Official EuroLeague performance metric
- `match_history`: Sorted by round (ascending)
- `user_rating`: Average user rating or "N/A"

---

### GET `/api/team/<team_id>`

Returns detailed team statistics, roster, and schedule.

**Request:**
```http
GET /api/team/BAR
```

**Success Response (200):**
```json
{
  "team_details": {
    "_id": "69384ba519d1dea64511ec1d",
    "season_team_id": "E2023_BAR",
    "season_code": "E2023",
    "team_id": "BAR",
    "team_name": "FC BARCELONA",
    "games_played": 39,
    "minutes": 1565,
    "points": 3163,
    "points_per_game": 81.1,
    "assists_per_game": 19.33,
    "total_rebounds_per_game": 35.82,
    "steals_per_game": 6.38,
    "two_points_percentage": 0.546,
    "three_points_percentage": 0.36,
    "free_throws_percentage": 0.726,
    "fg_percentage": 54.6,
    "valuation": 3573,
    "valuation_per_game": 91.62
  },
  "roster": [
    {
      "player": "DOE, JOHN",
      "player_id": "P003527",
      "games_played": 31,
      "points_per_game": 12.5,
      "assists_per_game": 3.2,
      "rebounds_per_game": 5.1,
      "steals_per_game": 1.2,
      "fg_percentage": 48.5,
      "eurostat_rating": 11.3
    }
  ],
  "schedule": [
    {
      "_id": "69384ce319d1dea64511fbe0",
      "game_id": "E2023_002",
      "game": "BAR-IST",
      "date": "2023-10-05T00:00:00.000Z",
      "time": "20:30:00",
      "round": 1,
      "phase": "REGULAR SEASON",
      "season_code": "E2023",
      "score_a": 91,
      "score_b": 74,
      "team_a": "FC BARCELONA",
      "team_b": "ANADOLU EFES ISTANBUL",
      "team_id_a": "BAR",
      "team_id_b": "IST"
    }
  ],
  "user_rating": 4.8
}
```

**Error Response (404):**
```json
{
  "error": "Team not found"
}
```

**Notes:**
- `roster`: Sorted by points per game (descending)
- `schedule`: All games where team is either home or away
- `fg_percentage`: Calculated from season totals

---

### GET `/api/match/<game_id>`

Returns detailed match information with boxscores for both teams.

**Request:**
```http
GET /api/match/E2023_002
```

**Success Response (200):**
```json
{
  "game_info": {
    "_id": "69384ce319d1dea64511fbe0",
    "game_id": "E2023_002",
    "game": "BAR-IST",
    "date": "2023-10-05T00:00:00.000Z",
    "time": "20:30:00",
    "round": 1,
    "phase": "REGULAR SEASON",
    "season_code": "E2023",
    "score_a": 91,
    "score_b": 74,
    "team_a": "FC BARCELONA",
    "team_b": "ANADOLU EFES ISTANBUL",
    "team_id_a": "BAR",
    "team_id_b": "IST",
    "coach_a": "GRIMAU, ROGER",
    "coach_b": "CAN, ERDEM",
    "game_time": "40:00",
    "stadium": "PALAU BLAUGRANA",
    "capacity": 5577,
    "referee_1": "RADOVIC, SRETEN",
    "referee_2": "DIFALLAH, MEHDI",
    "referee_3": "JOVCIC, MILIVOJE",
    "score_quarter_1_a": 22,
    "score_quarter_2_a": 40,
    "score_quarter_3_a": 69,
    "score_quarter_4_a": 91,
    "score_quarter_1_b": 19,
    "score_quarter_2_b": 34,
    "score_quarter_3_b": 64,
    "score_quarter_4_b": 74
  },
  "home_team_boxscore": [
    {
      "_id": "69384f0b19d1dea645126d2a",
      "game_player_id": "E2023_316_P008962",
      "game_id": "E2023_316",
      "player_id": "P008962",
      "player": "HAYES, NIGEL",
      "team_id": "ULK",
      "dorsal": 11,
      "is_starter": 1,
      "is_playing": 1,
      "minutes": "29:09",
      "points": 10,
      "assists": 1,
      "rebounds": 6,
      "steals": 2,
      "two_points_made": 3,
      "two_points_attempted": 4,
      "three_points_made": 0,
      "three_points_attempted": 4,
      "free_throws_made": 4,
      "free_throws_attempted": 4,
      "offensive_rebounds": 2,
      "defensive_rebounds": 4,
      "total_rebounds": 6,
      "turnovers": 1,
      "blocks_favour": 0,
      "blocks_against": 0,
      "fouls_committed": 3,
      "fouls_received": 6,
      "valuation": 16,
      "plus_minus": -5,
      "fg_percentage": 37.5,
      "eurostat_rating": 8.3
    }
  ],
  "away_team_boxscore": [
    {
      "_id": "69384f0719d1dea645124691",
      "game_player_id": "E2023_240_P010588",
      "game_id": "E2023_240",
      "player_id": "P010588",
      "player": "BROWN, JOHN",
      "team_id": "MCO",
      "dorsal": 10,
      "is_starter": 1,
      "minutes": "24:06",
      "points": 3,
      "assists": 1,
      "rebounds": 3,
      "steals": 1,
      "fg_percentage": 33.3,
      "eurostat_rating": 2.0,
      "plus_minus": 4
    }
  ]
}
```

**Error Response (404):**
```json
{
  "error": "Game not found"
}
```

**Notes:**
- Boxscores include calculated `fg_percentage` and `eurostat_rating`
- Players sorted by is_starter (starters first) then by minutes played
- `is_starter`: 1 = starter, 0 = bench

---

### POST `/api/rate`

Submits a user rating for a player or team.

**Request:**
```http
POST /api/rate
Content-Type: application/json

{
  "user_id": 1,
  "target_id": "P011948",
  "type": "player",
  "score": 5
}
```

**Parameters:**
- `user_id` (integer, required): User ID
- `target_id` (string, required): Player ID or Team ID
- `type` (string, required): "player" or "team"
- `score` (integer, required): Rating score (1-5)

**Success Response (200):**
```json
{
  "message": "Rating saved successfully!"
}
```

**Error Response (400):**
```json
{
  "error": "Error message details"
}
```

---

## ⚠️ Error Responses

### Common HTTP Status Codes

- **200 OK**: Request successful
- **400 Bad Request**: Invalid request parameters
- **401 Unauthorized**: Not logged in
- **403 Forbidden**: Insufficient permissions (admin required)
- **404 Not Found**: Resource not found

### Error Response Format

All errors follow this format:

```json
{
  "error": "Description of the error",
  "message": "Additional details (optional)"
}
```

---

## 🔄 Rate Limiting

Currently, there are no rate limits implemented. For production deployment, consider implementing rate limiting using Flask-Limiter.

---

## 📝 Notes

### Session Management
- Sessions are cookie-based
- Always include `credentials: 'include'` in fetch requests
- Sessions persist until logout or browser close

### CORS Configuration
Allowed origins (configurable in `app.py`):
- `http://127.0.0.1:8000`
- `http://localhost:8000`
- `http://127.0.0.1:5500`
- `http://localhost:5500`
- `null` (for file:// protocol)

### EuroStat Rating Formula
```
Rating = Points + 0.4×FG_Made - 0.7×FG_Attempted - 0.4×FT_Missed + 
         0.7×Off_Reb + 0.3×Def_Reb + Steals + 0.7×Assists + 
         0.7×Blocks - 0.4×Fouls - Turnovers
```

### Field Goal Percentage Calculation
```
FG% = (2PT_Made + 3PT_Made) / (2PT_Attempted + 3PT_Attempted) × 100
```

---

## 🧪 Testing the API

### Using cURL

```bash
# Login
curl -X POST http://127.0.0.1:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -c cookies.txt

# Get favorites (using saved cookies)
curl http://127.0.0.1:5000/api/favorites -b cookies.txt

# Search
curl "http://127.0.0.1:5000/api/search?q=john"
```

### Using JavaScript (Frontend)

```javascript
// Always include credentials for session management
const fetchOptions = {
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json'
  }
};

// Login
const login = await fetch('http://127.0.0.1:5000/api/login', {
  ...fetchOptions,
  method: 'POST',
  body: JSON.stringify({ username: 'admin', password: 'admin123' })
});

// Get data
const player = await fetch('http://127.0.0.1:5000/api/player/P003527', {
  credentials: 'include'
});
```

---

**For more information, see:**
- [Installation Guide](INSTALLATION.md)
- [Database Schema](DATABASE.md)
- [User Guide](USER_GUIDE.md)