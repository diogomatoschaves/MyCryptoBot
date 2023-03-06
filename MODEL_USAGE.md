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

<p align="left">
  <img src="shared/utils/drawings/backtest-plot" style="width: 60%" />
</p>

This module offers 2 types of Backtesting - Vectorized and Iterative. Below they are described in more detail
and an example usage is given.

### Vectorized Backtesting

Thee `VectorizedBacktester` class is a backtesting framework that allows you to test trading strategies
on historical price data. It has the advantage of being faster than the iterative backtesting, but at
a cost of flexibility, as it will be hard or outright not possible to accomplish this for some more 
complex strategies. For all the strategies provided by this library, vectorized backtesting is supported.

Below is an example of how to use it for the `MovingAverageConvergenceDivergence` strategy:

```python
from model.backtesting import VectorizedBacktester
from model.strategies import MovingAverageConvergenceDivergence

symbol = "BTCUSDT"
trading_costs = 0.1 # This should be in percentage, i.e. 0.1% 

macd = MovingAverageConvergenceDivergence(26, 12, 9)

vect = VectorizedBacktester(macd, symbol=symbol, trading_costs=trading_costs) # Initializes the VectorizedBacktester class with the strategy
vect.load_data() # Load the default sample data. You can pass your own DataFrame to load_data
vect.run() # Runs the backtest and shows the results
```

### Iterative Backtesting

The `IterativeBacktester` class is a backtesting framework that allows you to test trading strategies
on historical price data. It works by iterating through each historical data point and simulating
trades based on your strategy. Below is an example of how you would backtest the `MovingAverageCrossover`
strategy. 

```python
from model.backtesting import IterativeBacktester
from model.strategies import MovingAverageCrossover

symbol = "BTCUSDT"

mov_avg = MovingAverageCrossover(50, 200)

ite = IterativeBacktester(mov_avg, symbol, amount=1000) # Initializes the IterativeBacktester class with the strategy.
ite.load_data() # Load the default sample data. You can pass your own DataFrame to 'load_data'
ite.run() # Runs the backtest and shows the results
```

## Strategies

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
    _calculate_positions(self, data)
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

    def _calculate_positions(self, data):
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

`_calculate_positions()` should contain code to calculate the positions for your strategy based 
on the current data. This is where you input the logic of your strategy in a vectorized way. 
Note that this may not be possible, depending on your strategy, If that's the case, this method can 
be ignored.

`get_signal()` should contain code to generate the signal for a given row of data. The signal 
should be an integer, where -1 represents a short position, 1 represents a long position, 
and 0 represents a neutrral position.
