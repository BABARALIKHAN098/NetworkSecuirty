import os
import sys
from typing import Optional

import certifi
import numpy as np
import pandas as pd  # BUG FIX: was missing, so pd.DataFrame raised NameError
import pymongo
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split

from networksecuirty.entity.artifact_entity import DataIngestionArtifact
from networksecuirty.entity.config_entity import DataIngestionConfig
from networksecuirty.exception.exception import NetworkSecurityException
from networksecuirty.logging.logger import logging

# BUG FIX: load_dotenv was imported but never called, so MONGO_DB_URL was
# always None. It must run before os.getenv.
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")


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

    def export_collection_as_dataframe(self) -> pd.DataFrame:
        """Read the MongoDB collection and return it as a pandas DataFrame."""
        try:
            database_name = self.data_ingestion_config.database_name
            # BUG FIX: the attribute is `collection_name`, not `collection`
            collection_name = self.data_ingestion_config.collection_name

            # tlsCAFile=certifi.where() lets the TLS connection to Atlas verify
            self.mongo_client = pymongo.MongoClient(
                MONGO_DB_URL, tlsCAFile=certifi.where()
            )
            collection = self.mongo_client[database_name][collection_name]

            df = pd.DataFrame(list(collection.find()))

            # MongoDB adds an internal "_id" column that is not a feature
            if "_id" in df.columns:
                df = df.drop(columns=["_id"])

            # BUG FIX: the original `{"na:", np.nan}` was a set, not a dict,
            # and "na:" had a stray colon. Also, replace() and return were
            # indented inside the `if`, so the function returned None
            # whenever there was no "_id" column. Now they always run.
            df = df.replace({"na": np.nan})

            return df

        except Exception as e:
            # BUG FIX: the original raised the exception class without
            # arguments, which would itself fail
            raise NetworkSecurityException(e, sys)

    def export_data_into_feature_store(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Save the raw DataFrame to the feature store CSV and return it."""
        try:
            # BUG FIX: typo `data_ingestion_config_config`
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path

            # Create the folder if it does not exist yet
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)

            dataframe.to_csv(feature_store_file_path, index=False, header=True)

            return dataframe

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def split_data_as_train_test(self, dataframe: pd.DataFrame) -> None:
        """Split the DataFrame into train and test sets and save them as CSV."""
        # BUG FIX: the original `try` had no `except`, which is a SyntaxError
        try:
            train_set, test_set = train_test_split(
                dataframe,
                test_size=self.data_ingestion_config.train_test_split_ratio,
                random_state=42,  # makes the split reproducible
            )
            logging.info("Performed train test split on the dataframe")

            # Create the folder for the train/test files
            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)

            logging.info("Exporting train and test files")

            train_set.to_csv(
                self.data_ingestion_config.training_file_path, index=False, header=True
            )
            test_set.to_csv(
                self.data_ingestion_config.testing_file_path, index=False, header=True
            )

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