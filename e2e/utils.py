import datetime
import constants



def get_date_minus_days(date: str, days: int):
	start_date = datetime.datetime.strptime(date, constants.DATE_FORMAT)
	stock_days = datetime.timedelta(days)
	return (start_date - stock_days).strftime(constants.DATE_FORMAT)
