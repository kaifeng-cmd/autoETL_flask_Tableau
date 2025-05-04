from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class Config:
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
    FLASK_ENV = "development"
    FLASK_RUN_PORT = 5000