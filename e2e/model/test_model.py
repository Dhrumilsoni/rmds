from typing import Dict
from e2e.model.model import ModelFactory, Model
import pandas as pd


@ModelFactory.register('test_model')
class TestModel(Model):
    def __init__(self, split_date: str, company: str, hyperparams: Dict):
        super().__init__(company, split_date)
        self.hyperparams = hyperparams
        self._is_trained = False

    def train(self, column_wise_series: Dict[str, pd.Series]) -> None:
        pass

    '''
    :param
    h = The number of days after the split date that you want the forecast for

    :return
    pd.Series containing the forecasts indexed by date
    '''

    def predict(self, h: int) -> pd.Series:
        pass

    def summary(self):
        pass

    def save(self, pth):
        pass