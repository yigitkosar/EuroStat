import os
import certifi
from flask import Flask, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=['http://127.0.0.1:8000', 'http://localhost:8000', 'http://127.0.0.1:5500', 'http://localhost:5500', 'null'])
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production-12345'

# --- 1. DATABASE CONFIGURATION ---

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

ca = certifi.where()

atlas_connection_string = "mongodb+srv://ao3101_db_user:Password@cluster0.opz9odr.mongodb.net/?retryWrites=true&w=majority"

try:
    client = MongoClient(atlas_connection_string, tlsCAFile=ca)
    mongo_db = client['Eurostat'] 
    
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB Atlas!")
except Exception as e:
    print(f"Error connecting to Atlas: {e}")

players_col = mongo_db['players']
teams_col = mongo_db['teams']
games_col = mongo_db['games']
boxscores_col = mongo_db['boxscores']

# --- 2. SQLITE MODELS ---

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    target_id = db.Column(db.String(50), nullable=False) 
    target_type = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Integer, nullable=False)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    target_id = db.Column(db.String(50), nullable=False)
    target_type = db.Column(db.String(20), nullable=False)  # 'player' or 'team'
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

def init_sample_users():
    """Create 5 sample users and 1 admin if they don't exist"""
    sample_users = [
        {'username': 'admin', 'password': 'admin123', 'is_admin': True},
        {'username': 'john_doe', 'password': 'password1', 'is_admin': False},
        {'username': 'jane_smith', 'password': 'password2', 'is_admin': False},
        {'username': 'mike_jordan', 'password': 'password3', 'is_admin': False},
        {'username': 'sarah_lee', 'password': 'password4', 'is_admin': False},
        {'username': 'alex_brown', 'password': 'password5', 'is_admin': False},
    ]
    
    for user_data in sample_users:
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if not existing_user:
            hashed_pw = generate_password_hash(user_data['password'])
            new_user = User(
                username=user_data['username'],
                password=hashed_pw,
                is_admin=user_data['is_admin']
            )
            db.session.add(new_user)
    
    db.session.commit()
    print("  users initialized!")

with app.app_context():
    db.create_all()
    init_sample_users()

# --- 3. HELPER FUNCTIONS ---

def serialize_mongo(doc):
    if not doc: return None
    doc['_id'] = str(doc['_id'])
    return doc

def get_avg_rating(target_id):
    result = db.session.query(db.func.avg(Rating.score)).filter_by(target_id=target_id).scalar()
    return round(result, 1) if result else "N/A"

def calculate_eurostat_rating(stats):
    """
    Calculate EuroLeague rating using the formula:
    Rating = Points + 0.4(FG Made) - 0.7(FG Attempted) - 0.4(FT Missed) + 
             0.7(Off. Reb) + 0.3(Def. Reb) + Steals + 0.7(Assists) + 
             0.7(Blocks) - 0.4(Fouls) - Turnovers
    """
    points = stats.get('points', 0)
    
    # Field goals = 2PT + 3PT
    two_made = stats.get('two_points_made', 0)
    two_attempted = stats.get('two_points_attempted', 0)
    three_made = stats.get('three_points_made', 0)
    three_attempted = stats.get('three_points_attempted', 0)
    fg_made = two_made + three_made
    fg_attempted = two_attempted + three_attempted
    
    # Free throws
    ft_made = stats.get('free_throws_made', 0)
    ft_attempted = stats.get('free_throws_attempted', 0)
    ft_missed = ft_attempted - ft_made
    
    # Rebounds
    off_reb = stats.get('offensive_rebounds', 0)
    def_reb = stats.get('defensive_rebounds', 0)
    
    # Other stats
    steals = stats.get('steals', 0)
    assists = stats.get('assists', 0)
    blocks = stats.get('blocks_favour', 0)
    fouls = stats.get('fouls_committed', 0)
    turnovers = stats.get('turnovers', 0)
    
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
    
    return round(rating, 2)

