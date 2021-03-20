from typing import Dict
from e2e.models.model import ModelFactory, Model
import pandas as pd
import numpy as np
from e2e.utils import get_date_minus_days
import e2e.constants as constants
from fbprophet import Prophet

@ModelFactory.register('prophet_model')
class ProphetModel(Model):
    def __init__(self, split_date: str, company: str, **kwargs):
        super().__init__(company, split_date, **kwargs)

    def train(self, column_wise_series: Dict[str, pd.Series], prediction_window: int) -> None:
        ds_value = column_wise_series[constants.STOCK_COLUMN].index
        y_value = column_wise_series[constants.STOCK_COLUMN].values

        stock_dict = {
            "ds": ds_value,
            "y": np.array(y_value).reshape(len(y_value), )
        }
        df = pd.DataFrame(stock_dict)
        df.ds = pd.to_datetime(df.ds)
        # train now
        self.ml = Prophet(interval_width=0.95, weekly_seasonality=True, changepoint_prior_scale=0.05)
        self.ml.add_country_holidays(country_name="US")
        self.ml.fit(df)

    def predict(self, h: int, column_wise_series: Dict[str, pd.Series]) -> (pd.Series, Dict):
        future = self.ml.make_future_dataframe(periods=h)
        forecast = self.ml.predict(future[-h:])
        forecast = forecast.set_index("ds")
        conf_interval = {}
        conf_interval["95"] = [forecast["yhat_lower"], forecast["yhat_upper"]]
        return forecast["yhat"], conf_interval



