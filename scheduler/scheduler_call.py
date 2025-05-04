import requests
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_scheduled_fetch():
    try:
        response = requests.get('http://localhost:5000/fetch-data')
        response.raise_for_status()
        logging.info(f"Scheduled fetch completed: {response.json()}")
    except Exception as e:
        logging.error(f"Error during scheduled fetch: {e}")

if __name__ == '__main__':
    run_scheduled_fetch()