from typing import Dict
from e2e.models.model import ModelFactory, Model
import pandas as pd
from e2e.utils import get_date_minus_days
import e2e.constants as constants

@ModelFactory.register('mock_ML_model')
class MockMLModel(Model):
    def __init__(self, split_date: str, company: str, **kwargs):
        super().__init__(company, split_date, **kwargs)
        self._is_trained = False


    def train(self, column_wise_series: Dict[str, pd.Series], prediction_window) -> None:
        pass
        # data = self.generate_training_data(column_wise_series, prediction_window)
        # print(len(data))

    def predict(self, h: int) -> (pd.Series, Dict):
        return pd.Series(7, index=pd.date_range(get_date_minus_days(self.split_date.strftime(constants.DATE_FORMAT), -1), get_date_minus_days(self.split_date.strftime(constants.DATE_FORMAT), -h))), {}