import os
# Common constants used across the training pipeline

# Name of the target (label) column in the dataset
TARGET_COLUMN: str = "Result"

# Name of the pipeline, used for naming/organising outputs
PIPELINE_NAME: str = "NetworkSecurity"

# Root folder where all pipeline outputs (artifacts) are saved
ARTIFACT_DIR: str = "Artifacts"

# Name of the raw dataset file
FILE_NAME: str = "phisingData.csv"

# File names for the train/test splits created during ingestion
TRAIN_FILE_NAME: str = "train.csv"
TEST_FILE_NAME: str = "test.csv"


# Data Ingestion constants (all start with DATA_INGESTION_)

# MongoDB collection that holds the raw network data
DATA_INGESTION_COLLECTION_NAME: str = "NetworkData"

# MongoDB database that contains the collection
# Keep this aligned with the database used by push_data.py.
DATA_INGESTION_DATABASE_NAME: str = "sample_mflix"

# Folder (inside ARTIFACT_DIR) for everything produced by data ingestion
DATA_INGESTION_DIR_NAME: str = "data_ingestion"

# Sub-folder where the raw data exported from MongoDB is stored
DATA_INGESTION_FEATURE_STORE_DIR: str = "feature_store"

# Sub-folder where the final train/test CSV files are saved
DATA_INGESTION_INGESTED_DIR: str = "ingested"

# Fraction of data used for the test set (0.2 = 20% test, 80% train)
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO: float = 0.2




""" Data validation constants  start with the Data validation VR_NAME """
SCHEMA_FILE_PATH=os.path.join(".github", "data_schema", "schema.yaml")
DATA_VALIDATION_DIR_NAME:str="data_validation"
DATA_VALIDATION_VALID_DIR:str="validated"
DATA_VALIDATION_INVALID_DIR:str="invalid"
DATA_VALIDATION_DRIFT_REPORT_DIR:str="drift_report"
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME:str="report.yaml"
