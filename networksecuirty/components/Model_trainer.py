import os,sys
from networksecuirty.exception.exception import NetworkSecurityException
from networksecuirty.logging.logger import logging
from networksecuirty.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact
from networksecuirty.entity.config_entity import ModelTrainerConfig
from networksecuirty.utils.main_utils.utils import evaluate_models
from networksecuirty.utils.ml_utils.model.estimator import NetworkModel
from networksecuirty.utils.main_utils.utils import save_object,load_object,save_numpy_array_data,load_numpy_array_data
from networksecuirty.utils.ml_utils.metric.classification_metric import get_classification_score

class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig,
                 data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e
    
    def track_mlflow(self,best_model,classificationmetric):
        ssl_cert_file = os.environ.get("SSL_CERT_FILE")
        if ssl_cert_file and not os.path.isfile(ssl_cert_file):
            import certifi

            os.environ["SSL_CERT_FILE"] = certifi.where()
            logging.warning(
                "Ignoring missing SSL_CERT_FILE and using certifi's CA bundle: %s",
                ssl_cert_file,
            )

        import dagshub
        import mlflow

        dagshub.init(repo_owner='BABARALIKHAN098', repo_name='NetworkSecuirty', mlflow=True)

        with mlflow.start_run():
            f1_score=classificationmetric.f1_score
            precision_score=classificationmetric.precision_score
            recall_score=classificationmetric.recall_score

            mlflow.log_metric("f1_score",f1_score)
            mlflow.log_metric("precision_score",precision_score)
            mlflow.log_metric("recall_score",recall_score)

            mlflow.sklearn.log_model(
                best_model,
                "model",
                skops_trusted_types=["sklearn.tree._tree.Tree"],
            )
    def train_model(self,x_train,y_train,x_test,y_test):
        from sklearn.linear_model import LogisticRegression
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.ensemble import (
            AdaBoostClassifier,
            GradientBoostingClassifier,
            RandomForestClassifier,
        )

        models={
            "RandomForest":RandomForestClassifier(verbose=1),
            "DecisionTree":DecisionTreeClassifier(),
            "GradientBoosting":GradientBoostingClassifier(verbose=1),
            "LogisticRegression":LogisticRegression(verbose=1),
            "AdaBoost":AdaBoostClassifier(),
        }
        params= {
            "RandomForest": {
                "n_estimators": [100, 200, 300],
                "criterion": ["gini", "entropy", "log_loss"],
                "max_depth": [None, 5, 10, 20],
            },
            "DecisionTree": {
                "criterion": ["gini", "entropy", "log_loss"],
                "splitter": ["best", "random"],
                "min_samples_split": [2, 5, 10],
            },
            "GradientBoosting": {
                "n_estimators": [100, 200, 300],
                "learning_rate": [0.01, 0.05, 0.1, 0.2],
                "subsample": [0.8, 1.0],
            },
            "LogisticRegression": {
               "penalty": ["l1", "l2"],
               "solver": ["liblinear", "saga"],
            },
            "AdaBoost": {
                "n_estimators": [50, 100, 200, 300],
                "learning_rate": [0.01, 0.05, 0.1, 1.0],
                "algorithm": ["SAMME"]
            }
        }

        model_report:dict=evaluate_models(x_train=x_train,y_train=y_train,x_test=x_test,y_test=y_test,models=models,param=params)
        best_model_score=max(sorted(model_report.values()))
        best_model_name=list(model_report.keys())[list(model_report.values()).index(best_model_score)]
        best_model=models[best_model_name]
        y_train_pred=best_model.predict(x_train)
        classification_train_metric=get_classification_score(y_true=y_train,y_pred=y_train_pred)

        y_test_pred=best_model.predict(x_test)
        classification_test_metric=get_classification_score(y_true=y_test,y_pred=y_test_pred)
        self.track_mlflow(best_model,classification_test_metric)
        preprocessor=load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)

        model_dir_path=os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path,exist_ok=True)

        network_model=NetworkModel(preprocessor=preprocessor,model=best_model)
        save_object(self.model_trainer_config.trained_model_file_path,obj=network_model)

        model_trainer_artifact=ModelTrainerArtifact(
            trained_model_file_path=self.model_trainer_config.trained_model_file_path,
            train_metric_artifact=classification_train_metric,
            test_metric_artifact=classification_test_metric
        )
        logging.info(f"Model trainer artifact {model_trainer_artifact}")
        return model_trainer_artifact

    def initiate_model_trainer(self)->ModelTrainerArtifact:
        try:
            train_file_path=self.data_transformation_artifact.transformed_test_file_path
            test_file_path=self.data_transformation_artifact.transformed_test_file_path
            train_arr=load_numpy_array_data(train_file_path)
            test_arr=load_numpy_array_data(test_file_path)
            X_train, y_train = train_arr[:, :-1], train_arr[:, -1]
            X_test, y_test = test_arr[:, :-1], test_arr[:, -1]
            model_trainer_artifact=self.train_model(X_train,y_train,X_test,y_test)
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e

   