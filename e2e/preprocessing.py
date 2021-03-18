import argparse
from typing import List, Dict
from abc import abstractmethod
from collections.abc import Callable
import pandas as pd


def parse_args():
	parser = argparse.ArgumentParser()
	return parser.parse_args()


class AbstractPreProcessor:
	def __init__(self):
		pass

	'''
	Takes a list of csv files and returns dict of dataframes keyed by company names.
	For each dataframe we will have a list of columns indexed by dates. Other things like sorting by date, fillna,
	merging dataframe, etc. are included
	
	{
		'Exonn': df,
		'Chevron: df2
	}
	
	 
	'''

	@abstractmethod
	def preprocess(self, csvFiles: List[str]) -> Dict[str, pd.DataFrame]:
		pass

class PreProcessorFactory:
	""" The factory class for creating executors"""

	registry = {}
	""" Internal registry for available executors """

	@classmethod
	def create_preprocessor(cls, name: str, **kwargs) -> AbstractPreProcessor:
		""" Factory command to create the executor """

		exec_class = cls.registry[name]
		print(f'Extracted class: {exec_class}')
		executor = exec_class(**kwargs)
		return executor

	# end create_executor()

	@classmethod
	def register(cls, name: str) -> Callable:
		def inner_wrapper(wrapped_class: AbstractPreProcessor) -> Callable:
			if name in cls.registry:
				print('Executor %s already exists. Will replace it', name)
			cls.registry[name] = wrapped_class
			return wrapped_class

		return inner_wrapper


@PreProcessorFactory.register('smit_preprocessor')
class SmitPreprocessor(AbstractPreProcessor):
	def __init__(self):
		super().__init__()

	def preprocess(self, csvFiles: List[str]):
		print('Proudly inside preprocess')

@PreProcessorFactory.register('hmk_preprocessor')
class HMKPreprocessor(AbstractPreProcessor):
	def __init__(self):
		super().__init__()

	'''
	Takes a list of csv files and returns dict of dataframes keyed by company names.
	For each dataframe we will have a list of columns indexed by dates. Other things like sorting by date, fillna,
	merging dataframe, etc. are included 
	'''

	def preprocess(self, csvFiles: List[str]):
		print('Humbly inside preprocess')
