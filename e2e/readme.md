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
    "companies": ["CHEVRON CORPORATION"],
    "preprocessor_name": "stock_news_preprocessor",
    "past_horizon": {
      "stock_price": 200,
      "news_sentiment": 5
    },
    "start_date": "2017-01-01",
    "end_date": "2018-07-31"
  },
  "split_date": ["2018-03-01"],

  "prediction_window": 100,
  "model": {
    "name": "prophet_multifeature_model",
    "hyperparams": {
      "past_horizon": {
        "stock_price": 200,
        "news_sentiment": 5
      }
    }
  },
  "simulator": "S1",
  "simulator_args": {
    "initial_amount": 1000,
    "stock": ["CHEVRON CORPORATION"]
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

## Code Modules

There are five modules in the code.
1. Preprocessor
2. TrainTestSplit
3. Model
4. Evaluation
5. Strategy simulation

Each of the modules are implemented using classes. TrainTestSplit and Evaluation modules only have only one class in it, but other modules have multiple options from which user can choose.    
If user wants to run a model which predicts stock prices only using past stock price values, then user should choose ```stock_news_preprocessor``` and ```prophet_multifeature_model``` , and provide only ```stock_price``` in the ```past_horizon``` parameters.   
Following sections describes about each of the modules. 

### Preprocessor

Possible options:
1. ```stock_preprocessor``` - this preprocessor extracts stock data from csv files. It fills data points for the dates for which csv files didn't have data. For stock price it just takes closing price of yesterday.   
2. ```stock_oil_preprocessor``` - It does the same thing as of ```stock_preprocessor``` but it also extracts oil prices. For this code, we are only considering WTI crude oil prices as one of the factors that affect the stock price.
3. ```stock_news_preprocessor``` - It does the same thing as of ```stock_preprocessor``` but it also extracts news sentiments for each company.
4. ```stock_oil_news_preprocessor``` - It does the same thing as of ```stock_preprocessor``` but it also extracts oil prices and news sentiments for each company. For this code, we are only considering WTI crude oil prices as one of the factors that affect the stock price.

### TrainTestSplit Module

This module splits the dataset into multiple ```(train, test)``` data points. If ```split_date``` list is provided then it splits based on those dates. Otherwise it splits it based on ```split_method```.

### Model

This is a model which will be trained using the data gained from ```TrainTestSplit``` module.    
If one wants to implement a new model class, then one should inherit ```Model``` class and implement, ```train()```, ```test()``` and ```summary()``` methods in it.
Possible model options:
1. ```holt_winters_model``` - Model that implements ```holt_winters``` method of time series prediction on stock price.   
2. ```prophet_model``` - Model that uses ```prophet``` library from Facebook to predict stock prices.
3. ```prophet_multifeature_model``` - model that uses ```prophet``` library from Facebook to predict stock prices by taking news sentiments into account.

### Evaluate

Evaluate module has to method in it: ```add()``` and ```evaluate()```. ```add()``` method is called for all instances of the model and then evaluate method is called at the end of  

### Strategy simulation

This module is used to simulate investment strategies using predicted stock price. There are two methods in this class: ```add()``` and ```simulate()```.   
```add()``` method calls model's predict method to get prediction for next few days and gathers predicted data for a given time period. ```simulate()``` is then called at the end to run a simuation of any investment strategy.   
If one wants to implement a new investment strategy, then one should inherit ```Simulation``` class and implement ```add()``` and ```simulate()``` method of it.   

