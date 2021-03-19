import argparse
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt

DATE_ = 'Date2'
DATE = 'Date Value'
PARTITION_DATES = ['2018-01-01', '2018-04-01', '2018-08-01']

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--pth', help='Path to csv containing the stock prices')
	return parser.parse_args()

def get_data_after(df:pd.DataFrame, timestr:str):
	return df[df[DATE_] >= timestr]

def get_data_before(df:pd.DataFrame, timestr:str):
	return df[df[DATE_] < timestr]

def train_and_predict(df:pd.DataFrame, h:int):
	# series = pd.Series(df['Value'].values, index=df[DATE_])
	series = pd.Series(df['Value'].values, index=df.index)
	fit = Holt(pd.Series(df['Value'].values, index=pd.to_datetime(df[DATE_])), damped_trend=False, initialization_method="estimated").fit(optimized=True)

	fcast = fit.forecast(h)
	plt.figure(figsize=(12, 8))
	filtered_series = series[(series.index > '2021-01-01')]
	line_actual, = plt.plot(filtered_series, color='black')
	# line_actual, = plt.plot(series, color='black')
	print(f"fit.fittedvalues: {fit.fittedvalues}")
	filtered = fit.fittedvalues[(fit.fittedvalues.index > '2021-01-01')]
	line_fitted, = plt.plot(filtered, color='blue')

	print(f"fcast: {fcast}")
	fcast_range = pd.date_range(start=df[DATE_].max()+pd.DateOffset(1), end=df[DATE_].max()+pd.DateOffset(h))
	# print(fcast_range)
	fcast.index = fcast_range
	plt.plot(fcast, color='blue')
	plt.legend([line_actual, line_fitted], ['Actual', 'Fitted'])
	# plt.legend([line_actual], ['Actual'])
	plt.show()


def analyze_one_stock(df: pd.DataFrame):
	# pu.do_lineplot(df['Date2'], df['Value'], 'Til', 'x', 'y')
	# df = df[(df['Date2']>='2020-05-01') & (df['Date2']<='2020-05-31')]
	df = get_data_after(df, '2018-01-01')
	train_and_predict(df, 10)

def analyze(pth: str):
	df = pd.read_csv(pth)
	# print(df.head())
	df = df[df['Ticker'] == 'XOM']
	df[DATE] = pd.to_datetime(df[DATE])
	df = df[df['Stock Attribute']=='CLOSING PRICE']
	df = df.sort_values(by=DATE, ascending=True)
	print(df.head())
	print('Before reindc')
	print(df.head(n=20))

	s = pd.DataFrame(
		{DATE: pd.date_range(df[DATE].min(), df[DATE].max(), freq="D")}
	)

	# s["weekday"] = s.StartDate.dt.day_name()

	# s = s.loc[s["weekday"].isin(["Saturday", "Sunday"])]

	df_new = (
		pd.concat([df, s], sort=False)
			.drop_duplicates(keep="first", subset=DATE)
			.sort_values(DATE)
	)

	print('After reindex')
	df_new[DATE_] = df_new[DATE]
	df_new = df_new.set_index(DATE)
	df_new.index.freq = 'd'
	df_new = df_new.fillna(method='ffill')



	print(df_new.head(n=20))

	df[DATE_] = df[DATE]
	df = df.set_index(DATE)

	s1 = df['Value']
	s2 = df_new['Value']

	print(s1)
	print(s2)

	df_new.index.freq = 'd'

	#
	# # print(df.head())
	analyze_one_stock(df_new)



if __name__ == "__main__":
	opt = parse_args()
	analyze(opt.pth)
	pass
