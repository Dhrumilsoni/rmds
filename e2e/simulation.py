import argparse
from typing import List, Dict, Tuple
from abc import abstractmethod
from collections.abc import Callable
import pandas as pd
import constants
import datetime
from utils import get_date_minus_days
from e2e.models.model import Model


def parse_args():
    parser = argparse.ArgumentParser()
    return parser.parse_args()


class AbstractSimulator:
    def __init__(self, **kwargs):
        self.initial_amount = kwargs[constants.INITIAL_AMOUNT]
        # INFO: we are investing on only the stock that is passed in the stock argument.
        self.stock = kwargs['stock']
        # see next two functions comments.
        self.stock_val = {}
        # INFO: can't think of any other args :(

    @abstractmethod
    def add(self, model: Model, df_test_ground_truth: Dict[str, pd.Series], df_train: Dict[str, pd.DataFrame]) -> None:
        """
        - get the prediction for the test series values
        - dict (key->company, df(date, cur_val, next_val))
        """
        pass

    @abstractmethod
    def complete(self):
        """
        This method will note that there is nothing else to be added and simulation ends.

        - loop over time
            - buy/sell according to the prediction
            - update the current_money and current_invested variables

        All summary or stats will be printed from here.
        """
        pass

class SimulatorFactory:
    """ The factory class for creating executors"""

    registry = {}
    """ Internal registry for available executors """

    @classmethod
    def create_simulator(cls, name: str, **kwargs) -> AbstractSimulator:
        """ Factory command to create the executor """

        exec_class = cls.registry[name]
        executor = exec_class(**kwargs)
        return executor

    # end create_executor()

    @classmethod
    def register(cls, name: str) -> Callable:
        def inner_wrapper(wrapped_class: AbstractSimulator) -> Callable:
            if name in cls.registry:
                print('Executor %s already exists. Will replace it', name)
            cls.registry[name] = wrapped_class
            return wrapped_class

        return inner_wrapper


