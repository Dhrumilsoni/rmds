from typing import Dict
from e2e.models.model import ModelFactory, Model
import pandas as pd
from statsmodels.tsa.api import Holt
from statsmodels.tsa.holtwinters.results import HoltWintersResults


@ModelFactory.register('holt_winters_model')
class HoltWintersModel(Model):

    def __init__(self, stock_column_name=None, damped_trend=False,
                 initialization_method="estimated", **kwargs):
        super().__init__(**kwargs)
        self.model_instance: HoltWintersResults = None
        self.damped_trend = damped_trend
        self.initialization_method = initialization_method
        assert stock_column_name is not None
        self.stock_column_name = stock_column_name

    def train(self, column_wise_series: Dict[str, pd.Series]) -> None:
        series = column_wise_series[self.stock_column_name]
        self.model_instance = Holt(series, damped_trend=self.damped_trend,
                                   initialization_method=self.initialization_method).fit(optimized=True)
        self.model_instance.summary()
        self.is_trained = True

    '''
        :param
        h = The number of days after the split date that you want the forecast for

        :return
        pd.Series containing the forecasts indexed by date
    '''

    def predict(self, h: int) -> (pd.Series, Dict):
        fcast = self.model_instance.forecast(h)
        return fcast, {}

    def summary(self):
        print(self.model_instance.summary())

    def save(self, pth):
        pass