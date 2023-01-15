# MyCryptoBot

Welcome! This is your starting point to the awesome MyCryptoBot repository,
an extendable trading platform with a micro-services architecture that enables
you to set up your own infrastructure in the cloud, 
deploy your great trading strategies and hopefully see your net value increase!


DISCLAIMER:

This repository should in no way whatsoever be viewed as trading 
advice or encouragement to start trading with real money. This is a platform 
to help existing algo traders / professionals to have full control of their trading strategies
and their automation. 


## Introduction

The main goal of this repository is to provide a platform that enables you to deploy your strategies, run them on a 
remote server and manage all your trading action with the help of a simple user interface. However, in order to achieve
this there are some steps to be followed and configurations to be made for installing it properly. Therefore, there is 
not a *quick usage* section, as the setup is somewhat involved. It helps to understand the architecture of the app 
before delving into the setup, so that's where we'll start.

The app is composed of 3 different micro-services, interconnected together by a database and served by a frontend 
React app. There is ready-made functionality to deploy the services to *Heroku* (which requires an account). 

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


### Order Execution Service

The Order Execution service acts a layer to handle the communication between the app and the exchange.
It receives buy and sell orders from the **Model** service with a signal, assesses if an action is needed (if the received signal
is different from the current one), and acts accordingly. 


### Web App

This is a user interface, from which the user can start and stop trading bots, see open positions, performed trades, 
statistics, etc. 

#### Dashboard



## Usage


In order to use the app in its most basic form, you'll need to setup a Heroku account (if you don't have one yet) at 
[Heroku](https://www.heroku.com)