import argparse
from typing import List, Dict, Tuple
from abc import abstractmethod
from collections.abc import Callable
import pandas as pd
import constants
import datetime
from utils import get_date_minus_days


def parse_args():
	parser = argparse.ArgumentParser()
	return parser.parse_args()


class AbstractPreProcessor:
	def __init__(self, **kwargs):
		self.past_horizon = kwargs[constants.PAST_HORIZON]
		self.start_date = kwargs[constants.START_DATE]
		self.end_date = kwargs[constants.END_DATE]
		if constants.COMPANIES in kwargs:
			self.companies = kwargs[constants.COMPANIES]
		else:
			self.companies = None


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
			if self.companies is None or company in self.companies:
				stock_dfs[company] = stock_df.loc[stock_df["stock_name"] == company, [constants.STOCK_COLUMN]]

		for company, df in stock_dfs.items():
			stock_dfs[company] = AbstractPreProcessor.set_missing_dates_ffill(df)

		for company, df in stock_dfs.items():
			val = df[self.start_date:self.start_date]
			assert len(val), company+" stock doesn't have start_date value"

			stock_start_date = get_date_minus_days(self.start_date, self.past_horizon[constants.STOCK_COLUMN])
			val = df[stock_start_date:stock_start_date]
			assert len(val), company+" stock doesn't have start_date-stock_days value"

			val = df[self.end_date:self.end_date]
			assert len(val), company+" stock doesn't have end_date value"

		return stock_dfs

	def read_news_file(self, news_file):
		news_df = pd.read_csv(news_file)
		news_df = news_df.loc[:, ["Date Published", "News Sentiment", "Sentiment Magnitude", "Stock Name"]]
		news_df.columns = ["date", "News Sentiment", "Sentiment Magnitude", "stock_name"]
		news_df["date"] = pd.to_datetime(news_df["date"], format=constants.DATE_FORMAT)
		news_df = news_df.set_index("date")

		news_dfs = {}
		for company in news_df.stock_name.unique():
			# if companies is not defined in the config include all companies
			if self.companies is None or company in self.companies:
				news_dfs[company] = news_df.loc[news_df["stock_name"] == company, ['News Sentiment', 'Sentiment Magnitude']]
				news_dfs[company][constants.NEWS_COLUMN] = news_dfs[company]['News Sentiment']
				news_dfs[company] = news_dfs[company].loc[:, [constants.NEWS_COLUMN]]
				news_dfs[company] = news_dfs[company].sort_index()
				news_dfs[company] = news_dfs[company].resample('D').mean().fillna(method='ffill')

		# Check if all dates are valid or not!
		for company, df in news_dfs.items():
			val = df[self.start_date:self.start_date]
			assert len(val), company+" stock doesn't have start_date value"

			stock_start_date = get_date_minus_days(self.start_date, self.past_horizon[constants.NEWS_COLUMN])
			val = df[stock_start_date:stock_start_date]
			assert len(val), company+" stock doesn't have start_date-stock_days value"

			val = df[self.end_date:self.end_date]
			assert len(val), company+" stock doesn't have end_date value"

		return news_dfs

	def read_commodity_file(self, commodity_file):
		commodity_df = pd.read_csv(commodity_file)
		commodity_df = commodity_df.loc[commodity_df["Commodity And Exchange"] == "WTI CRUDE OIL (DOLLARS PER BARREL)", ["Date Value", "Value"]]
		commodity_df.columns = ["date", constants.OIL_COLUMN]
		commodity_df.date = pd.to_datetime(commodity_df.date)
		commodity_df = commodity_df.set_index('date')
		commodity_df = AbstractPreProcessor.set_missing_dates_ffill(commodity_df)

		val = commodity_df[self.start_date:self.start_date]
		assert len(val), "oil price doesn't have start_date value"

		oil_start_date = get_date_minus_days(self.start_date, self.past_horizon[constants.STOCK_COLUMN])
		val = commodity_df[oil_start_date:oil_start_date]
		assert len(val), "oil price doesn't have start_date-stock_days value"

		val = commodity_df[self.end_date:self.end_date]
		assert len(val), "oil price doesn't have end_date value"

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
				if col == constants.NEWS_COLUMN:
					for past_days in range(1, self.past_horizon[col]+1):
						columns_info[constants.NEWS_LAG_PREFIX+str(past_days)] = self.past_horizon[constants.STOCK_COLUMN]
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
class StockOilPreProcessor(AbstractPreProcessor):
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


