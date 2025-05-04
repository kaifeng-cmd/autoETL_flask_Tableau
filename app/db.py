from sqlalchemy import create_engine
from mysql.connector import Error
import mysql.connector
import logging
from dotenv import load_dotenv
import os

def init_db(app):
    try:
        connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            port=app.config['MYSQL_PORT'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD']
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {app.config['MYSQL_DATABASE']}")
        logging.info(f"Database '{app.config['MYSQL_DATABASE']}' is ready.")
        cursor.close()
        connection.close()
    except Error as e:
        logging.error(f"Error creating database: {e}")
        raise

def get_engine():
    from urllib.parse import quote_plus
    load_dotenv()
    connection_string = (
        f"mysql+mysqlconnector://"
        f"{os.getenv('MYSQL_USER')}:{quote_plus(os.getenv('MYSQL_PASSWORD'))}@"
        f"{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}"
    )
    return create_engine(connection_string)