import argparse
from abc import abstractmethod
from typing import List, Dict
import pandas as pd
from collections.abc import Callable
from statsmodels.tsa.api import Holt
from statsmodels.tsa.holtwinters.results import HoltWintersResults


def parse_args():
	parser = argparse.ArgumentParser()
	return parser.parse_args()


class Model(object):
	def __init__(self, company: str = None, split_date: str = None):
		self.split_date = split_date
		self.company = company
		self.is_trained = False

	@abstractmethod
	def train(self, column_wise_series: Dict[str, pd.Series]) -> None:
		pass

	'''
	:param
	h = The number of days after the split date that you want the forecast for
	
	:return
	pd.Series containing the forecasts indexed by date
	'''

	@abstractmethod
	def predict(self, h: int) -> pd.Series:
		pass

	@abstractmethod
	def summary(self):
		pass

	@abstractmethod
	def save(self, pth):
		pass


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


@ModelFactory.register('test_model')
class TestModel(Model):
	def __init__(self, split_date: str, company: str, hyperparams: Dict):
		self.split_date = split_date
		self.company = company
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

	def predict(self, h: int) -> pd.Series:
		fcast = self.model_instance.forecast(h)
		return fcast

	def summary(self):
		print(self.model_instance.summary())

	def save(self, pth):
		pass


if __name__ == "__main__":
	opt = parse_args()
	pass
