import argparse
from abc import abstractmethod
from typing import List, Dict
import pandas as pd
from collections.abc import Callable


def parse_args():
	parser = argparse.ArgumentParser()
	return parser.parse_args()


class Model(object):
	def __init__(self, company: str = None, split_date: str = None):
		self.split_date = split_date
		self.company = company
		self.is_trained = False

	@abstractmethod
	def train(self, column_wise_series: Dict[str, pd.Series], prediction_window: int) -> None:
		pass

	'''
	:param
	h = The number of days after the split date that you want the forecast for
	
	:return
	pd.Series containing the forecasts indexed by date
	'''

	@abstractmethod
	def predict(self, h: int) -> (pd.Series, Dict):
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


if __name__ == "__main__":
	opt = parse_args()
	pass
