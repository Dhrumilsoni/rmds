import argparse
from abc import abstractmethod
from typing import List, Dict
import pandas as pd
import datetime
import constants
import random
from calendar import monthrange
from utils import get_date_minus_days
import copy


def parse_args():
	parser = argparse.ArgumentParser()
	return parser.parse_args()


def increment_month(date):
	if date.month < 12:
		date = date.replace(month=date.month + 1)
	else:
		date = date.replace(year=date.year + 1, month=1)
	return date


def get_two_dates_in_a_month(start_date):
	first_date = random.randint(1, 15)
	second_date = first_date + random.randint(13, 15)

	while second_date > monthrange(start_date.year, start_date.month)[1]:
		second_date -= 1

	first_date = start_date.replace(day=first_date)
	second_date = start_date.replace(day=second_date)
	return first_date, second_date


class TrainTestSplit(object):

	def __init__(self, prediction_window, columns_info, start_date: str, end_date: str, split_method = "bi-monthly"):
		self.prediction_window = prediction_window
		self.columns_info = columns_info

		self.split_dates = []
		start_date = datetime.datetime.strptime(start_date, constants.DATE_FORMAT)
		start_date = start_date.replace(day=1)
		end_date = datetime.datetime.strptime(end_date, constants.DATE_FORMAT)

		if split_method == 'daily':
			self.split_dates_daily(start_date, end_date)
		else:
			self.split_dates_bimonthly(start_date, end_date)

	def split_dates_bimonthly(self, start_date, end_date):
		while start_date < datetime.datetime.strptime(
				get_date_minus_days(end_date.strftime(constants.DATE_FORMAT), self.prediction_window),
				constants.DATE_FORMAT):
			first_date, second_date = get_two_dates_in_a_month(start_date)
			if first_date < datetime.datetime.strptime(
					get_date_minus_days(end_date.strftime(constants.DATE_FORMAT), self.prediction_window),
					constants.DATE_FORMAT):
				self.split_dates.append(first_date)
			if second_date < datetime.datetime.strptime(
					get_date_minus_days(end_date.strftime(constants.DATE_FORMAT), self.prediction_window),
					constants.DATE_FORMAT):
				self.split_dates.append(second_date)

			# Incrementing months over time
			start_date = increment_month(start_date)

	def split_dates_daily(self, start_date, end_date):
		while start_date < datetime.datetime.strptime(
				get_date_minus_days(end_date.strftime(constants.DATE_FORMAT), self.prediction_window),
				constants.DATE_FORMAT):

			self.split_dates.append(start_date)

			# Increment day over time
			start_date = datetime.datetime.strptime(get_date_minus_days(start_date.strftime(constants.DATE_FORMAT), -1), constants.DATE_FORMAT)

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

	df1 structure(Dict):
	{
		'stock_price': pd.DataSeries(Date->val)
		...
	}
		

	df2 structure(pd.Series):
		Columns -> Date, Stock Price

	'''
	'''
		Set the start month as the first month of 2017 and end month as last month of 2020
		for each month,
			get a random number from 1-15 and pick a random from [13,14,15]
			set the first date as the first random and second as first+the second one if feasible
			append all these dates in a list
		for each date,
			get the data from the past according to the columns_info and make a dict similar to columns_info but, 
			with data instead of length.
		return dict of these dicts with keys as dates
	'''

	def do_split(self, df: pd.DataFrame, split_dates: List[str] = None):
		if not split_dates:
			split_dates = self.split_dates
		else:
			split_dates = [datetime.datetime.strptime(split_date, constants.DATE_FORMAT) for split_date in split_dates]

		return_data = {}
		for split_date in split_dates:
			splitted_data = {}
			for columns in self.columns_info:
				splitted_data[columns] = df[get_date_minus_days(split_date.strftime(constants.DATE_FORMAT),
																self.columns_info[columns] - 1): split_date.strftime(
					constants.DATE_FORMAT)].loc[:, [columns]]

			test_data = {}
			test_data[constants.STOCK_COLUMN] = df[get_date_minus_days(split_date.strftime(constants.DATE_FORMAT), -1): get_date_minus_days(
				split_date.strftime(constants.DATE_FORMAT), -self.prediction_window)].loc[:, [constants.STOCK_COLUMN]]
			for col in range(1, len([1 for c_name in self.columns_info.keys() if constants.NEWS_LAG_PREFIX==c_name[:len(constants.NEWS_LAG_PREFIX)]])+1):
				col_name = constants.NEWS_LAG_PREFIX+str(col)
				test_data[col_name] = df[get_date_minus_days(split_date.strftime(constants.DATE_FORMAT),
																		   -1): get_date_minus_days(
					split_date.strftime(constants.DATE_FORMAT), -self.prediction_window)].iloc[:col , [list(df.columns).index(col_name)]]


			return_data[split_date] = {
				'train': splitted_data,
				'test': test_data
			}

		return return_data


if __name__ == "__main__":
	opt = parse_args()
