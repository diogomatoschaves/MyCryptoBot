# Model Module Usage

The `Model` module is a Python package that provides a framework for backtesting trading
strategies. It contains a collection of pre-implemented trading strategies, as well as
tools for analyzing and visualizing the performance of these strategies.

To use the `Model` module, users can simply import the package and select one of the pre-implemented
strategies to backtest. Alternatively, users can create their own custom strategies by extending
the existing classes and implementing their own methods.

This module provides a convenient and flexible way for users to explore and experiment
with different trading strategies, and to evaluate their performance under different market
conditions. By providing a standardized interface for defining and testing trading strategies,
the Model module makes it easy for users to compare and evaluate different approaches to trading,
and to gain insights into the factors that contribute to successful trading.

Overall, the `Model` module is a powerful tool for anyone interested in developing, testing,
and refining trading strategies, whether for personal use or for professional trading applications.

## Backtesting 

This module offers 2 types of Backtesting - Vectorized and Iterative. Below they are described in more detail
and examples are given. It is also shown how to use the optimization API in order to fine tune the strategies and 
find the best parameters.

### Vectorized Backtesting

Thee `VectorizedBacktester` class is a backtesting framework that allows you to test trading strategies
on historical price data. It has the advantage of being faster than the iterative backtesting, but at
a cost of flexibility, as it will be hard or outright not possible to accomplish this for some more 
complex strategies. For all the strategies provided by this library, vectorized backtesting is supported.

Below is an example of how to use it for the `MovingAverageConvergenceDivergence` strategy:

```python
from model.backtesting import VectorizedBacktester
from model.strategies import MovingAverageCrossover

symbol = "BTCUSDT"
trading_costs = 0.1 # This should be in percentage, i.e. 0.1% 

mov_avg = MovingAverageCrossover(50, 200)

vect = VectorizedBacktester(mov_avg, symbol, amount=1000, trading_costs=trading_costs) # Initializes the IterativeBacktester class with the strategy.
vect.load_data() # Load the default sample data. You can pass your own DataFrame to 'load_data'
vect.run() # Runs the backtest and shows the results
```

This will output the results in textual and graphical form.

```
**************************************************
               BACKTESTING RESULTS                
**************************************************
                     Overview                     
--------------------------------------------------
Total Duration                4 years and 38 weeks
Start Date                     2018-05-23 13:00:00
End Date                       2023-02-13 00:00:00
Trading Costs [%]                              0.1
Leverage [x]                                     1
Initial Equity [USDT]                         1000
Exposed Capital [USDT]                      1000.0
Exposure Time [%]                            100.0
--------------------------------------------------
                     Returns                      
--------------------------------------------------
Total Return [%]                             221.6
Equity Final [USDT]                        3212.75
Equity Peak [USDT]                         5351.51
Annualized Return [%]                        21.49
Annualized Volatility [%]                    73.95
Buy & Hold Return [%]                       175.98
--------------------------------------------------
                    Drawdowns                     
--------------------------------------------------
Max Drawdown [%]                            -61.18
Avg Drawdown [%]                              -8.2
Max Drawdown Duration          1 year and 38 weeks
Avg Drawdown Duration           3 weeks and 2 days
--------------------------------------------------
                      Trades                      
--------------------------------------------------
Total Trades                                   267
Win Rate [%]                                 32.21
Best Trade [%]                               87.77
Worst Trade [%]                             -21.11
Avg Trade [%]                                 0.44
Max Trade Duration              5 weeks and 3 days
Avg Trade Duration             6 days and 11 hours
--------------------------------------------------
                      Ratios                      
--------------------------------------------------
Sharpe Ratio                                  0.07
Sortino Ratio                                 0.28
Calmar Ratio                                  0.35
Profit Factor                                  1.0
Expectancy [%]                                 5.9
System Quality Number                        -0.02
--------------------------------------------------
**************************************************
```

<p align="left">
  <img src="shared/utils/drawings/vectorized_results.png" style="width: 100%" />
</p>

### Iterative Backtesting

The `IterativeBacktester` class is a backtesting framework that allows you to test trading strategies
on historical price data. It works by iterating through each historical data point and simulating
trades based on your strategy. Below is an example of how you would backtest the `MovingAverageCrossover`
strategy. 

