# Component that exports data from MongoDB and splits it into train/test
from networksecuirty.components.data_ingestion import DataIngestion

# Custom exception that adds file name and line number to errors
from networksecuirty.exception.exception import NetworkSecurityException

# Project logger
from networksecuirty.logging.logger import logging

# Config classes holding paths and settings
from networksecuirty.entity.config_entity import (
    DataIngestionConfig,
    TrainingPipelineConfig,
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

    except Exception as e:
        # Wrap any error to include file and line details
        raise NetworkSecurityException(e, sys)