import os
import sqlite3
from flask import Flask, jsonify, request, g
from prometheus_flask_exporter import PrometheusMetrics
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Database configuration
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'users.db')

def get_db_connection():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Initialize database
def init_db():
    with app.app_context():
        db = get_db_connection()
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()

# Initialize the database when the app starts
init_db()

@app.route('/')
def home():
    return jsonify({
        "service": "User Service",
        "status": "running",
        "database": DATABASE_PATH
    })

@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({"error": "Name is required"}), 400
            
        name = data['name'].strip()
        if not name:
            return jsonify({"error": "Name cannot be empty"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name) VALUES (?)",
            (name,)
        )
        user_id = cursor.lastrowid
        conn.commit()
        
        return jsonify({
            "id": user_id,
            "name": name,
            "message": "User created successfully"
        }), 201
        
    except sqlite3.Error as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        conn = get_db_connection()
        user = conn.execute(
            "SELECT id, name, created_at FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        return jsonify(dict(user))
        
    except sqlite3.Error as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/users', methods=['GET'])
def get_all_users():
    try:
        conn = get_db_connection()
        users = conn.execute(
            "SELECT id, name, created_at FROM users ORDER BY created_at DESC"
        ).fetchall()
        
        return jsonify([dict(user) for user in users])
        
    except sqlite3.Error as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({"error": e.name, "message": e.description}), e.code

if __name__ == "__main__":
    # This will only run if the script is executed directly
    # In production, use a production WSGI server like Gunicorn
    app.run(host='0.0.0.0', port=5555, debug=os.environ.get('FLASK_ENV') == 'development')