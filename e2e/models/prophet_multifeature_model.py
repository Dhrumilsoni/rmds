from typing import Dict
from e2e.models.model import ModelFactory, Model
import pandas as pd
import numpy as np
from e2e.utils import get_date_minus_days
import e2e.constants as constants
from fbprophet import Prophet

@ModelFactory.register('prophet_multifeature_model')
class ProphetMultifeatureModel(Model):
    def __init__(self, split_date: str, company: str, **kwargs):
        super().__init__(company, split_date, **kwargs)

    def train(self, column_wise_series: Dict[str, pd.Series], prediction_window: int) -> None:
        ds_value = column_wise_series[constants.STOCK_COLUMN].index
        y_value = column_wise_series[constants.STOCK_COLUMN].values

        stock_dict = {
            "ds": ds_value,
            "y": np.array(y_value).reshape(len(y_value), )
        }
        # print(column_wise_series)
        for past_days in range(1, self.past_horizon[constants.NEWS_COLUMN]+1):
            temp = column_wise_series[constants.NEWS_LAG_PREFIX+str(past_days)].values
            stock_dict[constants.NEWS_LAG_PREFIX + str(past_days)] = np.array(temp).reshape(len(temp), )

        # with pd.option_context('display.max_rows', 100, 'display.max_columns', 100):
        #     print(stock_dict)

        self.train_data = column_wise_series

        df = pd.DataFrame(stock_dict)
        df.ds = pd.to_datetime(df.ds)
        # train now
        self.ml = Prophet(interval_width=0.95, weekly_seasonality=True, changepoint_prior_scale=self.prior_scale)
        for past_days in range(1, self.past_horizon[constants.NEWS_COLUMN] + 1):
            self.ml.add_regressor(constants.NEWS_LAG_PREFIX+str(past_days), prior_scale=self.prior_scale, mode='multiplicative')
        self.ml.add_country_holidays(country_name="US")
        self.ml.fit(df)

    def predict(self, h: int, column_wise_series: Dict[str, pd.Series]) -> (pd.Series, Dict):
        future = self.ml.make_future_dataframe(periods=h)

        future['ds2'] = future.ds
        future = future.set_index('ds')

        for col_name in column_wise_series.keys():
            future = future.merge(column_wise_series[col_name], how='left', left_index=True, right_index=True)
        future.fillna(method='ffill', inplace=True)
        future.reset_index(inplace=True)
        tmp_by_smit = ['ds']
        tmp_by_smit.extend(future.columns[1:])
        future.columns = tmp_by_smit
        # print(future)
        columns_future = list(future.columns)
        columns_future.remove('ds2')
        future = future.loc[:, columns_future]

        forecast = self.ml.predict(future[-h:])
        forecast = forecast.set_index("ds")
        # print(type(forecast['yhat']))
        conf_interval = {}
        conf_interval["95"] = [forecast["yhat_lower"], forecast["yhat_upper"]]
        return forecast["yhat"], conf_interval



