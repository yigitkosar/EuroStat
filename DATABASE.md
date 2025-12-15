# Database Documentation - EuroLeague Stats Explorer

This document describes the database architecture, schema, and relationships used in the EuroLeague Stats Explorer application.

## 🗄️ Database Architecture

The application uses a **dual-database architecture**:

1. **SQLite**: Local relational database for user management and interactions
2. **MongoDB Atlas**: Cloud NoSQL database for basketball statistics

### Why Dual Databases?

- **SQLite**: Perfect for structured user data with foreign key relationships
- **MongoDB**: Ideal for complex, nested basketball statistics with flexible schema

---

## 📊 SQLite Database (`users.db`)

### Overview
- **Type**: Relational database (SQL)
- **Location**: Local file (`users.db`)
- **ORM**: SQLAlchemy
- **Purpose**: User accounts, authentication, ratings, and favorites

### Schema Diagram

```
┌─────────────┐
│    user     │
├─────────────┤
│ id (PK)     │◄──┐
│ username    │   │
│ password    │   │
│ is_admin    │   │
└─────────────┘   │
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────┴─────┐    ┌────────┴─────┐
│   rating    │    │   favorite   │
├─────────────┤    ├──────────────┤
│ id (PK)     │    │ id (PK)      │
│ user_id(FK) │    │ user_id (FK) │
│ target_id   │    │ target_id    │
│ target_type │    │ target_type  │
│ score       │    │ added_at     │
└─────────────┘    └──────────────┘
```

### Table: `user`

Stores user account information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique user identifier |
| username | VARCHAR(80) | UNIQUE, NOT NULL | User login name |
| password | VARCHAR(120) | NOT NULL | Hashed password (scrypt algorithm) |
| is_admin | BOOLEAN | DEFAULT FALSE | Admin privileges flag |

**Indexes:**
- Primary key on `id`
- Unique index on `username`

**Sample Data:**
```json
{
  "id": 1,
  "username": "admin",
  "password": "scrypt:32768:8:1$oDJu...",
  "is_admin": 1
}
```

**Password Hashing:**
- Algorithm: scrypt
- Parameters: N=32768, r=8, p=1
- Salt: Randomly generated per password

---

### Table: `rating`

Stores user ratings for players and teams.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique rating identifier |
| user_id | INTEGER | FOREIGN KEY → user.id | User who submitted rating |
| target_id | VARCHAR(50) | NOT NULL | Player ID (e.g., "P003527") or Team ID (e.g., "BAR") |
| target_type | VARCHAR(20) | NOT NULL | Type: "player" or "team" |
| score | INTEGER | NOT NULL | Rating score (typically 1-5) |

**Foreign Keys:**
- `user_id` → `user.id` (ON DELETE CASCADE)

**Indexes:**
- Primary key on `id`
- Index on `target_id` for quick lookups

**Sample Data:**
```json
{
  "id": 1,
  "user_id": 2,
  "target_id": "P003527",
  "target_type": "player",
  "score": 5
}
```

**Usage:**
- Calculate average ratings per player/team
- Track user rating history
- Generate personalized recommendations

---

### Table: `favorite`

Stores user favorites for players and teams.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique favorite identifier |
| user_id | INTEGER | FOREIGN KEY → user.id, NOT NULL | User who favorited |
| target_id | VARCHAR(50) | NOT NULL | Player ID or Team ID |
| target_type | VARCHAR(20) | NOT NULL | Type: "player" or "team" |
| added_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | When favorite was added |

**Foreign Keys:**
- `user_id` → `user.id` (ON DELETE CASCADE)

**Indexes:**
- Primary key on `id`
- Composite index on `(user_id, target_id, target_type)` for uniqueness

**Sample Data:**
```json
{
  "id": 1,
  "user_id": 1,
  "target_id": "BAS",
  "target_type": "team",
  "added_at": "2025-12-09 21:35:10.578339"
}
```

**Constraints:**
- One user can only favorite the same player/team once
- Enforced at application level (not database constraint)

---

## 🍃 MongoDB Database (`Eurostat`)

### Overview
- **Type**: NoSQL document database
- **Location**: MongoDB Atlas (Cloud)
- **Driver**: PyMongo
- **Purpose**: Basketball statistics and game data

### Collections Overview