```python
from model.backtesting import IterativeBacktester
from model.strategies import MovingAverageConvergenceDivergence

symbol = "BTCUSDT"

macd = MovingAverageConvergenceDivergence(26, 12, 9)

ite = IterativeBacktester(macd, symbol=symbol) # Initializes the VectorizedBacktester class with the strategy
ite.load_data() # Load the default sample data. You can pass your own DataFrame to load_data
ite.run() # Runs the backtest and shows the results
```
This will output the results in textual and graphical form.

```
**************************************************
               BACKTESTING RESULTS                
**************************************************
                     Overview                     
--------------------------------------------------
Total Duration                4 years and 39 weeks
Start Date                     2018-05-16 15:00:00
End Date                       2023-02-13 00:00:00
Trading Costs [%]                              0.0
Leverage [x]                                     1
Initial Equity [USDT]                         1000
Exposed Capital [USDT]                      1000.0
Exposure Time [%]                            100.0
--------------------------------------------------
                     Returns                      
--------------------------------------------------
Total Return [%]                           1614.57
Equity Final [USDT]                       17145.68
Equity Peak [USDT]                        29566.42
Annualized Return [%]                        60.58
Annualized Volatility [%]                    70.99
Buy & Hold Return [%]                       163.16
--------------------------------------------------
                    Drawdowns                     
--------------------------------------------------
Max Drawdown [%]                            -56.09
Avg Drawdown [%]                             -5.46
Max Drawdown Duration          1 year and 22 weeks
Avg Drawdown Duration             1 week and 1 day
--------------------------------------------------
                      Trades                      
--------------------------------------------------
Total Trades                                  3136
Win Rate [%]                                 34.92
Best Trade [%]                               45.61
Worst Trade [%]                             -12.84
Avg Trade [%]                                 0.09
Max Trade Duration             2 days and 14 hours
Avg Trade Duration         13 hours and 15 minutes
--------------------------------------------------
                      Ratios                      
--------------------------------------------------
Sharpe Ratio                                  0.17
Sortino Ratio                                  0.8
Calmar Ratio                                  1.08
Profit Factor                                 1.01
Expectancy [%]                                1.72
System Quality Number                         0.16
--------------------------------------------------
**************************************************
```
<p align="left">
  <img src="shared/utils/drawings/iterative_results.png" style="width: 100%" />
</p>

### Backtesting with Leverage and Margin

