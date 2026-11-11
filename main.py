# Component that exports data from MongoDB and splits it into train/test
from networksecuirty.components.data_ingestion import DataIngestion

# Component that validates column count and checks data drift
from networksecuirty.components.data_validation import DataValidation
from networksecuirty.components.data_transformation import DataTransformation

# Custom exception that adds file name and line number to errors
from networksecuirty.exception.exception import NetworkSecurityException

# Project logger
from networksecuirty.logging.logger import logging

# Config classes holding paths and settings
from networksecuirty.entity.config_entity import (
    DataIngestionConfig,
    TrainingPipelineConfig,
    DataValidationConfig,
    DataTransformationConfig,
)

import sys

# Run only when this file is executed directly
if __name__ == "__main__":
    try:
        # Pipeline-level config (timestamped artifact folder)
        trainingpipelineconfig = TrainingPipelineConfig()

        # Data ingestion config built on top of the pipeline config
        dataingestionconfig = DataIngestionConfig(trainingpipelineconfig)

        # Create the data ingestion component
        data_ingestion = DataIngestion(dataingestionconfig)

        logging.info("Initiate the data ingestion")

        # Run ingestion; returns an artifact with the train/test file paths
        dataingestionartifact = data_ingestion.initiate_data_ingestion()

        logging.info("Data ingestion completed")

        print(dataingestionartifact)

        # Data validation config built on the same pipeline config
        data_validation_config = DataValidationConfig(trainingpipelineconfig)

        # Create the data validation component using the ingestion output
        data_validation = DataValidation(dataingestionartifact, data_validation_config)

        logging.info("Initiate the data validation")

        # Run validation; returns an artifact with the validation status and file paths
        data_validation_artifact = data_validation.initiate_data_validation()

        logging.info("Data validation completed")

        print(data_validation_artifact)


        logging.info("data transformation started")

        data_transformation_config = DataTransformationConfig(trainingpipelineconfig)
        data_transformation = DataTransformation(
            data_validation_artifact, data_transformation_config
        )
        data_transformation_artifact=data_transformation.initiate_data_transformation()

        logging.info("data transformation completed")

    except Exception as e:
        # Wrap any error to include file and line details
        raise NetworkSecurityException(e, sys) from e