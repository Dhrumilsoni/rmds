import argparse
from abc import abstractmethod
from typing import List, Dict
import pandas as pd


def parse_args():
	parser = argparse.ArgumentParser()
	return parser.parse_args()


class TrainTestSplit(object):
	def __init__(self, prediction_window, columns_info):
		self.prediction_window = prediction_window
		self.columns_info = columns_info

	'''
	Takes a dict of pre-processed pandas dataframe and for each dataframe in the list and outputs a dict with all
	keys present in the input dict. For each key, the value will again be a dict.....
	
	{
		'2020-01-04': {
		'train': df1,
		'test': df2
		}
		...
	} 
	'''

	def do_split(self, df: Dict[str, pd.DataFrame], split_dates: List[str] = None):
		pass


if __name__ == "__main__":
	opt = parse_args()
	pass
