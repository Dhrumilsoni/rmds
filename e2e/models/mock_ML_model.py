import random
from typing import Dict
from e2e.models.model import ModelFactory, Model
import pandas as pd
from e2e.utils import get_date_minus_days
import e2e.constants as constants
from e2e.train_test_split import TrainTestSplit
import datetime

@ModelFactory.register('mock_ML_model')
class MockMLModel(Model):
    def __init__(self, split_date: str, company: str, **kwargs):
        super().__init__(company, split_date)
        self.past_horizon = kwargs[constants.PAST_HORIZON]
        if constants.TRAINING_SAMPLES in kwargs:
            self.training_samples = kwargs[constants.TRAINING_SAMPLES]
        else:
            self.training_samples = 100

        self._is_trained = False

    def generate_random_dates(self, start_date, end_date, n):
        d1 = datetime.datetime.strptime(start_date, constants.DATE_FORMAT)
        d2 = datetime.datetime.strptime(end_date, constants.DATE_FORMAT)
        r = (d2 - d1).days + 1
        samples = random.sample(range(r), n)
        dates = []
        for sample in samples:
            dates.append(get_date_minus_days(start_date, -sample))

        return dates

    def generate_training_data(self, cws: Dict[str, pd.Series], prediction_window):
        columns_info = {}
        dataFrameList = []
        min_len = float('inf')
        max_len = 0
        for key in cws:
            min_len = min(min_len, len(cws[key]))
        min_len = int(min_len)

        for key in cws:
            if key not in self.past_horizon:
                assert False, "{} not found in past horizon hyperparameter"
            columns_info[key] = self.past_horizon[key]
            max_len = max(max_len, columns_info[key])
            dataFrameList.append(cws[key])

        start_date = cws[constants.STOCK_COLUMN].index[-min_len].strftime(constants.DATE_FORMAT)
        end_date = self.split_date.strftime(constants.DATE_FORMAT)

        dataFrame = pd.concat(dataFrameList, axis=1)

        tts = TrainTestSplit(prediction_window, columns_info, start_date, end_date)
        split_start_date = get_date_minus_days(start_date, max_len)
        split_end_date = get_date_minus_days(end_date, prediction_window)
        split_dates = self.generate_random_dates(split_start_date, split_end_date, self.training_samples)
        split_data = tts.do_split(dataFrame, split_dates)
        return split_data


    def train(self, column_wise_series: Dict[str, pd.Series], prediction_window) -> None:
        data = self.generate_training_data(column_wise_series, prediction_window)
        print(data)

    def predict(self, h: int) -> (pd.Series, Dict):
        return pd.Series(7, index=pd.date_range(get_date_minus_days(self.split_date.strftime(constants.DATE_FORMAT), -1), get_date_minus_days(self.split_date.strftime(constants.DATE_FORMAT), -h))), {}