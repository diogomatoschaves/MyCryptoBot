# MyCryptoBot

![build_badge](https://github.com/diogomatoschaves/MyCryptoBot/workflows/test-build-data-app/badge.svg)
![build_badge](https://github.com/diogomatoschaves/MyCryptoBot/workflows/test-build-model-app/badge.svg)
![build_badge](https://github.com/diogomatoschaves/MyCryptoBot/workflows/test-build-execution-app/badge.svg)
[![codecov](https://codecov.io/gh/diogomatoschaves/MyCryptoBot/branch/master/graph/badge.svg?token=M1Z50IJEJ3)](https://codecov.io/gh/diogomatoschaves/MyCryptoBot)

<p align="middle">
  <img src="shared/utils/drawings/dashboard.png" style="width: 48%" />
  <img src="shared/utils/drawings/trades.png" style="width: 48%" /> 
</p>

Welcome to the MyCryptoBot repository, a free, open source, and extensible trading platform that utilizes a 
micro-services architecture. The platform empowers you to run your own trading bots and strategies locally 
or in the cloud. At present, the app is integrated with Binance, supporting both the 
[testnet](https://testnet.binancefuture.com) and [live](https://www.binance.com/en/futures) *Futures* 
accounts. Additionally, it features backtesting, plotting, and strategy optimization tools.

*Please note that the contents of this repository are not intended as trading advice or encouragement to 
start trading with real money. This platform is designed to assist existing algo traders/professionals 
in having complete control of their trading strategies and automation. Therefore, it is recommended that 
you only risk money that you are willing to lose.*

## Installation & Usage

The detailed steps for installing and using this application locally and remotely on Heroku are provided in the
[INSTALLATION.md](INSTALLATION.md) file. However, we recommend that you understand the app's structure before 
diving into the installation steps.


## Introduction

The primary goal of this repository is to provide a platform that enables you to deploy your strategies, 
run them locally or on a remote server, and manage all your trading activities with a user-friendly web UI. 
The app comprises three micro-services that are interconnected via a database and served by a frontend web app.
There is a ready-made functionality to deploy the services to Heroku, which will require an account and associated 
monthly costs.

The app's architecture consists of the following:

![MyCryptoBot Architecture](shared/utils/drawings/MyCryptoBot%20architecture.png)

### Data Service

This service acts as the data warehouse of the app. It acquires data from external sources, such as exchanges, 
preprocesses it, and stores it in a database. When a new trading bot is initiated through the user interface, 
a new data pipeline is initiated, fetching live data from the various sources. Whenever a new candle is completed, 
a request is sent to the **Model** app for processing the new data according to the strategy.


### Model Service

The Model service is responsible for processing the data and generating a signal (Buy or Sell) according to the 
selected strategy. Whenever a request is received to generate a new signal, the data is loaded, processed, 
and a signal is produced, which is then sent to the **Order Execution** service with an order to be executed. 
This module also contains development and research tools for backtesting, analyzing, and exploring new strategies. 
For more information on how to use this module and customize your strategies, please refer to the
[MODEL_USAGE.md](MODEL_USAGE.md) file.


### Order Execution Service

The Order Execution service acts as a layer to handle the communication between the app and the exchange. 
It receives buy and sell orders from the **Model** service with a signal, assesses whether an action is required 
(if the received signal differs from the current one), and responds accordingly.


### Web App

The user interface enables the user to start and stop trading bots, view open positions, executed trades, 
statistics, and more. The following are brief descriptions of the various views of the app.


#### Dashboard

#### Trading Bots

#### Positions

#### Trades


## Software Requirements

- [Poetry](https://python-poetry.org/docs/)
- [PostgreSQL](https://www.postgresql.org/download/)
- [Docker](https://docs.docker.com/get-docker/) (For running the app locally.)
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) (For deploying the app to a cloud service.)