| Collection | Documents | Purpose |
|-----------|-----------|---------|
| players | ~400 | Player season statistics |
| teams | 18 | Team season statistics |
| games | 306 | Game schedules and results |
| boxscores | ~5,000 | Individual player game performances |

---

### Collection: `players`

Stores player season statistics for EuroLeague 2023.

**Document Structure:**
```javascript
{
  _id: ObjectId("693849ec19d1dea64511d259"),
  season_player_id: "E2023_P003527_VIR",
  season_code: "E2023",
  player_id: "P003527",
  player: "ABASS, AWUDU",
  team_id: "VIR",
  
  // Games played
  games_played: 31,
  games_started: 2,
  minutes: 398.6,
  
  // Scoring
  points: 136,
  points_per_game: 4.39,
  two_points_made: 25,
  two_points_attempted: 43,
  two_points_percentage: 0.581,
  three_points_made: 25,
  three_points_attempted: 79,
  three_points_percentage: 0.316,
  free_throws_made: 11,
  free_throws_attempted: 13,
  free_throws_percentage: 0.846,
  
  // Rebounds
  offensive_rebounds: 18,
  defensive_rebounds: 34,
  total_rebounds: 52,
  total_rebounds_per_game: 1.68,
  
  // Other stats
  assists: 13,
  assists_per_game: 0.42,
  steals: 12,
  steals_per_game: 0.39,
  turnovers: 6,
  turnovers_per_game: 0.19,
  blocks_favour: 3,
  blocks_against: 4,
  fouls_committed: 33,
  fouls_received: 11,
  
  // Advanced metrics
  plus_minus: -74,
  plus_minus_per_game: -2.39,
  valuation_per_game: 3.55
}
```

**Key Fields:**
- `player_id`: Unique identifier (e.g., "P003527")
- `season_player_id`: Unique for season + player + team
- `team_id`: Current team identifier
- All percentages stored as decimals (0.581 = 58.1%)
- Per-game stats are pre-calculated

**Indexes:**
- `_id` (default)
- `player_id` (recommended)
- `team_id` (recommended)
- `points_per_game` (for sorting)

---

### Collection: `teams`

Stores team season statistics for EuroLeague 2023.

**Document Structure:**
```javascript
{
  _id: ObjectId("69384ba519d1dea64511ec1d"),
  season_team_id: "E2023_BAR",
  season_code: "E2023",
  team_id: "BAR",
  team_name: "FC Barcelona",
  
  // Games
  games_played: 39,
  minutes: 1565,
  
  // Scoring
  points: 3163,
  points_per_game: 81.1,
  two_points_made: 856,
  two_points_attempted: 1568,
  two_points_percentage: 0.546,
  three_points_made: 328,
  three_points_attempted: 912,
  three_points_percentage: 0.36,
  free_throws_made: 467,
  free_throws_attempted: 643,
  free_throws_percentage: 0.726,
  
  // Rebounds
  offensive_rebounds: 449,
  defensive_rebounds: 948,
  total_rebounds: 1397,
  offensive_rebounds_per_game: 11.51,
  defensive_rebounds_per_game: 24.31,
  total_rebounds_per_game: 35.82,
  
  // Other stats
  assists: 754,
  assists_per_game: 19.33,
  steals: 249,
  steals_per_game: 6.38,
  turnovers: 497,
  turnovers_per_game: 12.74,
  blocks_favour: 89,
  blocks_against: 75,
  fouls_committed: 774,
  fouls_received: 739,
  
  // Advanced metrics
  valuation: 3573,
  valuation_per_game: 91.62,
  minutes_per_game: 40.13
}
```

**Key Fields:**
- `team_id`: Short identifier (e.g., "BAR", "MAD")
- `team_name`: Full team name
- `season_team_id`: Unique for season + team

**Indexes:**
- `_id` (default)
- `team_id` (recommended, unique)
- `points_per_game` (for sorting)

---

### Collection: `games`

Stores game schedules, results, and metadata.

