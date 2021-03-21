import argparse

from e2e import constants
from e2e.models.model import Model
import pandas as pd
from typing import Dict
import json
from utils import Stats
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime


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
        self.evaluation = {}
        self.num_train_days_to_include = self.prediction_window * 5
        now = datetime.datetime.now()
        dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")
        self.folder_name = dt_string

    def getRMSE(self, series1: pd.Series, series2: pd.Series):
        return ((series1 - series2) ** 2).mean() ** .5

    def get_avg_RMSE(self, company_prediction):
        rmse_values = Stats()
        for date in company_prediction:
            output_instance = company_prediction[date]
            rmse = self.getRMSE(output_instance["test_prediction"], output_instance["test_gt"])
            rmse_values.update(rmse)

        avg_rmse = rmse_values.get_mean()
        if avg_rmse is not None:
            return avg_rmse
        else:
            return 0

    def append_train_data(self, test_series, train_series):
        train_series_tail = train_series[-self.num_train_days_to_include:]
        concatenated_series = pd.concat([train_series_tail, test_series])
        return concatenated_series

    def get_plotting_serieses(self, output_instance):
        return_dict = {}

        train_data = output_instance["train_data"]
        test_gt = output_instance["test_gt"]
        test_pred = output_instance["test_prediction"]
        train_pred = output_instance["train_prediction"]

        return_dict["test_pred"] = test_pred
        return_dict["train_pred"] = train_pred[-self.num_train_days_to_include:]

        stock_price_series = self.append_train_data(test_gt, train_data[constants.STOCK_COLUMN][constants.STOCK_COLUMN])
        return_dict[constants.STOCK_COLUMN] = stock_price_series

        if constants.OIL_COLUMN in train_data:
            oil_price_series = train_data[constants.OIL_COLUMN][constants.OIL_COLUMN][-self.num_train_days_to_include:]
            return_dict[constants.OIL_COLUMN] = oil_price_series

        return return_dict

    def create_bar_chart(self, name):
        companies = list(self.evaluation.keys())
        x_pos = [i for i, _ in enumerate(companies)]
        y = [self.evaluation[company][name] for company in companies]

        plt.figure(figsize=(10, 10))
        plt.xlabel("Company")
        plt.ylabel(name)

        plt.bar(x_pos, y, color="blue")
        plt.title("{} for companies".format(name))
        plt.xticks(x_pos, companies)

        plt.setp(plt.gca().get_xticklabels(), rotation=-45, horizontalalignment='left')
        plt.show()

    def get_plot_folder(self, company):
        dir_path = os.path.join("results", self.folder_name, company).replace(" ", "_").replace(":", "-")
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return dir_path

    def create_plots(self):
        os.makedirs(os.path.join("results", self.folder_name))

        for company in self.results:
            for date in self.results[company]:
                output_instance = self.results[company][date]
                plotting_serieses = self.get_plotting_serieses(output_instance)
                fig = plt.figure(figsize=(12, 5))
                plt.xlabel("time")
                plt.title(f"{company}")

                for s in plotting_serieses:
                    ax = plotting_serieses[s].plot(grid=True, label=s)
                    ax.legend(loc=2)

                for conf in output_instance["test_confidence_interval"]:
                    lower_bound = output_instance["test_confidence_interval"][conf][0]
                    upper_bound = output_instance["test_confidence_interval"][conf][1]
                    plt.fill_between(lower_bound.index, lower_bound, upper_bound, alpha=0.2)

                folder = self.get_plot_folder(company)
                file_name = "{}.png".format(date)
                path = os.path.join(folder, file_name)
                path = path.replace(" ", "_").replace(":", "-")
                plt.savefig(path)
                plt.close(fig)

        self.create_bar_chart("RMSE")

    def evaluate(self):
        for company in self.results:
            avg_rmse_error = self.get_avg_RMSE(self.results[company])
            self.evaluation[company] = {}
            self.evaluation[company]["RMSE"] = avg_rmse_error

        print("******** Evalution results ***********")
        print(json.dumps(self.evaluation, indent=4))

        self.create_plots()

    def add(self, model: Model, df_test_ground_truth: Dict[str, pd.Series], df_train: Dict[str, pd.DataFrame]):
        df_test_for_prediction = {}
        for col in df_test_ground_truth:
            if col != constants.STOCK_COLUMN:
                df_test_for_prediction[col] = df_test_ground_truth[col]

        # df_test_ground_truth = pd.DataFrame({constants.STOCK_COLUMN: df_test_ground_truth[constants.STOCK_COLUMN]})
        prediction, confidence_interval = model.predict(self.prediction_window, df_test_for_prediction)
        if model.company not in self.results:
            self.results[model.company] = {}
        test_prediction = None
        train_prediction = None
        assert len(prediction) >= self.prediction_window, "Predicted for less then window size"
        if len(prediction) > self.prediction_window:
            test_prediction = prediction[-self.prediction_window:]
            train_prediction = prediction[:-self.prediction_window]
        else:
            test_prediction = prediction
        self.results[model.company][model.split_date] = {
            "train_data": df_train,
            "test_gt": df_test_ground_truth[constants.STOCK_COLUMN][constants.STOCK_COLUMN],
            "test_prediction": test_prediction,
            "train_prediction": train_prediction,
            "test_confidence_interval": confidence_interval
        }


if __name__ == "__main__":
    opt = parse_args()
    # d = {'p': [1, 10, 4, 5, 5], 'x': [1, 2, 3, 4, 5]}
    # df = pd.DataFrame(d)
    # print(Evaluation(7).getRMSE(df.p, df.x))
    s = pd.Series([0, 1, 2, 3], index=pd.date_range("2000-01-01", "2000-01-04"))
    s2 = pd.Series([1, 2, 3, 4], index=pd.date_range("2000-01-01", "2000-01-04"))
    plt.figure()
    plt.plot(s)

    plt.show()
    pass
