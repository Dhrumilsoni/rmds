import argparse
from model import Model
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

	def __init__(self):
		pass

	def evaluate(self):
		pass

	def add(self, model: Model, df_test_ground_truth: pd.DataFrame, df_train: Dict[str, pd.DataFrame]):
		pass


if __name__ == "__main__":
	opt = parse_args()
	pass
