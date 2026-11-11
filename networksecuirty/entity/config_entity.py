import os
from datetime import datetime

from networksecuirty.constant import training_pipeline


class TrainingPipelineConfig:
    """Holds the pipeline name and the timestamped artifact folder for one run."""

    # BUG FIX: the original `def __init__(self.timestamp=datetime.now())` is a
    # SyntaxError. A parameter cannot be `self.timestamp`. Also, a default of
    # datetime.now() is evaluated once at import time, so every run would get
    # the same timestamp. Using None and calling now() inside fixes both.
    def __init__(self, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()

        # BUG FIX: "%m-%D-%Y-%M-%S" was wrong. %D expands to "11/06/26" (with
        # slashes, which would create nested folders), and %M is minutes where
        # hours (%H) was intended. Fixed format: month-day-year-hour-min-sec.
        timestamp = timestamp.strftime("%m_%d_%Y_%H_%M_%S")

        self.pipeline_name = training_pipeline.PIPELINE_NAME
        self.artifact_name = training_pipeline.ARTIFACT_DIR

        # Each run gets its own folder: Artifacts/<timestamp>
        self.artifact_dir = os.path.join(self.artifact_name, timestamp)

        self.timestamp: str = timestamp


class DataIngestionConfig:
    """Holds all paths and settings needed by the data ingestion step."""

    # BUG FIX: the original took `training_pipeline_` as a parameter, which
    # shadowed the imported module and was never needed. The module is already
    # imported at the top, so only the config object is passed in.
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        # Folder for everything produced by data ingestion:
        # Artifacts/<timestamp>/data_ingestion
        # BUG FIX: the original used the class name `TrainingPipelineConfig`
        # with a misspelled attribute (`artifacts_dir`). It must use the
        # instance's `artifact_dir`. FILE_NAME was also removed from this path
        # because a data file name does not belong in a directory path.
        self.data_ingestion_dir: str = os.path.join(
            training_pipeline_config.artifact_dir,
            training_pipeline.DATA_INGESTION_DIR_NAME,
        )

        # Where the raw data exported from MongoDB is stored:
        # .../data_ingestion/feature_store/<FILE_NAME>
        # (the file name is added here, which is where it belongs)
        self.feature_store_file_path: str = os.path.join(
            self.data_ingestion_dir,
            training_pipeline.DATA_INGESTION_FEATURE_STORE_DIR,
            training_pipeline.FILE_NAME,
        )

        # Path of the training split: .../data_ingestion/ingested/train.csv
        self.training_file_path: str = os.path.join(
            self.data_ingestion_dir,
            training_pipeline.DATA_INGESTION_INGESTED_DIR,
            training_pipeline.TRAIN_FILE_NAME,
        )

        # Path of the testing split: .../data_ingestion/ingested/test.csv
        self.testing_file_path: str = os.path.join(
            self.data_ingestion_dir,
            training_pipeline.DATA_INGESTION_INGESTED_DIR,
            training_pipeline.TEST_FILE_NAME,
        )

        # Fraction of data used for the test set (0.2 = 20%)
        self.train_test_split_ratio: float = (
            training_pipeline.DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO
        )

        # MongoDB collection and database the raw data is read from
        self.collection_name: str = training_pipeline.DATA_INGESTION_COLLECTION_NAME
        self.database_name: str = training_pipeline.DATA_INGESTION_DATABASE_NAME



class DataValidationConfig:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        self.data_validation_dir: str = os.path.join(
            training_pipeline_config.artifact_dir,
            training_pipeline.DATA_VALIDATION_DIR_NAME
        )

        # FIX 1: This used DATA_VALIDATION_INVALID_DIR, so the "valid" directory
        # actually pointed to the "invalid" folder. It must use the VALID constant.
        self.valid_data_dir: str = os.path.join(
            self.data_validation_dir,
            training_pipeline.DATA_VALIDATION_VALID_DIR
        )

        # FIX 2: This was built from self.valid_data_dir, which nested the invalid
        # folder inside the valid folder (valid/invalid). Both folders should be
        # siblings under data_validation_dir.
        self.invalid_data_dir: str = os.path.join(
            self.data_validation_dir,
            training_pipeline.DATA_VALIDATION_INVALID_DIR
        )

        self.valid_train_file_path: str = os.path.join(
            self.valid_data_dir, training_pipeline.TRAIN_FILE_NAME
        )

        self.valid_test_file_path: str = os.path.join(
            self.valid_data_dir, training_pipeline.TEST_FILE_NAME
        )

        self.invalid_train_file_path: str = os.path.join(
            self.invalid_data_dir, training_pipeline.TRAIN_FILE_NAME
        )

        # FIX 3: The invalid test file path was missing. The valid side has both
        # train and test paths, so the invalid side needs both too, otherwise
        # invalid test data has nowhere to be saved.
        self.invalid_test_file_path: str = os.path.join(
            self.invalid_data_dir, training_pipeline.TEST_FILE_NAME
        )

        # FIX 4: The old attribute was named "drift_report_dir" but included the
        # report file name, so it was really a file path. Renamed to
        # drift_report_file_path. If other code uses drift_report_dir, update it.
        self.drift_report_file_path: str = os.path.join(
            self.data_validation_dir,
            training_pipeline.DATA_VALIDATION_DRIFT_REPORT_DIR,
            training_pipeline.DATA_VALIDATION_DRIFT_REPORT_FILE_NAME
        )