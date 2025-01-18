from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    reorder_level = db.Column(db.Integer, nullable=False)

# Initialize Database
def initialize_database():
    with app.app_context():
        db.create_all()

# Route to serve the frontend
@app.route('/')
def home():
    return render_template('index.html')

# API to fetch inventory data
@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    inventory = Inventory.query.all()
    return jsonify([{
        "id": item.id,
        "product": item.product,
        "location": item.location,
        "stock": item.stock,
        "reorder_level": item.reorder_level
    } for item in inventory])

# API to update stock levels (replenishment)
@app.route('/api/replenish', methods=['POST'])
def replenish_stock():
    data = request.json
    product_id = data.get('id')
    quantity = data.get('quantity')

    if not product_id or not quantity:
        return jsonify({"error": "Invalid input data"}), 400

    item = Inventory.query.get(product_id)
    if item:
        item.stock += int(quantity)
        db.session.commit()
        return jsonify({"message": f"Stock for {item.product} replenished by {quantity} units."}), 200

    return jsonify({"error": "Product not found"}), 404

# API to add new products
@app.route('/api/add_product', methods=['POST'])
def add_product():
    data = request.json
    product = data.get('product')
    location = data.get('location')
    stock = data.get('stock')
    reorder_level = data.get('reorder_level')

    if not product or not location or stock is None or reorder_level is None:
        return jsonify({"error": "Invalid input data"}), 400

    new_item = Inventory(product=product, location=location, stock=stock, reorder_level=reorder_level)
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"message": "Product added successfully."}), 201

# API to provide inventory forecast data
@app.route('/api/forecast', methods=['GET'])
def forecast_inventory():
    forecast_data = {
        "labels": ["January", "February", "March", "April", "May"],
        "data": [120, 140, 160, 180, 200]
    }
    return jsonify(forecast_data)

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)