@PreProcessorFactory.register('stock_news_preprocessor')
class StockNewsPreProcessor(AbstractPreProcessor):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	'''
	csvFiles: ["stock_exchange.csv", "all_news.csv"]
	'''
	# TODO: exxon is not included in news_file. Please FIX!
	def preprocess(self, csvFiles: List[str]) -> Tuple[Dict[str, pd.DataFrame], Dict]:
		company_wise_dataframes = {}
		stock_file = csvFiles[0]
		news_file = csvFiles[1]
		stock_df = self.read_stock_file(stock_file)
		news_df = self.read_news_file(news_file)



		for company in stock_df:
			for past_days in range(1, self.past_horizon[constants.NEWS_COLUMN]+1):
				# create column for each past_days and subtract the current date and get the fucking value.
				news_df[company][constants.NEWS_LAG_PREFIX+str(past_days)] = news_df[company][constants.NEWS_COLUMN].shift(periods=past_days)
			news_df[company] = news_df[company].dropna()
			# news_df[company] = news_df[company].drop(columns=constants.NEWS_COLUMN)

		for company in stock_df:
			company_wise_dataframes[company] = self.merge_dfs(stock_df[company], news_df[company])

		column_info = self.create_columns_info(company_wise_dataframes)

		

		# with pd.option_context('display.max_rows', 100, 'display.max_columns', 100):
		# 	print(list(company_wise_dataframes.items())[0][1])
		return company_wise_dataframes, column_info


@PreProcessorFactory.register('stock_oil_news_preprocessor')
class StockOilNewsPreProcessor(AbstractPreProcessor):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	'''
	csvFiles: ["stock_exchange.csv", "commodity.csv", "all_company_news.csv"]
	'''

	def read_news_file(self, news_file):
		news_df = pd.read_csv(news_file)
		news_df = news_df.loc[:, ["Date Published", "News Sentiment", "Sentiment Magnitude", "Stock Name"]]
		news_df.columns = ["date", "News Sentiment", "Sentiment Magnitude", "stock_name"]
		news_df["date"] = pd.to_datetime(news_df["date"], format=constants.DATE_FORMAT)
		news_df = news_df.set_index("date")

		news_dfs = {}
		for company in news_df.stock_name.unique():
			# if companies is not defined in the config include all companies
			if self.companies is None or company in self.companies:
				news_dfs[company] = news_df.loc[news_df["stock_name"] == company, ['News Sentiment', 'Sentiment Magnitude']]
				news_dfs[company][constants.NEWS_COLUMN_2] = news_dfs[company]['News Sentiment']*news_dfs[company]['Sentiment Magnitude']
				# news_dfs[company][constants.NEWS_COLUMN_2] = news_dfs[company]['News Sentiment']
				news_dfs[company] = news_dfs[company].loc[:, [constants.NEWS_COLUMN_2]]
				news_dfs[company] = news_dfs[company].sort_index()
				news_dfs[company] = news_dfs[company].resample('D').mean().fillna(method='ffill')

		# Check if all dates are valid or not!
		for company, df in news_dfs.items():
			val = df[self.start_date:self.start_date]
			assert len(val), company+" stock doesn't have start_date value"

			stock_start_date = get_date_minus_days(self.start_date, self.past_horizon[constants.NEWS_COLUMN_2])
			val = df[stock_start_date:stock_start_date]
			assert len(val), company+" stock doesn't have start_date-stock_days value"

			val = df[self.end_date:self.end_date]
			assert len(val), company+" stock doesn't have end_date value"

		return news_dfs

	def preprocess(self, csvFiles: List[str]) -> Tuple[Dict[str, pd.DataFrame], Dict]:

		company_wise_dataframes = {}
		stock_file = csvFiles[0]
		commodity_file = csvFiles[1]
		news_file = csvFiles[2]
		stock_df = self.read_stock_file(stock_file)
		oil_df = self.read_commodity_file(commodity_file)
		news_df = self.read_news_file(news_file)

		for company in stock_df:
			company_wise_dataframes[company] = self.merge_dfs(stock_df[company], oil_df, news_df[company])

		column_info = self.create_columns_info(company_wise_dataframes)
		return company_wise_dataframes, column_info
