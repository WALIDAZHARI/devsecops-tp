import os
import sqlite3
from flask import Flask, jsonify, request, g
from prometheus_flask_exporter import PrometheusMetrics
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Database configuration
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'products.db')

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
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()

# Initialize the database when the app starts
init_db()

@app.route('/')
def home():
    return jsonify({
        "service": "Product Service",
        "status": "running",
        "database": DATABASE_PATH
    })

@app.route('/products', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'price' not in data:
            return jsonify({"error": "Name and price are required"}), 400
            
        name = data['name'].strip()
        try:
            price = float(data['price'])
            if price < 0:
                return jsonify({"error": "Price cannot be negative"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid price format"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, price) VALUES (?, ?)",
            (name, price)
        )
        product_id = cursor.lastrowid
        conn.commit()
        
        return jsonify({
            "id": product_id,
            "name": name,
            "price": price,
            "message": "Product created successfully"
        }), 201
        
    except sqlite3.Error as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        conn = get_db_connection()
        product = conn.execute(
            "SELECT id, name, price, created_at FROM products WHERE id = ?",
            (product_id,)
        ).fetchone()
        
        if not product:
            return jsonify({"error": "Product not found"}), 404
            
        return jsonify(dict(product))
        
    except sqlite3.Error as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/products', methods=['GET'])
def get_all_products():
    try:
        conn = get_db_connection()
        products = conn.execute(
            "SELECT id, name, price, created_at FROM products ORDER BY created_at DESC"
        ).fetchall()
        
        return jsonify([dict(product) for product in products])
        
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
    app.run(host='0.0.0.0', port=5556, debug=os.environ.get('FLASK_ENV') == 'development')