from typing import Dict
from e2e.models.model import ModelFactory, Model
import pandas as pd
import numpy as np
from e2e.utils import get_date_minus_days
import e2e.constants as constants
from fbprophet import Prophet

@ModelFactory.register('prophet_multifeature_model2')
class ProphetMultifeatureModel2(Model):
    def __init__(self, split_date: str, company: str, **kwargs):
        super().__init__(company, split_date, **kwargs)

    def train(self, column_wise_series: Dict[str, pd.Series], prediction_window: int) -> None:
        ds_value = column_wise_series[constants.STOCK_COLUMN].index
        y_value = column_wise_series[constants.STOCK_COLUMN].values
        oil = column_wise_series[constants.OIL_COLUMN].values
        # news_value = column_wise_series[constants.NEWS_COLUMN_2].values

        stock_dict = {
            "ds": ds_value,
            "y": np.array(y_value).reshape(len(y_value), ),
            "oil": np.array(oil).reshape(len(oil), )
        }

        df = pd.DataFrame(stock_dict)
        df.ds = pd.to_datetime(df.ds)
        # train now
        self.ml = Prophet(interval_width=0.95, weekly_seasonality=True, changepoint_prior_scale=0.05)
        self.ml.add_country_holidays(country_name="US")

        self.ml.add_regressor('oil', prior_scale=0.05, mode="multiplicative")
        # self.ml.add_regressor('news', prior_scale=0.05, mode="multiplicative")
        self.ml.fit(df)

        # df_news = df[['ds', 'news']]
        # df_news.rename(columns={'news': 'y'}, inplace=True)
        # self.ml_news = Prophet(interval_width=0.95, weekly_seasonality=True, changepoint_prior_scale=0.05)
        # self.ml_news.add_country_holidays(country_name="US")
        # self.ml_news.fit(df_news)

        df_oil = df[['ds', 'oil']]
        df_oil.rename(columns={'oil': 'y'}, inplace=True)
        self.ml_oil = Prophet(interval_width=0.95, weekly_seasonality=True, changepoint_prior_scale=0.05)
        self.ml_oil.add_country_holidays(country_name="US")
        self.ml_oil.fit(df_oil)
        #


    def predict(self, h: int, column_wise_series: Dict[str, pd.Series]) -> (pd.Series, Dict):
        future = self.ml.make_future_dataframe(periods=h)

        # forecast_news = self.ml_news.predict(future)
        forecast_oil = self.ml_oil.predict(future)
        final_future = pd.concat([future[-h:], forecast_oil["yhat"][-h:]], axis=1)
        # final_future = pd.concat([future[-h:], forecast_oil["yhat"][-h:]], axis=1)
        final_future.columns = ["ds", "oil"]

        forecast = self.ml.predict(final_future[-h:])
        forecast = forecast.set_index("ds")
        # print(type(forecast['yhat']))
        conf_interval = {}
        conf_interval["95"] = [forecast["yhat_lower"], forecast["yhat_upper"]]
        return forecast["yhat"], conf_interval