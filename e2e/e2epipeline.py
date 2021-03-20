import argparse
from preprocessing import PreProcessorFactory
from e2e.models.model import ModelFactory
from train_test_split import TrainTestSplit
from evaluation import Evaluation
import constants
import json


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_pth', help='Path to the config file')
    return parser.parse_args()


def main(config_pth: str):
    with open(config_pth, 'r') as f:
        config = json.load(f)

    preprocessor = PreProcessorFactory.create_preprocessor(config[constants.PREPROCESSOR_ARGS][constants.PREPROCESSOR_NAME],
                                                           **config[constants.PREPROCESSOR_ARGS])
    company_wise_dataframes, columns_info = preprocessor.preprocess(config[constants.PREPROCESSOR_ARGS][constants.CSV_FILES])

    # print(company_wise_dataframes)
    # print(columns_info)
    if "split_method" in config:
        split_method = config["split_method"]
    else:
        split_method = "bi-monthly"

    tts = TrainTestSplit(config[constants.PREDICTION_WINDOW], columns_info, config[constants.PREPROCESSOR_ARGS][constants.START_DATE], config[constants.PREPROCESSOR_ARGS][constants.END_DATE], split_method=split_method)
    evaluation = Evaluation(config[constants.PREDICTION_WINDOW])

    if "split_date" not in config:
        split_dates = None
    else:
        split_dates = config["split_date"]

    for company, df in company_wise_dataframes.items():
        date_splits = tts.do_split(df, split_dates)
        for date, train_test_data in date_splits.items():
            df_train = train_test_data[constants.TRAIN]
            df_test = train_test_data[constants.TEST]

            # model_args = {'split_date': date, 'company': company, 'hyperparams': config[constants.MODEL][constants.HYPERPARAMS]}
            hyperparams = config[constants.MODEL][constants.HYPERPARAMS]
            model = ModelFactory.create_model(config[constants.MODEL][constants.NAME],
                                              split_date=date, company=company, **hyperparams)
            model.train(df_train, config[constants.PREDICTION_WINDOW])
            # model.summary()
            evaluation.add(model, df_test, df_train)
    evaluation.evaluate()


if __name__ == "__main__":
    opt = parse_args()
    main(opt.config_pth)
    pass
