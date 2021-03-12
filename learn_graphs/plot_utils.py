import argparse
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")
plt.rc('xtick', labelsize=15)
plt.rc('ytick', labelsize=15)

def parse_args():
	parser = argparse.ArgumentParser()
	return parser.parse_args()

def do_lineplot(time, value, title:str, xlabel:str, ylabel:str):
	fig, ax = plt.subplots(figsize=(15, 6))
	sns.lineplot(time, value)
	ax.set_title(title, fontsize=20, loc='center', fontdict=dict(weight='bold'))
	ax.set_xlabel(xlabel, fontsize=16, fontdict=dict(weight='bold'))
	ax.set_ylabel(ylabel, fontsize=16, fontdict=dict(weight='bold'))
	plt.tick_params(axis='y', which='major', labelsize=16)
	plt.tick_params(axis='x', which='major', labelsize=16)
	plt.show()

def do_scatter_plot(x, y, title:str, xlabel:str, ylabel:str):
	fig, ax = plt.subplots(figsize=(15, 6))
	sns.scatterplot(x, y)
	ax.set_title(title, fontsize=20, loc='center', fontdict=dict(weight='bold'))
	ax.set_xlabel(xlabel, fontsize=16, fontdict=dict(weight='bold'))
	ax.set_ylabel(ylabel, fontsize=16, fontdict=dict(weight='bold'))
	plt.tick_params(axis='y', which='major', labelsize=16)
	plt.tick_params(axis='x', which='major', labelsize=16)
	plt.show()

if __name__ == "__main__":
	opt = parse_args()
	pass
