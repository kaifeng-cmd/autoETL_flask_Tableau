from flask import Blueprint, jsonify
from .fetch_usgs import fetch_and_store_earthquake_data
import logging

bp = Blueprint('routes', __name__)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@bp.route('/fetch-data', methods=['GET'])
def fetch_data():
    try:
        new_records_count = fetch_and_store_earthquake_data()
        return jsonify({
            'status': 'success',
            'message': f'Fetched and stored {new_records_count} new earthquake records'
        }), 200
    except Exception as e:
        logging.error(f"Error in fetch_data: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500