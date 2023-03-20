import os
import pymongo
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


class MongoDBConnection:
    @classmethod
    def connect(cls):
        client = MongoClient(os.getenv('nosql_connect'))
        db = client[os.getenv('nosql_database')]
        return db

    @classmethod
    def insert_one(cls, collection_name, document):
        try:
            db = cls.connect()
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
            collection = db[collection_name]
            result = collection.insert_one(document)
            #print(f"Se insertó el documento con ID: {result.inserted_id}")
            return result.inserted_id
        except pymongo.errors.PyMongoError as e:
            print(f"Error al insertar el documento: {e}")

    @classmethod
    def find_documents(cls, collection_name, query=None, projection=None, limit=0):
        collection = cls.connect()[collection_name]
        cursor = collection.find(query, projection).limit(limit)
        results = []
        for document in cursor:
            results.append(document)
        return results

    @classmethod
    def exists_in_field(cls, collection_name, field, value):
        collection = cls.connect()[collection_name]
        query = {field: value}
        result = collection.find_one(query)
        if result:
            return True
        else:
            return False

    @classmethod
    def update_one(cls, collection_name, query, update):
        try:
            collection = cls.connect()[collection_name]
            result = collection.update_one(query, update)
            #print(f"Se actualizaron {result.modified_count} documentos.")
            return result.modified_count
        except pymongo.errors.PyMongoError as e:
            print(f"Error al actualizar el documento: {e}")
