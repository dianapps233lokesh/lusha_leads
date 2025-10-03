from pymongo import MongoClient

from app.core.config import settings
from app.utils.logger import logging


def get_db_connection():
    """Establishes a connection to the MongoDB database."""
    client = MongoClient(settings.MONGO_URI)
    logging.info(
        f"database connected successfully. and database name is {client[settings.MONGO_DB_NAME]}"
    )
    return client[settings.MONGO_DB_NAME]


def get_collection(collection_name):
    """Returns a collection from the database."""
    db = get_db_connection()
    logging.info(f"database collection name is {db[collection_name]}")

    return db[collection_name]
