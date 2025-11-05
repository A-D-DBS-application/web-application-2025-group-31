from flask import Blueprint, jsonify

bp = Blueprint('api', __name__)

@bp.route('/api/data', methods=['GET'])
def get_data():
    # Sample data to return as JSON
    sample_data = {
        "message": "Welcome to the API!",
        "data": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
            {"id": 3, "name": "Item 3"}
        ]
    }
    return jsonify(sample_data)

def init_app(app):
    app.register_blueprint(bp)