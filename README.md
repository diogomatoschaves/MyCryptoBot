# MyCryptoBot

![build_badge](https://github.com/diogomatoschaves/MyCryptoBot/workflows/test-build-data-app/badge.svg)
![build_badge](https://github.com/diogomatoschaves/MyCryptoBot/workflows/test-build-model-app/badge.svg)
![build_badge](https://github.com/diogomatoschaves/MyCryptoBot/workflows/test-build-execution-app/badge.svg)
[![codecov](https://codecov.io/gh/diogomatoschaves/MyCryptoBot/branch/master/graph/badge.svg?token=M1Z50IJEJ3)](https://codecov.io/gh/diogomatoschaves/MyCryptoBot)

Welcome! This is your starting point to the awesome `MyCryptoBot` repository,
an extendable trading platform with a micro-services architecture that enables
you to set up your own infrastructure in the cloud,
deploy your great trading strategies and hopefully see your net value increase!


**Disclaimer**: *This repository should in no way whatsoever be viewed as trading
advice or encouragement to start trading with real money. This is a platform
to help existing algo traders / professionals to have full control of their trading strategies
and their automation.*


## Installation & Usage

The steps to install and use this application locally as well as remotely (on Heroku) are described in detail 
in [INSTALLATION.md](INSTALLATION.md). However, it is recommended to understand how the app is structured 
before you delve deeper into the installation steps, which is provided below.


## Introduction

The main goal of this repository is to provide a platform that enables you to deploy your strategies, run them on a
remote server and manage all your trading activities with the help of a simple user interface.

The app is composed of 3 different micro-services, interconnected together by a database and served by a frontend
web app. There is ready-made functionality to deploy the services to *Heroku* (which will require an account and 
some associated monthly cost).

The architecture of the app is as follows:

![MiCrypto Architecture](shared/utils/drawings/MiCrypto%20architecture.png)

### Data Service

This service consists on the data warehouse of the app. Here, data is acquired from
external sources (exchanges, twitter, etc), is pre-processed and stored onto a
database. When a new trading bot is started through the user interface, a new data pipeline is started, fetching live
data from the different sources and, whenever a new candle is completed, a request is then sent
to the **Model** app for processing the new data according to the strategy.


### Model Service


The Model service is where the data is processed, and a signal (Buy or Sell) is generated according to the
selected strategy. Whenever a request is received to generate a new signal, the data is loaded, processed,
and a signal comes as the output, which is then sent to the **Order Execution** service with an order to be executed.

This module also contains development and research tools for backtesting, analyzing and explore new strategies. 
For more information on how to use this module, go to [DEVELOPMENT.md](DEVELOPMENT.md).

### Order Execution Service

The Order Execution service acts a layer to handle the communication between the app and the exchange.
It receives buy and sell orders from the **Model** service with a signal, assesses if an action is needed (if the received signal
is different from the current one), and acts accordingly.


### Web App

This is a user interface, from which the user can start and stop trading bots, see open positions, performed trades,
statistics, etc.
