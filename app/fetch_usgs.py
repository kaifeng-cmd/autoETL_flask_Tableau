import requests
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import text
import logging
from .db import get_engine
from dotenv import load_dotenv
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

# Load environment variables
load_dotenv()

def convert_time(ms):
    if ms:
        return datetime.utcfromtimestamp(ms / 1000).strftime('%Y-%m-%d %H:%M:%S')
    return None

def convert_malaysia_time(ms):
    if ms:
        return (datetime.utcfromtimestamp(ms / 1000) + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    return None

def get_location_info(lat, lon):
    try:
        api_key = os.getenv("BIGDATACLOUD_API_KEY")
        url = f"https://api.bigdatacloud.net/data/reverse-geocode?latitude={lat}&longitude={lon}&localityLanguage=en&key={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return (
                data.get("principalSubdivision") or "Unknown",
                data.get("countryName") or "Unknown",
                data.get("continent") or "Unknown",
                data.get("locality") or "Unknown"
            )
    except Exception as e:
        logging.error(f"Error in geocoding: {e}")
    return "Unknown", "Unknown", "Unknown", "Unknown"

def fetch_and_store_earthquake_data():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        logging.error(f"Error fetching earthquake data: {e}")
        raise

    records = []
    for feature in data["features"]:
        props = feature["properties"]
        geom = feature["geometry"]
        coords = geom["coordinates"]
        earthquake_id = feature["id"]

        record = {
            "ID": earthquake_id,
            "Magnitude_Richter": props.get("mag") or 0,
            "Location": props.get("place") or None,
            "Time_UTC": convert_time(props.get("time")),
            "Last_Updated_UTC": convert_time(props.get("updated")),
            "Time_MYT": convert_malaysia_time(props.get("time")),
            "Last_Updated_MYT": convert_malaysia_time(props.get("updated")),
            "Time_Zone_Offset": props.get("tz") or 0,
            "Detail_URL": props.get("url") or None,
            "Map_URL": props.get("url") + "/map" if props.get("url") else None,
            "Detail_API": props.get("detail") or None,
            "Reported_Felt_Count": props.get("felt") or 0,
            "CDI": props.get("cdi") or 0,
            "MMI": props.get("mmi") or 0,
            "Alert_Level": props.get("alert") or "None",
            "Status": props.get("status") or None,
            "Tsunami_Flag": props.get("tsunami") or 0,
            "Significance": props.get("sig") or 0,
            "Network": props.get("net") or None,
            "Event_Code": props.get("code") or None,
            "IDs": props.get("ids") or None,
            "Sources": props.get("sources") or None,
            "Types": props.get("types") or None,
            "Number_of_Stations": props.get("nst") or 0,
            "Distance_to_Nearest_Station_Degrees": props.get("dmin") or 0,
            "RMS": props.get("rms") or 0,
            "Gap_Degrees": props.get("gap") or 0,
            "Magnitude_Type": props.get("magType") or None,
            "Event_Type": props.get("type") or None,
            "Title": props.get("title") or None,
            "Longitude_Degrees": coords[0] if coords else 0,
            "Latitude_Degrees": coords[1] if coords else 0,
            "Depth_km": coords[2] if coords else 0
        }
        records.append(record)

    df = pd.DataFrame(records)
    df[["State", "Country", "Continent", "Locality"]] = df.apply(
        lambda row: pd.Series(get_location_info(row["Latitude_Degrees"], row["Longitude_Degrees"])),
        axis=1
    )
    df[["State", "Country", "Continent", "Locality"]] = df[["State", "Country", "Continent", "Locality"]].replace("", "Unknown").fillna("Unknown")
    df.columns = df.columns.str.replace(' ', '_').str.replace('[\(\)]', '', regex=True)

    engine = get_engine()
    table_name = "earthquakes"

    create_table_query = """
    CREATE TABLE IF NOT EXISTS earthquakes (
        ID VARCHAR(50) PRIMARY KEY,
        Magnitude_Richter FLOAT,
        Location TEXT,
        Time_UTC DATETIME,
        Last_Updated_UTC DATETIME,
        Time_MYT DATETIME,
        Last_Updated_MYT DATETIME,
        Time_Zone_Offset INT,
        Detail_URL TEXT,
        Map_URL TEXT,
        Detail_API TEXT,
        Reported_Felt_Count INT,
        CDI FLOAT,
        MMI FLOAT,
        Alert_Level VARCHAR(50),
        Status VARCHAR(50),
        Tsunami_Flag INT,
        Significance INT,
        Network VARCHAR(50),
        Event_Code VARCHAR(50),
        IDs TEXT,
        Sources TEXT,
        Types TEXT,
        Number_of_Stations INT,
        Distance_to_Nearest_Station_Degrees FLOAT,
        RMS FLOAT,
        Gap_Degrees FLOAT,
        Magnitude_Type VARCHAR(50),
        Event_Type VARCHAR(50),
        Title TEXT,
        Longitude_Degrees FLOAT,
        Latitude_Degrees FLOAT,
        Depth_km FLOAT,
        State VARCHAR(100),
        Country VARCHAR(100),
        Continent VARCHAR(100),
        Locality VARCHAR(100)
    )
    """

    try:
        with engine.connect() as conn:
            conn.execute(text(create_table_query))
            logging.info(f"Table '{table_name}' is ready.")
            
            existing_ids = pd.read_sql(f"SELECT ID FROM {table_name}", conn)["ID"].tolist()
            new_records = df[~df["ID"].isin(existing_ids)]
            
            if not new_records.empty:
                new_records.to_sql(name=table_name, con=engine, if_exists='append', index=False, chunksize=1000)
                logging.info(f"Inserted {len(new_records)} new records.")
                return len(new_records)
            else:
                logging.info("No new records to insert.")
                return 0
    except Exception as e:
        logging.error(f"Error during MySQL operation: {e}")
        raise