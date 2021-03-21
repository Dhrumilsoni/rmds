# Stock market prediction

This code predicts stock prices for 10 companies in the field of gas and fuel industry, using different datasets and models. It also has strategies for investment based on the model prediction

## Installation

```bash
pip install requirements.txt
```

## Run

To run the code, one needs to execute the following command

```bash
python e2epipline.py --config_pth CONFIG_FILE_PATH
```

The argument to the above code is a config file that controls the execution of the code. Example of the config files are given in the ```configs_dir```

The next section describes how to write a config file.

## Config file

the example of the config file is below:
```json
{
  "preprocessor_args": {
    "csv_files": ["dataset/stock_exchange.csv", "data/all_company_news.csv"],
    "companies": ["MARATHON OIL CORPORATION"],
    "preprocessor_name": "stock_news_preprocessor",
    "past_horizon": {
      "stock_price": 400,
      "news_sentiment": 5
    },
    "start_date": "2017-01-01",
    "end_date": "2018-07-31"
  },
  "split_date": ["2018-03-01"],

  "prediction_window": 100,
  "model": {
    "name": "prophet_model",
    "hyperparams": {
      "damped_trend": true,
      "stock_column_name": "stock_price"
    }
  }
}
```

**preprocessor args** - These are the parameter to control preprocessing of the data.   
**csv_files** - list of files that the preprocessor will use to get the dataset   
**companies** - list of companies/stocks that one wants to consider for prediction   
**preprocessor_name** - the name of the preprocessor class   
**past_horizon** - each attribute in this dictionary will be a feature for predicting the stock price, and value refers to a number of past days that one wants to consider for predicting future stock price.   
**start_date** and **end_date** - time frame for which one wants to use the data. It's in the format of YYYY-MM-DD   
**split_date** - List of dates on which you want to split the dataset. Each date in the list will create one (train, test) data point. Where *train* data point will have the stock price and columns for last ***past_horizon*** days. And *test* will have stock price for *prediction_window* days   
**split_method** - If split date is not provided then code uses **split_method** parameter to split the dataset. Possible values are: ***daily*** - all the days between *start_date* and *end_date* are considered as split_dates, ***bi-monthly*** - two days from each month are selected as *split_date*. If split_method is not provided then ***bi-monthly*** is chosen by default.   
**prediction_window** - Number of days for which model will predict the stock price.
**model** - These are the parameter that represents the model
**name** - Name of the class that implements the model
**hyperparameter** - hyperparams for the model, this will be given to the model during initialization
**past_horizon** - number of days of data in the past that model relies on to predict future stock prices.
**