def calculate_fg_percentage(stats):
    """Calculate field goal percentage from 2PT + 3PT"""
    two_made = stats.get('two_points_made', 0)
    two_attempted = stats.get('two_points_attempted', 0)
    three_made = stats.get('three_points_made', 0)
    three_attempted = stats.get('three_points_attempted', 0)
    
    fg_made = two_made + three_made
    fg_attempted = two_attempted + three_attempted
    
    if fg_attempted == 0:
        return 0.0
    return round((fg_made / fg_attempted) * 100, 1)

# --- 4. AUTHENTICATION ROUTES ---

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_admin'] = user.is_admin
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'is_admin': user.is_admin
            }
        })
    
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/current_user', methods=['GET'])
def current_user():
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'user': {
                'id': session['user_id'],
                'username': session['username'],
                'is_admin': session.get('is_admin', False)
            }
        })
    return jsonify({'logged_in': False})

# --- 5. FAVORITES ROUTES ---

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_favorites = Favorite.query.filter_by(user_id=session['user_id']).all()
    
    favorite_players = []
    favorite_teams = []
    
    for fav in user_favorites:
        if fav.target_type == 'player':
            player = players_col.find_one({'player_id': fav.target_id})
            if player:
                player_data = serialize_mongo(player)
                player_data['fg_percentage'] = calculate_fg_percentage(player)
                
                # Calculate EuroStat rating
                matches = list(boxscores_col.find({"player_id": fav.target_id}))
                if matches:
                    total_rating = sum(calculate_eurostat_rating(m) for m in matches)
                    player_data['eurostat_rating'] = round(total_rating / len(matches), 2)
                else:
                    player_data['eurostat_rating'] = 0
                
                favorite_players.append(player_data)
        
        elif fav.target_type == 'team':
            team = teams_col.find_one({'team_id': fav.target_id})
            if team:
                team_data = serialize_mongo(team)
                team_data['fg_percentage'] = calculate_fg_percentage(team)
                favorite_teams.append(team_data)
    
    return jsonify({
        'players': favorite_players,
        'teams': favorite_teams
    })

@app.route('/api/favorites/add', methods=['POST'])
def add_favorite():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json
    target_id = data.get('target_id')
    target_type = data.get('target_type')
    
    # Check if already favorited
    existing = Favorite.query.filter_by(
        user_id=session['user_id'],
        target_id=target_id,
        target_type=target_type
    ).first()
    
    if existing:
        return jsonify({'message': 'Already in favorites'}), 400
    
    new_fav = Favorite(
        user_id=session['user_id'],
        target_id=target_id,
        target_type=target_type
    )
    db.session.add(new_fav)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Added to favorites'})

@app.route('/api/favorites/remove', methods=['POST'])
def remove_favorite():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json
    target_id = data.get('target_id')
    target_type = data.get('target_type')
    
    favorite = Favorite.query.filter_by(
        user_id=session['user_id'],
        target_id=target_id,
        target_type=target_type
    ).first()
    
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Removed from favorites'})
    
    return jsonify({'error': 'Favorite not found'}), 404

@app.route('/api/favorites/check', methods=['GET'])
def check_favorite():
    if 'user_id' not in session:
        return jsonify({'is_favorite': False})
    
    target_id = request.args.get('target_id')
    target_type = request.args.get('target_type')
    
    favorite = Favorite.query.filter_by(
        user_id=session['user_id'],
        target_id=target_id,
        target_type=target_type
    ).first()
    
    return jsonify({'is_favorite': favorite is not None})

# --- 6. ADMIN ROUTES ---

