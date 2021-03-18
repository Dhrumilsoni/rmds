import argparse
from model import Model
import pandas as pd


def parse_args():
	parser = argparse.ArgumentParser()
	return parser.parse_args()


class Evaluation(object):

	def __init__(self):
		pass

	'''
	
	'''
	def evaluate(self):
		pass

	def add(self, model: Model, df_test_gt: pd.DataFrame):
		pass

if __name__ == "__main__":
	opt = parse_args()
	pass
