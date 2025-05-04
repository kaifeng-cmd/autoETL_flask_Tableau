import requests
import logging
import os

# Create logs directory in project root
log_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "app.log")

# Setup logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

try:
    response = requests.get('http://localhost:5000/fetch-data')
    response.raise_for_status()
    logging.info(f"API call successful: {response.json()}")
except Exception as e:
    logging.error(f"Error calling API: {e}")