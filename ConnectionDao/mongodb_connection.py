import os
import pymongo
import time
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
    def find_all_documents(cls, collection_name, query=None, sort_by=None, sort_direction=1, projection=None, limit=0):
        collection = cls.connect()[collection_name]
        if sort_by:
            cursor = collection.find(query, projection).sort(sort_by, sort_direction).limit(limit)
        else:
            cursor = collection.find(query, projection).limit(limit)
        results = []
        time.sleep(2)
        for document in cursor:
            results.append(document)
        return results

    @classmethod
    def find_one_documents(cls, collection_name, query=None, projection=None):
        collection = cls.connect()[collection_name]
        result = collection.find_one(query, projection)
        return result

    @classmethod
    def exists_in_field(cls, collection_name, query=None):
        collection = cls.connect()[collection_name]
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
            return result.modified_count
        except pymongo.errors.PyMongoError as e:
            print(f"Error al actualizar el documento: {e}")
    @classmethod
    def delete_one(cls, collection_name, query):
        try:
            collection = cls.connect()[collection_name]
            result = collection.delete_one(query)
            return result.deleted_count
        except pymongo.errors.PyMongoError as e:
            print(f"Error al eliminar el documento: {e}")


    @classmethod
    def replace_document(cls, collection_name, query, new_document):
        try:
            db = collection = cls.connect()[collection_name]
            collection = db[collection_name]
            result = collection.replace_one(query, new_document)

            return result.upserted_id is not None
        except pymongo.errors.PyMongoError as e:
            print(f"Error al reemplazar el documento: {e}")
