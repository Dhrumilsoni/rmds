import argparse
import pandas as pd
from datetime import datetime
import plot_utils
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller, kpss, acf, grangercausalitytests
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf,month_plot,quarter_plot
from scipy import signal
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--pth', help='Path to the file')
	return parser.parse_args()


def fix_time(x: str):
	if x.startswith('Mar') or x.startswith('Jun') or x.startswith('Sep') or x.startswith('Dec'):
		return x
	else:
		temp = x.split('-')
		return temp[1] + '-0' + temp[0]


def read_processed_data(pth):
	data = pd.read_csv(pth)
	data['Date'] = data['Date'].apply(fix_time)
	conv = lambda x: datetime.strptime(x, "%b-%y")
	data['Date'] = data['Date'].apply(conv)
	data['Date'] = pd.to_datetime(data['Date'])
	data['year'] = data['Date'].dt.year
	data['month'] = data['Date'].dt.month
	data = data.set_index('Date')
	return data

def do_analysis(data: pd.DataFrame):
	# plot_utils.do_lineplot(data['Date'], data['Sales'], 'Quarterly Sales data', 'Date', 'Sales')
	# plot_utils.do_lineplot(data['Date'], data['AdBudget'], 'AdBudget quarterly', 'Date', 'Budget')
	# adbudget = data['AdBudget']
	sales = data['Sales']
	# plot_utils.do_scatter_plot(adbudget, sales, 'scatter plot for adbudget vs sales', 'Sales', 'AdBudget')
	# print(f"Correlation coeffcient is: {adbudget.corr(sales)}")
	sd = data[['Sales']]
	# print(sd.info())
	# sd.plot(x='Date')
	# plt.show()
	result = seasonal_decompose(sd)
	print(result.resid.mean())
	result.plot()
	plt.show()


if __name__ == "__main__":
	opt = parse_args()
	data = read_processed_data(opt.pth)
	do_analysis(data)
