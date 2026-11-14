import sys
from networksecuirty.exception.exception import NetworkSecurityException
from networksecuirty.logging.logger import logging


class NetworkModel:
    def __init__(self,model,preprocessor):
        """
        model: trained model object
        preprocessor:preprocessor object
        """
        try:
            self.preprocessor=preprocessor
            self.model=model
        except Exception as e:
            raise NetworkSecurityException(e,sys)from e


    def predict(self,x):
        try:
            x_transform=self.preprocessor.transform(x)
            y_hat=self.model.predict(x_transform)

            return y_hat
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e

        