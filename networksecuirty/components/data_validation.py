import csv
import math
import os
import sys
from typing import Dict, List

from networksecuirty.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from networksecuirty.entity.config_entity import DataValidationConfig
from networksecuirty.exception.exception import NetworkSecurityException
from networksecuirty.logging.logger import logging
from networksecuirty.constant.training_pipeline import SCHEMA_FILE_PATH
from networksecuirty.utils.main_utils.utils import read_yaml_file, write_yaml_file


class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            # Load the schema (column names and types) from schema.yaml
            self.schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def read_data(file_path) -> List[Dict[str, str]]:
        try:
            with open(file_path, newline="", encoding="utf-8") as file:
                return list(csv.DictReader(file))
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def validate_number_of_columns(self, dataframe: List[Dict[str, str]]) -> bool:
        try:
            # Number of columns expected by the schema
            number_of_columns = len(self.schema_config["columns"])
            logging.info(f"Required number of columns as per schema: {number_of_columns}")
            logging.info(f"Dataframe has columns: {len(dataframe[0]) if dataframe else 0}")

            # True only when the dataframe has exactly the expected column count
            return len(dataframe[0]) == number_of_columns if dataframe else False
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def detect_dataset_drift(self, base_df, current_df, threshold=0.05) -> bool:
        try:
            status = True  # True means no drift detected
            report = {}
            for column in base_df[0]:
                d1 = sorted(float(row[column]) for row in base_df)
                d2 = sorted(float(row[column]) for row in current_df)
                values = sorted(set(d1 + d2))
                d1_index = d2_index = 0
                distance = 0.0
                for value in values:
                    while d1_index < len(d1) and d1[d1_index] <= value:
                        d1_index += 1
                    while d2_index < len(d2) and d2[d2_index] <= value:
                        d2_index += 1
                    distance = max(
                        distance,
                        abs(d1_index / len(d1) - d2_index / len(d2)),
                    )
                p_value = math.exp(-2 * distance * distance * len(d1) * len(d2) / (len(d1) + len(d2)))
                is_found = p_value < threshold
                if is_found:
                    status = False

                report.update({column: {
                    "P_value": p_value,
                    "drift_status": is_found
                }})

            drift_report_file_path = self.data_validation_config.drift_report_file_path

            # Create the report folder if it doesn't exist
            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path, exist_ok=True)

            # Write the drift report for all columns
            write_yaml_file(file_path=drift_report_file_path, content=report)

            return status
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            # Read the train and test data
            train_dataframe = DataValidation.read_data(train_file_path)
            test_dataframe = DataValidation.read_data(test_file_path)

            # Check the column count of both dataframes against the schema
            train_status = self.validate_number_of_columns(dataframe=train_dataframe)
            if not train_status:
                logging.error("Train dataframe does not contain all the columns as per schema file")

            test_status = self.validate_number_of_columns(dataframe=test_dataframe)
            if not test_status:
                logging.error("Test dataframe does not contain all the columns as per schema file")

            # Check for drift between train (base) and test (current) data
            drift_status = self.detect_dataset_drift(base_df=train_dataframe, current_df=test_dataframe)

            # Validation passes only if columns match and no drift is found
            status = train_status and test_status and drift_status

            # Save the validated train and test files
            dir_path = os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path, exist_ok=True)

            for path, records in (
                (self.data_validation_config.valid_train_file_path, train_dataframe),
                (self.data_validation_config.valid_test_file_path, test_dataframe),
            ):
                with open(path, "w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=list(records[0]))
                    writer.writeheader()
                    writer.writerows(records)

            data_validation_artifact = DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)