@SimulatorFactory.register('S1')
class S1Simulator(AbstractSimulator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # if there are more than one stocks. S1 shouldn't run.
        assert len(self.stock) == 1, "S1 should have only one stock."
        self.prediction_window = 1

    def add(self, model: Model, df_test_ground_truth: Dict[str, pd.Series], df_train: Dict[str, pd.DataFrame]) -> None:
        df_test_for_prediction = {}
        for col in df_test_ground_truth:
            if col != constants.STOCK_COLUMN:
                df_test_for_prediction[col] = df_test_ground_truth[col]

        prediction, confidence_interval = model.predict(self.prediction_window, df_test_for_prediction)
        prediction = prediction[-self.prediction_window:]
        for interval in confidence_interval:
            confidence_interval[interval][0] = confidence_interval[interval][0][-self.prediction_window:]
            confidence_interval[interval][1] = confidence_interval[interval][1][-self.prediction_window:]
        self.stock_val[model.company] = self.stock_val.get(model.company, {
                                                                    "date": [],
                                                                    "cur_val": [],
                                                                    "next_val": [],
                                                                    "lower_bound": [],
                                                                    "upper_bound": []
                                                                })

        date = datetime.datetime.strptime(get_date_minus_days(prediction.index[0].strftime(constants.DATE_FORMAT), 1), constants.DATE_FORMAT)
        self.stock_val[model.company]["date"].append(date)
        self.stock_val[model.company]["cur_val"].append(df_train[constants.STOCK_COLUMN][constants.STOCK_COLUMN][date])
        self.stock_val[model.company]["next_val"].append(prediction.values[0])
        self.stock_val[model.company]["lower_bound"].append(confidence_interval["95"][0].values[0])
        self.stock_val[model.company]["upper_bound"].append(confidence_interval["95"][1].values[0])

    def complete(self):
        current_money = self.initial_amount
        current_stocks = 0
        all_val = self.stock_val[self.stock[0]]
        net_worth = []
        for ind, date in enumerate(all_val["date"]):
            if all_val["cur_val"][ind] < all_val["next_val"][ind]:
                current_stocks += current_money / all_val["cur_val"][ind]
                current_money = 0

            if all_val["cur_val"][ind] > all_val["next_val"][ind]:
                current_money += current_stocks*all_val["cur_val"][ind]
                current_stocks = 0

            net_worth.append(current_money+current_stocks*all_val["cur_val"][ind])
        pd.Series(net_worth).plot()


@SimulatorFactory.register('S2')
class S2Simulator(AbstractSimulator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # if there are more than one stocks. S2 shouldn't run.
        # TODO: Think about multiple stocks anytime soon.
        assert len(self.stock) == 1, "S2 should have only one stock."
        self.prediction_window = 1

    # TODO: add "add" function in the parent class instead of the child class.
    def add(self, model: Model, df_test_ground_truth: Dict[str, pd.Series], df_train: Dict[str, pd.DataFrame]) -> None:
        df_test_for_prediction = {}
        for col in df_test_ground_truth:
            if col != constants.STOCK_COLUMN:
                df_test_for_prediction[col] = df_test_ground_truth[col]

        prediction, confidence_interval = model.predict(self.prediction_window, df_test_for_prediction)
        prediction = prediction[-self.prediction_window:]
        for interval in confidence_interval:
            confidence_interval[interval][0] = confidence_interval[interval][0][-self.prediction_window:]
            confidence_interval[interval][1] = confidence_interval[interval][1][-self.prediction_window:]
        self.stock_val[model.company] = self.stock_val.get(model.company, {
                                                                    "date": [],
                                                                    "cur_val": [],
                                                                    "next_val": [],
                                                                    "lower_bound": [],
                                                                    "upper_bound": []
                                                                })

        date = datetime.datetime.strptime(get_date_minus_days(prediction.index[0].strftime(constants.DATE_FORMAT), 1), constants.DATE_FORMAT)
        self.stock_val[model.company]["date"].append(date)
        self.stock_val[model.company]["cur_val"].append(df_train[constants.STOCK_COLUMN][constants.STOCK_COLUMN][date])
        self.stock_val[model.company]["next_val"].append(prediction.values[0])
        self.stock_val[model.company]["lower_bound"].append(confidence_interval["95"][0].values[0])
        self.stock_val[model.company]["upper_bound"].append(confidence_interval["95"][1].values[0])

    def complete(self):
        current_money = self.initial_amount
        current_stocks = 0
        all_val = self.stock_val[self.stock[0]]
        net_worth = []
        for ind, date in enumerate(all_val["date"]):
            if all_val["cur_val"][ind] < all_val["next_val"][ind]:
                money_to_invest = current_money*(1-(all_val["next_val"][ind]-all_val["lower_bound"][ind])/(all_val["upper_bound"][ind]-all_val["lower_bound"][ind]))
                current_stocks += money_to_invest / all_val["cur_val"][ind]
                current_money -= money_to_invest

            if all_val["cur_val"][ind] > all_val["next_val"][ind]:
                current_money += current_stocks*all_val["cur_val"][ind]
                current_stocks = 0

            net_worth.append(current_money+current_stocks*all_val["cur_val"][ind])
        pd.Series(net_worth).plot()


@SimulatorFactory.register('S3')
class S3Simulator(AbstractSimulator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # if there are more than one stocks. S2 shouldn't run.
        # TODO: Think about multiple stocks anytime soon.
        assert len(self.stock) == 1, "S3 should have only one stock."
        self.prediction_window = 1

    # TODO: add "add" function in the parent class instead of the child class.
    def add(self, model: Model, df_test_ground_truth: Dict[str, pd.Series], df_train: Dict[str, pd.DataFrame]) -> None:
        df_test_for_prediction = {}
        for col in df_test_ground_truth:
            if col != constants.STOCK_COLUMN:
                df_test_for_prediction[col] = df_test_ground_truth[col]

        prediction, confidence_interval = model.predict(self.prediction_window, df_test_for_prediction)
        prediction = prediction[-self.prediction_window:]
        for interval in confidence_interval:
            confidence_interval[interval][0] = confidence_interval[interval][0][-self.prediction_window:]
            confidence_interval[interval][1] = confidence_interval[interval][1][-self.prediction_window:]
        self.stock_val[model.company] = self.stock_val.get(model.company, {
                                                                    "date": [],
                                                                    "cur_val": [],
                                                                    "next_val": [],
                                                                    "lower_bound": [],
                                                                    "upper_bound": []
                                                                })

        date = datetime.datetime.strptime(get_date_minus_days(prediction.index[0].strftime(constants.DATE_FORMAT), 1), constants.DATE_FORMAT)
        self.stock_val[model.company]["date"].append(date)
        self.stock_val[model.company]["cur_val"].append(df_train[constants.STOCK_COLUMN][constants.STOCK_COLUMN][date])
        self.stock_val[model.company]["next_val"].append(prediction.values[0])
        self.stock_val[model.company]["lower_bound"].append(confidence_interval["95"][0].values[0])
        self.stock_val[model.company]["upper_bound"].append(confidence_interval["95"][1].values[0])

    def complete(self):
        current_money = self.initial_amount
        current_stocks = 0
        all_val = self.stock_val[self.stock[0]]
        net_worth = []
        for ind, date in enumerate(all_val["date"]):
            if all_val["cur_val"][ind] < all_val["next_val"][ind]:
                if all_val["cur_val"][ind]<all_val["lower_bound"][ind]:
                    # invest all
                    money_to_invest = current_money
                else:
                    money_to_invest = current_money*(1-(all_val["cur_val"][ind]-all_val["lower_bound"][ind])/(all_val["upper_bound"][ind]-all_val["lower_bound"][ind]))
                current_stocks += money_to_invest / all_val["cur_val"][ind]
                current_money -= money_to_invest

            if all_val["cur_val"][ind] > all_val["next_val"][ind]:
                current_money += current_stocks*all_val["cur_val"][ind]
                current_stocks = 0

            net_worth.append(current_money+current_stocks*all_val["cur_val"][ind])
        pd.Series(net_worth).plot()

