import datetime
import constants



def get_date_minus_days(date: str, days: int):
	start_date = datetime.datetime.strptime(date, constants.DATE_FORMAT)
	stock_days = datetime.timedelta(days)
	return (start_date - stock_days).strftime(constants.DATE_FORMAT)


class Stats:
	def __init__(self):
		self.values = []

	def update(self, value):
		self.values.append(value)

	def get_mean(self):
		if not len(self.values):
			return None

		sum = 0
		for value in self.values:
			sum += value

		return sum/len(self.values)