import os

import pymongo

MONGO_DB_NAME = "project"
MONITORS_COLLECTION_NAME = "monitors"


def get_prod_client():
    return pymongo.MongoClient(host=os.getenv("MONGO_URL"))
