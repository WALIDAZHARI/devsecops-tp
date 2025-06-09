from flask import Flask, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

products = []

@app.route('/')
def home():
    return jsonify({"message": "Hello from Product Service!"})

@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')

    if not name or price is None:
        return jsonify({"error": "Missing name or price"}), 400

    product = {"id": len(products) + 1, "name": name, "price": price}
    products.append(product)
    return jsonify(product), 201

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = next((p for p in products if p["id"] == product_id), None)
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

@app.route('/products', methods=['GET'])
def get_all_products():
    return jsonify(products)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5556)