**Document Structure:**
```javascript
{
  _id: ObjectId("69384ce319d1dea64511fbe0"),
  game_id: "E2023_002",
  game: "BAR-IST",
  
  // Date/Time
  date: ISODate("2023-10-05T00:00:00.000Z"),
  time: "20:30:00",
  
  // Competition info
  round: 1,
  phase: "REGULAR SEASON", // or "PLAYOFFS"
  season_code: "E2023",
  
  // Teams
  team_a: "FC BARCELONA",
  team_b: "ANADOLU EFES ISTANBUL",
  team_id_a: "BAR",
  team_id_b: "IST",
  coach_a: "GRIMAU, ROGER",
  coach_b: "CAN, ERDEM",
  
  // Scores
  score_a: 91,
  score_b: 74,
  score_quarter_1_a: 22,
  score_quarter_2_a: 40,
  score_quarter_3_a: 69,
  score_quarter_4_a: 91,
  score_quarter_1_b: 19,
  score_quarter_2_b: 34,
  score_quarter_3_b: 64,
  score_quarter_4_b: 74,
  
  // Venue
  stadium: "PALAU BLAUGRANA",
  capacity: 5577,
  
  // Officials
  referee_1: "RADOVIC, SRETEN",
  referee_2: "DIFALLAH, MEHDI",
  referee_3: "JOVCIC, MILIVOJE",
  
  // Game stats
  game_time: "40:00",
  remaining_partial_time: "00:00",
  fouls_a: 15,
  fouls_b: 15,
  timeouts_a: 2,
  timeouts_b: 4,
  w_id: 80
}
```

**Key Fields:**
- `game_id`: Unique identifier (e.g., "E2023_002")
- `team_id_a/b`: For querying team schedules
- `phase`: "REGULAR SEASON" or "PLAYOFFS"
- Quarter scores are cumulative (not per-quarter)

**Indexes:**
- `_id` (default)
- `game_id` (recommended, unique)
- `team_id_a` (for team schedule queries)
- `team_id_b` (for team schedule queries)
- `round` (for chronological sorting)

---

### Collection: `boxscores`

Stores individual player performance in each game.

**Document Structure:**
```javascript
{
  _id: ObjectId("69384f0b19d1dea645126d2a"),
  game_player_id: "E2023_316_P008962",
  game_id: "E2023_316",
  game: "MCO-ULK",
  round: 38,
  phase: "PLAYOFFS",
  season_code: "E2023",
  
  // Player info
  player_id: "P008962",
  player: "HAYES, NIGEL",
  team_id: "ULK",
  dorsal: 11,
  
  // Game participation
  is_starter: 1, // 1 = starter, 0 = bench
  is_playing: 1, // 1 = played, 0 = DNP
  minutes: "29:09",
  
  // Scoring
  points: 10,
  two_points_made: 3,
  two_points_attempted: 4,
  three_points_made: 0,
  three_points_attempted: 4,
  free_throws_made: 4,
  free_throws_attempted: 4,
  
  // Rebounds
  offensive_rebounds: 2,
  defensive_rebounds: 4,
  total_rebounds: 6,
  
  // Other stats
  assists: 1,
  steals: 2,
  turnovers: 1,
  blocks_favour: 0,
  blocks_against: 0,
  fouls_committed: 3,
  fouls_received: 6,
  
  // Advanced metrics
  valuation: 16,
  plus_minus: -5
}
```

**Key Fields:**
- `game_player_id`: Unique identifier for this performance
- `game_id`: Links to games collection
- `player_id`: Links to players collection
- `is_starter`: 1 for starters, 0 for bench players
- `minutes`: String format "MM:SS"
- `plus_minus`: Team score differential while player was on court

**Indexes:**
- `_id` (default)
- `game_id` (for game boxscore queries)
- `player_id` (for player match history)
- Composite: `(game_id, team_id)` (recommended)

---

## 🔗 Database Relationships

### Cross-Database Relationships

```
SQLite (users.db)              MongoDB (Eurostat)
┌──────────┐                   ┌──────────┐
│  user    │                   │  players │
│  id=1    │                   │ player_id│
└────┬─────┘                   └────┬─────┘
     │                              │
     │ user_id                      │
┌────▼─────┐                        │
│ favorite │                        │
│target_id ├────────────────────────┘
│  ="P123" │    (Reference only,
└──────────┘     no FK constraint)
```

**Key Points:**
- No formal foreign keys between SQLite and MongoDB
- Application-level referential integrity
- `target_id` in SQLite references `player_id` or `team_id` in MongoDB

### Within MongoDB

