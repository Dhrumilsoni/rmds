import argparse
from abc import abstractmethod
from typing import List, Dict
import pandas as pd
from collections.abc import Callable
import e2e.constants as constants
from e2e.train_test_split import TrainTestSplit
import datetime
import random
from e2e.utils import get_date_minus_days


def parse_args():
	parser = argparse.ArgumentParser()
	return parser.parse_args()


class Model(object):
	def __init__(self, company: str = None, split_date: str = None, **kwargs):
		self.split_date = split_date
		self.company = company
		if constants.PAST_HORIZON in kwargs:
			self.past_horizon = kwargs[constants.PAST_HORIZON]
		else:
			self.past_horizon = {}

		if constants.TRAINING_SAMPLES in kwargs:
			self.training_samples = kwargs[constants.TRAINING_SAMPLES]
		else:
			self.training_samples = 100

		self.is_trained = False

	@abstractmethod
	def train(self, column_wise_series: Dict[str, pd.Series], prediction_window: int) -> None:
		pass

	'''
	:param
	h = The number of days after the split date that you want the forecast for
	
	:return
	pd.Series containing the forecasts indexed by date
	dict containing confidence interval
	
	dict: {
		"95" : [
				lower_bound_series indexed by date,
				upper_bound_series indexed by date
				],
		...
	}
	'''

	@abstractmethod
	def predict(self, h: int, column_wise_series: Dict[str, pd.Series]) -> (pd.Series, Dict):
		pass

	@abstractmethod
	def summary(self):
		pass

	@abstractmethod
	def save(self, pth):
		pass

	def generate_random_dates(self, start_date, end_date, n):
		d1 = datetime.datetime.strptime(start_date, constants.DATE_FORMAT)
		d2 = datetime.datetime.strptime(end_date, constants.DATE_FORMAT)
		r = (d2 - d1).days + 1
		samples = random.sample(range(r), n)
		dates = []
		for sample in samples:
			dates.append(get_date_minus_days(start_date, -sample))

		return dates

	'''
	input:
	cws: column wise series
	prediction_window: for prediction
	
	output: dataset containing 'n' number of samples from given series. where n is self.training_samples
	structure of the output:
	{
		"split_date": {
			"train" : {
				"stock_price" : series of 'past_stock_horizon' days
				"oil_price": series of 'past_oil_horizon' days
			}
			"test" : series of 'prediction_window' days
		...
	} 
	'''
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
				assert False, "{} not found in past horizon hyperparameter".format(key)
			columns_info[key] = self.past_horizon[key]
			max_len = max(max_len, columns_info[key])
			dataFrameList.append(cws[key])

		start_date = cws[constants.STOCK_COLUMN].index[-min_len].strftime(constants.DATE_FORMAT)
		end_date = self.split_date.strftime(constants.DATE_FORMAT)

		dataFrame = pd.concat(dataFrameList, axis=1)

		tts = TrainTestSplit(prediction_window, columns_info, start_date, end_date)
		split_start_date = get_date_minus_days(start_date, -max_len)
		split_end_date = get_date_minus_days(end_date, prediction_window)
		split_dates = self.generate_random_dates(split_start_date, split_end_date, self.training_samples)
		split_data = tts.do_split(dataFrame, split_dates)
		return split_data


class ModelFactory:
	""" The factory class for creating executors"""

	registry = {}
	""" Internal registry for available executors """

	@classmethod
	def create_model(cls, name: str, **kwargs) -> Model:
		""" Factory command to create the executor """

		exec_class = cls.registry[name]
		executor = exec_class(**kwargs)
		return executor

	# end create_executor()

	@classmethod
	def register(cls, name: str) -> Callable:
		def inner_wrapper(wrapped_class: Model) -> Callable:
			if name in cls.registry:
				print('Executor %s already exists. Will replace it', name)
			cls.registry[name] = wrapped_class
			return wrapped_class

		return inner_wrapper


if __name__ == "__main__":
	opt = parse_args()
	pass
