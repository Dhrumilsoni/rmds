import argparse
from typing import List, Dict, Tuple
from abc import abstractmethod
from collections.abc import Callable
import pandas as pd
import constants
import datetime


def parse_args():
	parser = argparse.ArgumentParser()
	return parser.parse_args()


def get_date_minus_days(date: str, days: int):
	start_date = datetime.datetime.strptime(date, constants.DATE_FORMAT)
	stock_days = datetime.timedelta(days)
	return (start_date - stock_days).strftime(constants.DATE_FORMAT)


class AbstractPreProcessor:
	def __init__(self, **kwargs):
		self.past_horizon = kwargs[constants.PAST_HORIZON]
		self.start_date = kwargs[constants.START_DATE]
		self.end_date = kwargs[constants.END_DATE]

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
	def preprocess(self, csvFiles: List[str]) -> Tuple[Dict[str, pd.DataFrame], Dict]:
		pass

	def set_missing_dates_ffill(df: pd.DataFrame) -> pd.DataFrame:
		date_range = pd.date_range(min(df.index), max(df.index))
		df = df.reindex(date_range)
		df = df.fillna(method='ffill')
		return df

	def read_stock_file(self, stock_file):
		stock_df = pd.read_csv(stock_file)
		stock_df = stock_df.loc[:, ["Date Value", "Value", "Stock Name"]]
		stock_df.columns = ["date", constants.STOCK_COLUMN, "stock_name"]
		stock_df["date"] = pd.to_datetime(stock_df["date"], format=constants.DATE_FORMAT)
		stock_df = stock_df.set_index("date")

		stock_dfs = {}
		for company in stock_df.stock_name.unique():
			stock_dfs[company] = stock_df.loc[stock_df["stock_name"] == company, [constants.STOCK_COLUMN]]

		for company, df in stock_dfs.items():
			stock_dfs[company] = AbstractPreProcessor.set_missing_dates_ffill(df)

		# for company, df in stock_dfs.items():
			# print(df.index[0])
			# print(pd.to_datetime('1997-08-01', format=constants.DATE_FORMAT))
			# print(df[str(pd.to_datetime('1997-08-01', format=constants.DATE_FORMAT))])
			# # print(df.index.dtype)
			# try:
			# 	print(self.start_date)
			# 	val = df.loc[self.start_date, 'date']
			# except KeyError:
			# 	assert False, company+" stock doesn't have start_date value"

			#
			# val = df.date.get(get_date_minus_days(self.start_date, self.past_horizon[constants.STOCK_COLUMN]), None)
			# assert val, company+" stock doesn't have start_date-stock_days value"
			#
			# val = df.date.get(self.end_date, None)
			# assert val, company+" stock doesn't have end_date value"

		return stock_dfs

	def read_commodity_file(self, commodity_file):
		commodity_df = pd.read_csv(commodity_file)
		commodity_df = commodity_df.loc[commodity_df["Commodity And Exchange"] == "WTI CRUDE OIL (DOLLARS PER BARREL)", ["Date Value", "Value"]]
		commodity_df.columns = ["date", constants.OIL_COLUMN]
		commodity_df.date = pd.to_datetime(commodity_df.date)
		commodity_df = commodity_df.set_index('date')
		commodity_df = AbstractPreProcessor.set_missing_dates_ffill(commodity_df)

		# val = commodity_df.date.get(self.start_date, None)
		# assert val, "oil price doesn't have start_date value"
		#
		# val = commodity_df.date.get(get_date_minus_days(self.start_date, self.past_horizon[constants.STOCK_COLUMN]), None)
		# assert val, "oil price doesn't have start_date-stock_days value"
		#
		# val = commodity_df.date.get(self.end_date, None)
		# assert val, "oil price doesn't have end_date value"

		return commodity_df

	def merge_dfs(self, *args):
		merged_df = args[0]
		for df in args[1:]:
			merged_df = merged_df.join(df, how='inner')

		return merged_df

	def create_columns_info(self, company_wise_df):
		columns_info = {}
		company_df = company_wise_df[list(company_wise_df.keys())[0]]
		if self.past_horizon:
			for col in self.past_horizon:
				if col in company_df.columns:
					columns_info[col] = self.past_horizon[col]

		return columns_info



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


@PreProcessorFactory.register('stock_preprocessor')
class StockPreProcessor(AbstractPreProcessor):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	'''
	csvFiles: ["golbal_stock_exchange_data.csv"]
	'''
	def preprocess(self, csvFiles: List[str]) -> Tuple[Dict[str, pd.DataFrame], Dict]:

		stock_file = csvFiles[0]
		self.read_stock_file(stock_file)
		comapny_wise_dfs = self.read_stock_file(stock_file)
		column_info = self.create_columns_info(comapny_wise_dfs)
		return comapny_wise_dfs, column_info


@PreProcessorFactory.register('stock_oil_preprocessor')
class StockPreProcessor(AbstractPreProcessor):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	'''
	csvFiles: ["stock_exchange.csv", "commodity.csv"]
	'''

	def preprocess(self, csvFiles: List[str]) -> Tuple[Dict[str, pd.DataFrame], Dict]:

		company_wise_dataframes = {}
		stock_file = csvFiles[0]
		commodity_file = csvFiles[1]
		stock_df = self.read_stock_file(stock_file)
		oil_df = self.read_commodity_file(commodity_file)

		for company in stock_df:
			company_wise_dataframes[company] = self.merge_dfs(stock_df[company], oil_df)

		column_info = self.create_columns_info(company_wise_dataframes)
		return company_wise_dataframes, column_info
