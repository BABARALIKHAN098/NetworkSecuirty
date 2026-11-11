import sys
import os
import csv
import numpy as np
from networksecuirty.constant.training_pipeline import TARGET_COLUMN
from networksecuirty.constant.training_pipeline import DATA_TRANSFORMATION_IMPUTER_PARAMS
from networksecuirty.exception.exception import NetworkSecurityException
from networksecuirty.logging.logger import logging
from networksecuirty.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
    DataTransformationArtifact
)
from networksecuirty.entity.config_entity import DataTransformationConfig
from networksecuirty.utils.main_utils.utils import save_numpy_array_data,save_object


class NumpyImputer:
    def fit(self, values):
        self.fill_values = np.nanmean(values, axis=0)
        self.fill_values = np.where(np.isnan(self.fill_values), 0.0, self.fill_values)
        return self

    def transform(self, values):
        return np.where(np.isnan(values), self.fill_values, values)


class DataTransformation:
    def __init__(self, data_validation_artifact:DataValidationArtifact,data_transformation_config:DataTransformationConfig):

        try:
            self.data_validation_artifact:DataValidationArtifact=data_validation_artifact
            self.data_transformation_config:DataTransformationConfig=data_transformation_config
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e


    @staticmethod
    def read_data(file_path: str):
        try:
            with open(file_path, newline="", encoding="utf-8") as file:
                return list(csv.DictReader(file))
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e


    def get_data_transformer_object(cls):
        """Create the numeric missing-value transformer used by the pipeline."""


        logging.info("Entered get_data_transformer_object a transformation class")

        try:
            logging.info(
                f"Initialized numeric imputer with parameters: "
                f"{DATA_TRANSFORMATION_IMPUTER_PARAMS}"
            )
            return NumpyImputer()

        except Exception as e:
            raise NetworkSecurityException(e,sys) from e

    def initiate_data_transformation(self)->DataTransformationArtifact:

        logging.info("Entered initiate_data_transformation method of DataTransformation class")

        try:
            logging.info('starting data transformation')

            train_df = DataTransformation.read_data(
                self.data_validation_artifact.valid_train_file_path
            )
            test_df = DataTransformation.read_data(
                self.data_validation_artifact.valid_test_file_path
            )
            feature_columns = [column for column in train_df[0] if column != TARGET_COLUMN]
            input_feature_train_df = np.array(
                [[float(row[column]) for column in feature_columns] for row in train_df]
            )
            target_feature_train_df = np.array(
                [float(row[TARGET_COLUMN]) for row in train_df]
            )
            input_feature_test_df = np.array(
                [[float(row[column]) for column in feature_columns] for row in test_df]
            )
            target_feature_test_df = np.array(
                [float(row[TARGET_COLUMN]) for row in test_df]
            )
            target_feature_train_df = np.where(target_feature_train_df == -1, 0, target_feature_train_df)
            target_feature_test_df = np.where(target_feature_test_df == -1, 0, target_feature_test_df)

            preprocessor=self.get_data_transformer_object()

            preprocessor_object=preprocessor.fit(input_feature_train_df)

            transformed_input_train_feature=preprocessor_object.transform(input_feature_train_df)

            train_arr=np.c_[transformed_input_train_feature,np.array(target_feature_train_df)]


            transformed_input_test_feature=preprocessor_object.transform(input_feature_test_df)

            test_arr=np.c_[transformed_input_test_feature,np.array(target_feature_test_df)]


            #Save numpy data
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path,array=train_arr)

            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path,array=test_arr)

            save_object(self.data_transformation_config.transformed_object_file_path,preprocessor_object)


            # prepare artifact 
            data_transformation_artifact=DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path

            )

            return data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e

            
