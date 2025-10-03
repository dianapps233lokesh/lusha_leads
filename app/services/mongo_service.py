from app.core.database import get_collection
from app.utils.logger import logging


class MongoService:
    def __init__(self, collection_name):
        self.collection = get_collection(collection_name)

    def save_data(self, data):
        """Saves data to the collection."""
        logging.info("saving data innto the database....")
        if not data:
            return
        if isinstance(data, list):
            self.collection.insert_many(data)
        else:
            self.collection.insert_one(data)


mongo_service = MongoService("leads")