```
┌──────────┐         ┌───────────┐         ┌──────────┐
│  teams   │         │   games   │         │ boxscore │
│ team_id  │◄────────┤team_id_a/b│────────►│ game_id  │
└──────────┘         └─────┬─────┘         └────┬─────┘
                           │                     │
┌──────────┐               │                     │
│  players │               │                     │
│ team_id  │◄──────────────┘                     │
│player_id │◄────────────────────────────────────┘
└──────────┘
```

---

## 📈 Calculated Fields

Some fields are calculated on-the-fly by the application:

### Field Goal Percentage (FG%)
```python
fg_percentage = ((two_points_made + three_points_made) / 
                 (two_points_attempted + three_points_attempted)) * 100
```

### EuroStat Rating
```python
rating = (points + 
          0.4 * fg_made - 
          0.7 * fg_attempted - 
          0.4 * ft_missed + 
          0.7 * off_reb + 
          0.3 * def_reb + 
          steals + 
          0.7 * assists + 
          0.7 * blocks - 
          0.4 * fouls - 
          turnovers)
```

### Average User Rating
```sql
SELECT AVG(score) 
FROM rating 
WHERE target_id = 'P003527'
```

---

## 🔍 Common Queries

### SQLite Queries

**Get user's favorites:**
```sql
SELECT target_id, target_type 
FROM favorite 
WHERE user_id = 1
ORDER BY added_at DESC;
```

**Calculate average rating:**
```sql
SELECT target_id, AVG(score) as avg_rating
FROM rating
GROUP BY target_id
HAVING target_type = 'player';
```

### MongoDB Queries

**Find top scorers:**
```javascript
db.players.find({})
  .sort({ points_per_game: -1 })
  .limit(10)
```

**Get team roster:**
```javascript
db.players.find({ team_id: "BAR" })
  .sort({ points_per_game: -1 })
```

**Get player match history:**
```javascript
db.boxscores.find({ player_id: "P003527" })
  .sort({ round: 1 })
```

**Get team schedule:**
```javascript
db.games.find({
  $or: [
    { team_id_a: "BAR" },
    { team_id_b: "BAR" }
  ]
}).sort({ round: 1 })
```

**Search players by name:**
```javascript
db.players.find({
  player: { $regex: "JOHN", $options: "i" }
}).limit(10)
```

---

## 🔒 Data Integrity

### SQLite
- **Foreign keys enabled**: ON DELETE CASCADE
- **Unique constraints**: username must be unique
- **Application-level validation**: target_id must exist in MongoDB

### MongoDB
- **Schema validation**: Not enforced (flexible schema)
- **Application-level validation**: Required fields checked before insert
- **Duplicate prevention**: Unique indexes recommended on key fields

---

## 💾 Backup and Maintenance

### SQLite Backup
```bash
# Simple file copy
cp users.db users_backup.db

# Using SQLite command
sqlite3 users.db ".backup users_backup.db"
```

### MongoDB Atlas Backup
- Automatic backups enabled in Atlas
- Point-in-time recovery available
- Manual backup via mongodump:
```bash
mongodump --uri="mongodb+srv://..." --db=Eurostat
```

---

## 📊 Database Statistics

### Storage Estimates

| Database | Size | Collections/Tables | Documents/Rows |
|----------|------|-------------------|----------------|
| SQLite | ~50 KB | 3 tables | ~10-100 rows |
| MongoDB | ~25 MB | 4 collections | ~5,700 documents |

### Index Sizes

MongoDB indexes add approximately 10-15% to database size.

---

## 🔧 Migration and Updates

### Adding New Fields

**SQLite:**
```sql
ALTER TABLE user ADD COLUMN email VARCHAR(120);
```

**MongoDB:**
```javascript
// No schema changes needed
// Just start using new fields
db.players.updateMany({}, {
  $set: { new_field: default_value }
})
```

### Data Cleanup

**Remove test users:**
```sql
DELETE FROM user WHERE username LIKE 'test_%';
```

**Remove old favorites:**
```sql
DELETE FROM favorite 
WHERE added_at < date('now', '-1 year');
```

---

## 📚 Additional Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

---

**Related Documentation:**
- [API Documentation](API_DOCS.md)
- [Installation Guide](INSTALLATION.md)
- [User Guide](USER_GUIDE.md)