from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this in production

# Decorator to require login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Initialize the database
def init_db():
    with sqlite3.connect('tournament.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS tournaments
                     (id INTEGER PRIMARY KEY, name TEXT, start_date TEXT, status TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS teams
                     (id INTEGER PRIMARY KEY, name TEXT, tournament_id INTEGER,
                      FOREIGN KEY (tournament_id) REFERENCES tournaments(id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS players
                     (id INTEGER PRIMARY KEY, name TEXT, team_id INTEGER,
                      FOREIGN KEY (team_id) REFERENCES teams(id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS matches
                     (id INTEGER PRIMARY KEY, tournament_id INTEGER, team1_id INTEGER, team2_id INTEGER,
                      team1_score INTEGER, team2_score INTEGER, match_date TEXT, status TEXT,
                      FOREIGN KEY (tournament_id) REFERENCES tournaments(id),
                      FOREIGN KEY (team1_id) REFERENCES teams(id),
                      FOREIGN KEY (team2_id) REFERENCES teams(id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL,
                      password TEXT NOT NULL, user_type TEXT NOT NULL)''')
        try:
            c.execute("INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)",
                     ('admin', generate_password_hash('admin123'), 'admin'))
            conn.commit()
        except sqlite3.IntegrityError:
            pass

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        with sqlite3.connect('tournament.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username = ? AND user_type = ?", (username, user_type))
            user = c.fetchone()
            if user and check_password_hash(user[2], password):
                session['user_id'] = user[0]
                session['user_type'] = user[3]
                session['username'] = user[1]
                flash('Login successful!')
                return redirect(url_for('index'))
            flash('Invalid username or password')
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Homepage
@app.route('/')
@login_required
def index():
    with sqlite3.connect('tournament.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM tournaments")
        tournaments = c.fetchall()
    return render_template('index.html', tournaments=tournaments)

# Create tournament
@app.route('/create_tournament', methods=['GET', 'POST'])
@login_required
def create_tournament():
    if session['user_type'] != 'admin':
        flash('Access denied. Admin only.')
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        start_date = request.form['start_date']
        with sqlite3.connect('tournament.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO tournaments (name, start_date, status) VALUES (?, ?, ?)",
                      (name, start_date, 'Pending'))
            conn.commit()
        return redirect(url_for('index'))
    return render_template('create_tournament.html')

# View tournament details
@app.route('/tournament/<int:tournament_id>')
@login_required
def tournament_details(tournament_id):
    with sqlite3.connect('tournament.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM tournaments WHERE id = ?", (tournament_id,))
        tournament = c.fetchone()
        c.execute("SELECT * FROM teams WHERE tournament_id = ?", (tournament_id,))
        teams = c.fetchall()
        c.execute("""SELECT m.*, t1.name, t2.name FROM matches m
                     JOIN teams t1 ON m.team1_id = t1.id
                     JOIN teams t2 ON m.team2_id = t2.id
                     WHERE m.tournament_id = ?""", (tournament_id,))
        matches = c.fetchall()
        c.execute("""SELECT p.*, t.name FROM players p
                     JOIN teams t ON p.team_id = t.id
                     WHERE t.tournament_id = ?""", (tournament_id,))
        players = c.fetchall()
    return render_template('tournament_details.html', tournament=tournament, teams=teams,
                           matches=matches, players=players)

# Add team
@app.route('/add_team/<int:tournament_id>', methods=['GET', 'POST'])
@login_required
def add_team(tournament_id):
    if session['user_type'] != 'admin':
        flash('Access denied. Admin only.')
        return redirect(url_for('tournament_details', tournament_id=tournament_id))
    if request.method == 'POST':
        name = request.form['name']
        with sqlite3.connect('tournament.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO teams (name, tournament_id) VALUES (?, ?)", (name, tournament_id))
            conn.commit()
        return redirect(url_for('tournament_details', tournament_id=tournament_id))
    return render_template('add_team.html', tournament_id=tournament_id)

# Add player
@app.route('/add_player/<int:tournament_id>', methods=['GET', 'POST'])
@login_required
def add_player(tournament_id):
    if session['user_type'] != 'admin':
        flash('Access denied. Admin only.')
        return redirect(url_for('tournament_details', tournament_id=tournament_id))
    if request.method == 'POST':
        name = request.form['name']
        team_id = request.form['team_id']
        with sqlite3.connect('tournament.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO players (name, team_id) VALUES (?, ?)", (name, team_id))
            conn.commit()
        return redirect(url_for('tournament_details', tournament_id=tournament_id))
    with sqlite3.connect('tournament.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM teams WHERE tournament_id = ?", (tournament_id,))
        teams = c.fetchall()
    return render_template('add_player.html', tournament_id=tournament_id, teams=teams)

# Schedule match
@app.route('/schedule_match/<int:tournament_id>', methods=['GET', 'POST'])
@login_required
def schedule_match(tournament_id):
    if session['user_type'] != 'admin':
        flash('Access denied. Admin only.')
        return redirect(url_for('tournament_details', tournament_id=tournament_id))
    if request.method == 'POST':
        team1_id = request.form['team1_id']
        team2_id = request.form['team2_id']
        match_date = request.form['match_date']
        with sqlite3.connect('tournament.db') as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO matches (tournament_id, team1_id, team2_id, match_date, status)
                         VALUES (?, ?, ?, ?, ?)""", (tournament_id, team1_id, team2_id, match_date, 'Scheduled'))
            conn.commit()
        return redirect(url_for('tournament_details', tournament_id=tournament_id))
    with sqlite3.connect('tournament.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM teams WHERE tournament_id = ?", (tournament_id,))
        teams = c.fetchall()
    return render_template('schedule_match.html', tournament_id=tournament_id, teams=teams)

# Update match score
@app.route('/update_score/<int:match_id>', methods=['POST'])
@login_required
def update_score(match_id):
    if session['user_type'] != 'admin':
        flash('Access denied. Admin only.')
        return redirect(request.referrer)
    team1_score = request.form['team1_score']
    team2_score = request.form['team2_score']
    with sqlite3.connect('tournament.db') as conn:
        c = conn.cursor()
        c.execute("UPDATE matches SET team1_score = ?, team2_score = ?, status = 'Completed' WHERE id = ?",
                  (team1_score, team2_score, match_id))
        conn.commit()
    return redirect(request.referrer)

# API: Rankings
@app.route('/api/rankings/<int:tournament_id>')
@login_required
def get_rankings(tournament_id):
    with sqlite3.connect('tournament.db') as conn:
        c = conn.cursor()
        c.execute("""
            SELECT t.name, 
                   COUNT(CASE 
                       WHEN m.team1_score > m.team2_score AND m.team1_id = t.id THEN 1 
                       WHEN m.team2_score > m.team1_score AND m.team2_id = t.id THEN 1 
                   END) as wins 
            FROM teams t 
            LEFT JOIN matches m ON t.id IN (m.team1_id, m.team2_id) 
            WHERE t.tournament_id = ? 
            GROUP BY t.id 
            ORDER BY wins DESC""", (tournament_id,))
        rankings = c.fetchall()
    return jsonify(rankings)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