Both the Vectorized and Iterative backtesting classes provide users with the ability to incorporate leverage into a 
backtest and visualize the margin ratio as a curve on the results plot. This feature enables users to identify 
instances where a margin call would occur, leading to a potential loss of all funds. The calculations follow the 
rules outlined by Binance, as detailed [here](https://www.binance.com/en/support/faq/how-to-calculate-liquidation-price-of-usd%E2%93%A2-m-futures-contracts-b3c689c1f50a44cabb3a84e663b81d93)
and [here](https://www.binance.com/en/support/faq/leverage-and-margin-of-usd%E2%93%A2-m-futures-360033162192). 
It's important to note that these calculations assume the selected margin is _Isolated_, and the position mode
is _One Way_. To utilize this functionality, follow these steps:

```python
from model.backtesting import VectorizedBacktester
from model.strategies import MovingAverageCrossover

symbol = "BTCUSDT"
trading_costs = 0.05

mov_avg = MovingAverageCrossover(20, 150)

vect = VectorizedBacktester(
    mov_avg,
    symbol,
    amount=10000,
    trading_costs=trading_costs,
    include_margin=True,  # This tells the backtester to include the margin calculations 
    leverage=8  # Here one can choose the desired leverage
)

vect.load_data()
vect.run()
```

This will output the following results and plot:

```
**************************************************
               BACKTESTING RESULTS                
**************************************************
                     Overview                     
--------------------------------------------------
Total Duration                4 years and 38 weeks
Start Date                     2018-05-21 11:00:00
End Date                       2023-02-13 00:00:00
Trading Costs [%]                             0.05
Leverage [x]                                     8
Initial Equity [USDT]                        10000
Exposed Capital [USDT]                      1250.0
Exposure Time [%]                            100.0
--------------------------------------------------
                     Returns                      
--------------------------------------------------
Total Return [%]                          14588.33
Equity Final [USDT]                      192257.96
Equity Peak [USDT]                       330531.27
Annualized Return [%]                       131.49
Annualized Volatility [%]                    71.64
Buy & Hold Return [%]                       1260.2
--------------------------------------------------
                    Drawdowns                     
--------------------------------------------------
Max Drawdown [%]                            -69.84
Avg Drawdown [%]                             -5.98
Max Drawdown Duration          1 year and 38 weeks
Avg Drawdown Duration            1 week and 2 days
--------------------------------------------------
                      Trades                      
--------------------------------------------------
Total Trades                                   406
Win Rate [%]                                 29.31
Best Trade [%]                              519.44
Worst Trade [%]                             -83.34
Avg Trade [%]                                -4.63
Max Trade Duration              3 weeks and 4 days
Avg Trade Duration              4 days and 6 hours
--------------------------------------------------
                      Ratios                      
--------------------------------------------------
Sharpe Ratio                                  0.17
Sortino Ratio                                 0.84
Calmar Ratio                                  0.91
Profit Factor                                 1.07
Expectancy [%]                                4.61
System Quality Number                         0.33
--------------------------------------------------
**************************************************
```
<p align="left">
  <img src="shared/utils/drawings/backtesting_with_margin.png" style="width: 100%" />
</p>

As evident from the results, employing a leverage of `8` led to 3 margin calls during the backtest, 
showing that this particular strategy would have implied a total loss of the funds, unless more margin was
added to the positions. 

#### Calculation the Maximum Allowed Leverage

The backtesting class also offers an API to determine the maximum permissible leverage for a backtest, 
ensuring that the margin ratio remains below a specified threshold. This can be accomplished by following the 
steps outlined in the following example.

```python
from model.backtesting import VectorizedBacktester
from model.strategies import MovingAverageCrossover

symbol = "BTCUSDT"
trading_costs = 0.05

mov_avg = MovingAverageCrossover(20, 50)

vect = VectorizedBacktester(
    mov_avg,
    symbol,
    amount=10000,
    trading_costs=trading_costs,
)

vect.load_data()
vect.maximum_leverage(margin_threshold=0.8)  # The margin threshold will be the maximum margin_ratio allowed during the 
                                             # backtest. If omitted, then the default value of 0.8 is used. Must be 
#                                            # between 0 and 1.
```

Which will output the maximum leverage without a margin call. In the example, it would be:

```shell
Out[2]: 5
```

### Optimization

You can use the optimization API of either the iterative or vectorized backtester in order to find the best combination 
of parameters for a backtest. Below is an example of how to achive this.

```python
from model.backtesting import VectorizedBacktester
from model.strategies import Momentum

symbol = "BTCUSDT"
trading_costs = 0.1

mom = Momentum(30) # Initialize the strategy object with any values. 

vect = VectorizedBacktester(mom, symbol=symbol, trading_costs=trading_costs) # It could also have been the
                                                                             # IterativeBacktester class

vect.load_data() # Load the default sample data. You can pass your own DataFrame to load_data

vect.optimize(dict(window=(40, 90))) # Pass as an argument a dictionary with the parameters as keywords and 
                                     # with a tuple with the limits to test as the value. In this case we are
                                     # testing the strategy with the parameter 'window' between the values of
                                     # 40 and 90

```

This will output the best parameters and show the corresponding results.

<p align="left">
  <img src="shared/utils/drawings/optimization_results.png" style="width: 100%" />
</p>


## Strategies

### Combined Strategies

It is possible to combine 2 or more strategies into one, by means of the `StrategyCombiner` class. The options
for combining the strategies are `Unanimous` or `Majority`. The `Unaninmous` option signals a buy or a sell
if the individual strategy signals all agree (unanimous), whereas the `Majority` method provides a buy a 
or sell signal if the majority of the individual strategy signals points in one direction. 

Here's an example of how that could be achieved:

```python
from model.backtesting import VectorizedBacktester
from model.strategies import MovingAverageCrossover, Momentum, BollingerBands
from model.backtesting.combining import StrategyCombiner

symbol = "BTCUSDT"
trading_costs = 0.1

mov_avg = MovingAverageCrossover(30, 200)
momentum = Momentum(70)
boll_bands = BollingerBands(20, 2)

# The strategies are passed on to StrategyCombiner as list.
combined = StrategyCombiner([mov_avg, momentum, boll_bands], method='Unanimous')

vect = VectorizedBacktester(combined, symbol, amount=1000, trading_costs=trading_costs)
vect.load_data() # Load the default sample data. You can pass your own DataFrame to 'load_data'

vect.run()
```

This strategy combiner class can also be optimized using the same API, with the difference that the 
optimization parameters have to be passed in an array. See the next example:

```python
from model.backtesting import VectorizedBacktester
from model.strategies import MovingAverageCrossover, Momentum
from model.backtesting.combining import StrategyCombiner

symbol = "BTCUSDT"
trading_costs = 0.1

mov_avg = MovingAverageCrossover(30, 200)
momentum = Momentum(70)

# The strategies are passed on to StrategyCombiner as list.
combined = StrategyCombiner([mov_avg, momentum], method='Majority')

vect = VectorizedBacktester(combined, symbol, amount=1000, trading_costs=trading_costs)
vect.load_data() # Load the default sample data. You can pass your own DataFrame to 'load_data'

# The optimization parameters are passed as an array of dictionaries containing the parameter intervals and step
# for each individual strategy.
vect.optimize([dict(sma_s=(20, 40)), dict(window=(60, 80))])
```


### Develop a new strategy

This module comes with some default strategies ready to be used, but chances are you will want
to expand this and create your own strategies. This can be easily achieved by using the template class below, 
which inherits the `StrategyMixin` class:

```python
from collections import OrderedDict
from model.strategies._mixin import StrategyMixin


class MyStrategy(StrategyMixin):
    """
    Description of my strategy

    Parameters
    ----------
    parameter1 : type
        Description of parameter1.
    parameter2 : type, optional
        Description of parameter2, by default default_value.

    Attributes
    ----------
    params : OrderedDict
        Parameters for the strategy, by default {"parameter1": lambda x: x}

    Methods
    -------
    __init__(self, parameter1, parameter2=default_value, **kwargs)
        Initializes the strategy object.
    update_data(self)
        Retrieves and prepares the data.
    calculate_positions(self, data)
        Calculates positions based on strategy rules.
    get_signal(self, row=None)
        Returns signal based on current data.
    """

    def __init__(self, parameter1, parameter2=default_value, data=None, **kwargs):
        """
        Initializes the strategy object.

        Parameters
        ----------
        parameter1 : type
            Description of parameter1.
        parameter2 : type, optional
            Description of parameter2, by default default_value.
        data : pd.DataFrame, optional
            Dataframe of OHLCV data, by default None.
        **kwargs : dict, optional
            Additional keyword arguments to be passed to parent class, by default None.
        """
        self._parameter1 = parameter1
        self._parameter2 = parameter2

        self.params = OrderedDict(parameter1=lambda x: x)

        StrategyMixin.__init__(self, data, **kwargs)

    def update_data(self, data):
        """
        Updates the input data with additional columns required for the strategy.

        Parameters
        ----------
        data : pd.DataFrame
            OHLCV data to be updated.

        Returns
        -------
        pd.DataFrame
            Updated OHLCV data containing additional columns.
        """
        super().update_data(data)

        # Code to update data goes here. Check the given strategies for an example.
        
        return data

    def calculate_positions(self, data):
        """
        Calculates positions based on strategy rules.

        Parameters
        ----------
        data : pd.DataFrame
            OHLCV data.

        Returns
        -------
        pd.DataFrame
            OHLCV data with additional 'position' column containing -1 for short, 1 for long.
        """
        # Code to calculate positions goes here

        return data

    def get_signal(self, row=None):
        """
        Returns signal based on current data.

        Parameters
        ----------
        row : pd.Series, optional
            Row of OHLCV data to generate signal for, by default None.

        Returns
        -------
        int
            Signal (-1 for short, 1 for long, 0 for neutral).
        """
        # Code to generate signal goes here

        return signal

```

You would replace "MyStrategy" with the name of your strategy, and replace "Description of my strategy"
with a brief explanation of what your strategy does. Similarly, "parameter1" and "parameter2" would be
replaced with the names of your strategy's parameters, and "type" would be replaced with the appropriate
data types.

The params attribute is an OrderedDict that specifies the default parameters for your strategy. 
The key is the parameter name, and the value is a lambda function that converts the user's input
into the appropriate data type.

In `__init__()`, you would initialize the strategy object with the appropriate parameters, and 
call StrategyMixin.__init__(self, data, **kwargs) to initialize the parent class.

`update_data()` should contain code to retrieve and prepare the data for your strategy. This 
will depend on the data source you are using. It is advised to check the provided strategies 
to see how this would be done.

`calculate_positions()` should contain code to calculate the positions for your strategy based 
on the current data. This is where you input the logic of your strategy in a vectorized way. 
Note that this may not be possible, depending on your strategy, If that's the case, this method can 
be ignored.

`get_signal()` should contain code to generate the signal for a given row of data. The signal 
should be an integer, where -1 represents a short position, 1 represents a long position, 
and 0 represents a neutrral position.
