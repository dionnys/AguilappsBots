import logging
import pymongo

class LogManager:
    def __init__(self, database, collection, level=logging.INFO):
        self.client = pymongo.MongoClient(os.getenv('nosql_connect'))
        self.db = self.client[database]
        self.collection = self.db[collection]

        logging.basicConfig(level=level)
        self.logger = logging.getLogger(__name__)

    def log(self, level, message):
        log_entry = {
            "level": level.upper(),
            "message": message,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        self.collection.insert_one(log_entry)
        self.logger.log(getattr(logging, level.upper()), message)

# Crear una instancia de LogManager
log_manager = LogManager("aguilaapps", "logs")

# Uso del LogManager en lugar de la biblioteca de logging estándar
# Ejemplo de cómo utilizar la clase LogManager para registrar mensajes
log_manager.log("INFO", "Mensaje de información")
log_manager.log("ERROR", "Mensaje de error")