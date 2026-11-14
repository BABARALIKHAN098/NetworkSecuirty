import os
import numpy as np

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

""" Data transformation constants  start with the Data transformation DT_NAME """
DATA_TRANSFORMATION_DIR_NAME:str="data_transformation"
DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR:str="transformed"
DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR:str="transformed_object"
## KNN imputer  to replace the missing values with the mean of the column

DATA_TRANSFORMATION_IMPUTER_PARAMS:dict={
    "missing_values":np.nan,
    "n_neighbors":3,
    "weights":"uniform",
}

SAVED_MODEL_DIR=os.path.join("saved_models")
""" Model trainer related constant start with Model trainer Var_name"""
MODEL_TRAINER_DIR_NAME: str = "model_trainer"
MODEL_TRAINER_TRAINED_MODEL_DIR: str = "trained_model"
MODEL_TRAINER_TRAINED_MODEL_NAME: str = "model.pkl"
MODEL_TRAINER_EXPECTED_SCORE: float = 0.6
MODEL_TRAINER_OVER_FITTING_UNDER_FITTING_THRESHOLD: float = 0.05