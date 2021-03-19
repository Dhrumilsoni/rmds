import argparse
from e2e.model.model import Model
import pandas as pd
from typing import Dict


def parse_args():
	parser = argparse.ArgumentParser()
	return parser.parse_args()


'''
	Final output when evaluate is called. 
	- File structure
		- results
			- company_name
				- prediction_plot_1.png ... prediction_plot_n.png
				- summary.json -> (includes all losses and accuracies and what not)
	- Print average error/acc for each company. 
'''


class Evaluation(object):

	def __init__(self, prediction_window):
		self.prediction_window = prediction_window
		self.results = {}

	def evaluate(self):
		print(self.results)

	def add(self, model: Model, df_test_ground_truth: pd.DataFrame, df_train: Dict[str, pd.DataFrame]):
		prediction, confidence_interval = model.predict(self.prediction_window)
		if model.company not in self.results:
			self.results[model.company] = {}
		self.results[model.company][model.split_date] = {
			"train_data": df_train,
			"test_gt": df_test_ground_truth,
			"test_prediction": prediction
		}



if __name__ == "__main__":
	opt = parse_args()
	pass
