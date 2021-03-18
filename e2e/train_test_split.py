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
		'train': Dict[str, pd.DataSeries],
		'test': df2
		}
		...
	} 

	df1 structure:
	{
		'stock_price': pd.DataSeries(Date->val)
		...
	}
		

	df2 structure:
		Columns -> Date, Stock Price

	'''

	def do_split(self, df: Dict[str, pd.DataFrame], split_dates: List[str] = None):
		if not split_dates:
			pass
			'''
				(for oil, stock and news columns, see if they exist)

				Set the start month as the first month of 2017 and end month as last month of 2020
				for each month,
					get a random number from 1-15 and pick a random from [13,14,15]
					set the first date as the first random and second as first+the second one if feasible
					append all these dates in a list
				for each date,
					get the data from the past according to the columns_info and make a dict similar to columns_info but, 
					with data instead of length.
				return the dict man return the dict
			'''
			

		else:
			# not supporting split_dates. YET TO BE ADDED.
			pass


if __name__ == "__main__":
	opt = parse_args()
	pass
