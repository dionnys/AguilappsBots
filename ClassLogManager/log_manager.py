import logging
from datetime import datetime
from ConnectionDao.mongodb_connection import MongoDBConnection


class LogManager:
    @staticmethod
    def log(level, message):
        collection_name = 'logs'
        log_entry = {
            "level": level.upper(),
            "message": message,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        MongoDBConnection.insert_one(collection_name, log_entry)
        logging.log(getattr(logging, level.upper()), message)