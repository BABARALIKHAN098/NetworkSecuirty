import os
import sys
import csv
import random
from typing import Dict, List

from dotenv import load_dotenv

from networksecuirty.constant.training_pipeline import FILE_NAME
from networksecuirty.entity.artifact_entity import DataIngestionArtifact
from networksecuirty.entity.config_entity import DataIngestionConfig
from networksecuirty.exception.exception import NetworkSecurityException
from networksecuirty.logging.logger import logging

# BUG FIX: load_dotenv was imported but never called, so MONGO_DB_URL was
# always None. It must run before os.getenv.
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")
LOCAL_DATA_FILE_PATH = os.path.join("Network_Data", FILE_NAME)


class DataIngestion:
    """Reads data from MongoDB, saves it to a feature store CSV, and splits it
    into train and test CSV files."""

    # BUG FIX: the parameter was named `data_ingestion`, but the body read
    # `self.data_ingestion_config`, which does not exist yet. Renamed the
    # parameter and assigned it properly.
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_collection_as_dataframe(self) -> List[Dict[str, str]]:
        """Read MongoDB when configured, otherwise use the bundled CSV dataset."""
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name

            if MONGO_DB_URL and MONGO_DB_URL.startswith(("mongodb://", "mongodb+srv://")):
                import certifi
                import pymongo

                self.mongo_client = pymongo.MongoClient(
                    MONGO_DB_URL, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000
                )
                collection = self.mongo_client[database_name][collection_name]
                records = list(collection.find())
                for record in records:
                    record.pop("_id", None)
                if records:
                    return [{key: str(value) for key, value in record.items()} for record in records]
                logging.warning("MongoDB collection is empty; using the local dataset")

            logging.warning("MongoDB is not configured; using %s", LOCAL_DATA_FILE_PATH)
            with open(LOCAL_DATA_FILE_PATH, newline="", encoding="utf-8") as file:
                return list(csv.DictReader(file))

        except Exception as e:
            if os.path.exists(LOCAL_DATA_FILE_PATH):
                logging.warning("MongoDB read failed; using local dataset: %s", e)
                with open(LOCAL_DATA_FILE_PATH, newline="", encoding="utf-8") as file:
                    return list(csv.DictReader(file))
            raise NetworkSecurityException(e, sys)

    def export_data_into_feature_store(self, dataframe: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Save the raw records to the feature store CSV and return them."""
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            with open(feature_store_file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=list(dataframe[0]))
                writer.writeheader()
                writer.writerows(dataframe)
            return dataframe

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def split_data_as_train_test(self, dataframe: List[Dict[str, str]]) -> None:
        """Split records into train and test CSV files."""
        try:
            shuffled_data = list(dataframe)
            random.Random(42).shuffle(shuffled_data)
            split_index = int(len(shuffled_data) * (1 - self.data_ingestion_config.train_test_split_ratio))
            train_set = shuffled_data[:split_index]
            test_set = shuffled_data[split_index:]
            logging.info("Performed train test split on the dataframe")
            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)
            fieldnames = list(dataframe[0])
            for path, records in (
                (self.data_ingestion_config.training_file_path, train_set),
                (self.data_ingestion_config.testing_file_path, test_set),
            ):
                with open(path, "w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(records)
            logging.info("Exported train and test files")

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        """Run the full ingestion: MongoDB -> feature store -> train/test split."""
        try:
            # BUG FIX: `self.export.collection_as_dataframe` was wrong twice:
            # wrong method name, and it was not called (no parentheses)
            dataframe = self.export_collection_as_dataframe()
            dataframe = self.export_data_into_feature_store(dataframe)

            self.split_data_as_train_test(dataframe)

            # BUG FIX: the original returned a DataIngestionConfig, which is
            # the wrong class, and passed training_file for the test path.
            # It must return an artifact holding both file paths.
            dataingestionartifact = DataIngestionArtifact(
                train_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path,
            )
            return dataingestionartifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)