@app.route('/api/admin/player/<player_id>', methods=['PUT'])
def admin_edit_player(player_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.json
    
    # Update MongoDB player document
    update_fields = {}
    allowed_fields = ['player', 'points_per_game', 'assists_per_game', 
                      'total_rebounds_per_game', 'steals_per_game']
    
    for field in allowed_fields:
        if field in data:
            update_fields[field] = data[field]
    
    if update_fields:
        result = players_col.update_one(
            {'player_id': player_id},
            {'$set': update_fields}
        )
        
        if result.modified_count > 0:
            return jsonify({'success': True, 'message': 'Player updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'No changes made'}), 400
    
    return jsonify({'error': 'No valid fields to update'}), 400

@app.route('/api/admin/team/<team_id>', methods=['PUT'])
def admin_edit_team(team_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.json
    
    # Update MongoDB team document
    update_fields = {}
    allowed_fields = ['team_name', 'points_per_game', 'assists_per_game', 
                      'total_rebounds_per_game', 'steals_per_game']
    
    for field in allowed_fields:
        if field in data:
            update_fields[field] = data[field]
    
    if update_fields:
        result = teams_col.update_one(
            {'team_id': team_id},
            {'$set': update_fields}
        )
        
        if result.modified_count > 0:
            return jsonify({'success': True, 'message': 'Team updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'No changes made'}), 400
    
    return jsonify({'error': 'No valid fields to update'}), 400

# --- 7. MAIN API ROUTES ---

@app.route('/api/home', methods=['GET'])
def home():
    top_players = list(players_col.find(
        {}, 
        {'player': 1, 'player_id': 1, 'team_id': 1, 'points_per_game': 1}
    ).sort('points_per_game', -1).limit(5))
    
    best_teams = list(teams_col.find(
        {}, 
        {'team_id': 1, 'points_per_game': 1}
    ).sort('points_per_game', -1).limit(5))
    
    return jsonify({
        'top_players': [serialize_mongo(p) for p in top_players],
        'best_teams': [serialize_mongo(t) for t in best_teams]
    })

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query: return jsonify({'players': [], 'teams': []})
    
    regex = {"$regex": query, "$options": "i"}
    
    found_players = list(players_col.find(
        {'player': regex}, 
        {'player': 1, 'player_id': 1, 'team_id': 1}
    ).limit(10))
    
    found_teams = list(teams_col.find(
        {'team_name': regex}, 
        {'team_name': 1}
    ).limit(10))
    
    return jsonify({
        'players': [serialize_mongo(p) for p in found_players],
        'teams': [serialize_mongo(t) for t in found_teams]
    })

@app.route('/api/player/<player_id>', methods=['GET'])
def player_page(player_id):
    player_stats = players_col.find_one({"player_id": player_id})
    if not player_stats: return jsonify({"error": "Player not found"}), 404
    
    team_id = player_stats.get('team_id')
    team_info = teams_col.find_one({"team_id": team_id}, {"team_id": 1})
    
    matches_played = list(boxscores_col.find(
        {"player_id": player_id}
    ).sort("round", 1))
    
    # Calculate additional stats for each match
    enhanced_matches = []
    for match in matches_played:
        match_data = {
            'game_id': match.get('game_id'),
            'game': match.get('game'),
            'round': match.get('round'),
            'points': match.get('points', 0),
            'assists': match.get('assists', 0),
            'rebounds': match.get('total_rebounds', 0),
            'steals': match.get('steals', 0),
            'minutes': match.get('minutes'),
            'plus_minus': match.get('plus_minus', 0),
        }
        
        # Calculate FG%
        match_data['fg_percentage'] = calculate_fg_percentage(match)
        
        # Calculate EuroStat Rating
        match_data['eurostat_rating'] = calculate_eurostat_rating(match)
        
        enhanced_matches.append(match_data)
    
    # Calculate season averages using per_game fields that already exist
    games_played = player_stats.get('games_played', 0)
    
    # Add the calculated stats to player_stats
    player_stats['assists_per_game'] = player_stats.get('assists_per_game', 0)
    player_stats['rebounds_per_game'] = player_stats.get('total_rebounds_per_game', 0)
    player_stats['steals_per_game'] = player_stats.get('steals_per_game', 0)
    
    # Calculate FG% from player season totals
    player_stats['fg_percentage'] = calculate_fg_percentage(player_stats)
    
    # Calculate season average EuroStat rating
    if games_played > 0:
        total_rating = sum(calculate_eurostat_rating(m) for m in matches_played)
        player_stats['eurostat_rating'] = round(total_rating / games_played, 2)
    else:
        player_stats['eurostat_rating'] = 0

    return jsonify({
        "player_details": serialize_mongo(player_stats),
        "team_link": serialize_mongo(team_info),
        "match_history": enhanced_matches,
        "user_rating": get_avg_rating(player_id)
    })

@app.route('/api/team/<team_id>', methods=['GET'])
def team_page(team_id):
    team_stats = teams_col.find_one({"team_id": team_id})
    if not team_stats: return jsonify({"error": "Team not found"}), 404
    
    # Add calculated team stats
    team_stats['fg_percentage'] = calculate_fg_percentage(team_stats)
    
    # Get full roster with all stats
    roster_players = list(players_col.find({"team_id": team_id}))
    
    # Calculate enhanced stats for each player
    enhanced_roster = []
    for player in roster_players:
        player_data = {
            'player': player.get('player'),
            'player_id': player.get('player_id'),
            'games_played': player.get('games_played', 0),
            'points_per_game': player.get('points_per_game', 0),
            'assists_per_game': player.get('assists_per_game', 0),
            'rebounds_per_game': player.get('total_rebounds_per_game', 0),
            'steals_per_game': player.get('steals_per_game', 0),
            'fg_percentage': calculate_fg_percentage(player)
        }
        
        # Calculate average EuroStat rating for this player
        matches = list(boxscores_col.find({"player_id": player.get('player_id')}))
        if matches:
            total_rating = sum(calculate_eurostat_rating(m) for m in matches)
            player_data['eurostat_rating'] = round(total_rating / len(matches), 2)
        else:
            player_data['eurostat_rating'] = 0
        
        enhanced_roster.append(player_data)
    
    # Sort by points per game
    enhanced_roster.sort(key=lambda x: x['points_per_game'], reverse=True)
    
    schedule = list(games_col.find({
        "$or": [{"team_id_a": team_id}, {"team_id_b": team_id}]
    }).sort("round", 1))
    
    return jsonify({
        "team_details": serialize_mongo(team_stats),
        "roster": enhanced_roster,
        "schedule": [serialize_mongo(g) for g in schedule],
        "user_rating": get_avg_rating(team_id)
    })

@app.route('/api/match/<game_id>', methods=['GET'])
def match_page(game_id):
    game_header = games_col.find_one({"game_id": game_id})
    if not game_header: return jsonify({"error": "Game not found"}), 404
    
    all_stats = list(boxscores_col.find({"game_id": game_id}))
    
    home_team_stats = []
    away_team_stats = []
    
    team_a_id = game_header.get('team_id_a')
    team_b_id = game_header.get('team_id_b')
    
    for stat in all_stats:
        enhanced_stat = serialize_mongo(stat)
        enhanced_stat['eurostat_rating'] = calculate_eurostat_rating(stat)
        enhanced_stat['fg_percentage'] = calculate_fg_percentage(stat)
        enhanced_stat['rebounds'] = stat.get('total_rebounds', 0)
        
        if stat.get('team_id') == team_a_id:
            home_team_stats.append(enhanced_stat)
        else:
            away_team_stats.append(enhanced_stat)

    return jsonify({
        "game_info": serialize_mongo(game_header),
        "home_team_boxscore": home_team_stats,
        "away_team_boxscore": away_team_stats
    })

@app.route('/api/rate', methods=['POST'])
def submit_rating():
    data = request.json
    try:
        new_rating = Rating(
            user_id=data['user_id'],
            target_id=data['target_id'],
            target_type=data['type'],
            score=data['score']
        )
        db.session.add(new_rating)
        db.session.commit()
        return jsonify({"message": "Rating saved successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':

    app.run(debug=True, port=5000)
