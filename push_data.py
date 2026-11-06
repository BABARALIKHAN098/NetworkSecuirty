import os
import sys
import json

import certifi
import pandas as pd
import pymongo  # BUG FIX: was missing, so pymongo.MongoClient raised NameError
from dotenv import load_dotenv

from networksecuirty.exception.exception import NetworkSecurityException
from networksecuirty.logging.logger import logging

# Load environment variables from the .env file
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

# Trusted CA bundle so the TLS connection to MongoDB Atlas can be verified
ca = certifi.where()


class NetworkDataExtract:
    """Reads network/phishing data from a CSV file and loads it into MongoDB."""

    def __init__(self):
        pass  # nothing to initialise; the useless try/except was removed

    def csv_to_json_convertor(self, file_path):
        """Convert a CSV file into a list of dict records (one per row)."""
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)

            # BUG FIX: the original `json.load(data.T.To.json()).values` had
            # three errors: `.To` (should be `.to_json`), `json.load` (expects a
            # file; should be `json.loads`), and `.values` without `()`.
            records = json.loads(data.to_json(orient="records"))
            return records

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def insert_data_mongodb(self, records, database, collection):
        """Insert records into the given MongoDB database/collection.

        Returns the number of records inserted.
        """
        try:
            # BUG FIX: the original reused the same attribute for the name and
            # the object. Separate variables keep it clear.
            # tlsCAFile=ca makes use of certifi (it was unused before).
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)
            db = self.mongo_client[database]
            col = db[collection]

            # BUG FIX: typo `self.coolection` -> `col`
            col.insert_many(records)

            # BUG FIX: `len.self.records` -> `len(records)`
            return len(records)

        # BUG FIX: the original `try` had no `except`, which is a SyntaxError
        except Exception as e:
            raise NetworkSecurityException(e, sys)


if __name__ == "__main__":
    FILE_PATH = "Network_Data/phisingData.csv"
    DATABASE = "sample_mflix"
    COLLECTION = "NetworkData"

    networkobj = NetworkDataExtract()

    # Step 1: CSV -> list of dicts
    records = networkobj.csv_to_json_convertor(file_path=FILE_PATH)

    # Step 2: insert into MongoDB
    no_of_records = networkobj.insert_data_mongodb(records, DATABASE, COLLECTION)

    print(f"Inserted {no_of_records} records")
    
        