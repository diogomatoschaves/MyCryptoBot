# Add New Strategies

The tools for backtesting and analysing strategies were turned into their own downloadable package: 
[stratestic](https://github.com/diogomatoschaves/stratestic)

`stratestic` comes as a dependency of this app, and as such its modules can be directly accessed on a `MyCryptoBot`
environment. Please check the documentation of `stratestic` for more details on how to backtest strategies.

However, any new strategy you create will have to be added to this application, so it can be selected in the frontend
when a new trading bot (pipeline) is started. Below it is shown how you'd go about to achieve this.

## Create a new strategy

### Develop a strategy

The `stratestic` module comes with some default strategies ready to be used, but chances are you will want
to create your own strategies. This can be easily achieved by using the template class below, 
which inherits the `StrategyMixin` class:

```python
from collections import OrderedDict
from stratestic.strategies._mixin import StrategyMixin


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

    def __init__(
        self, 
        parameter1: <type>,
        parameter2: <type> = <some_default_value>,
        data=None,
        **kwargs
    ):
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
        self._parameter1 = parameter1  # Each specific parameter that you want to add to the strategy
                                       # must be initalized in this manner, with a _ follwoed by the name 
                                       # of the parameter
        self._parameter2 = parameter2

        self.params = OrderedDict(
            parameter1=lambda x: <type>(x),
            parameter2=lambda x: <type>(x)
        ) 

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
        data["side"] =  # Code to calculate side goes here

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

You would replace `MyStrategy` with the name of your strategy, and replace "Description of my strategy"
with a brief explanation of what your strategy does. 



`__init__()` is where you initialize your strategy parameters. In the case of our example strategy outlined 
above, `parameter1` and `parameter2` would be replaced with the actual names of your strategy's parameter(s), 
and `<type>` would be replaced with the appropriate data types of your parameters. 
This is very important for appropriate type checking on the frontend.

The `params` attribute is an `OrderedDict` that specifies the default parameters for your strategy. 
The key is the parameter name, and the value is a lambda function that converts the user's input
into the appropriate data type.

Finally, we need to call StrategyMixin.__init__(self, data, **kwargs) in order to initialize the parent class.

`update_data()` should contain code to retrieve and prepare the data for your strategy. This is where you can 
add indicators or manipulate the data and create new columns that will then be used to calculate a signal. 
And example if you were developing a momentum strategy would be to calculate the moving average for the selected window.

`calculate_positions()` should contain code to calculate the positions for your strategy based 
on the current data. This is where you input the logic of your strategy in a vectorized way. For the same example 
of the momentum strategy, here you'd add the logic for getting the signal of when it was a BUY or a SELL.

Note that this may not be possible if your strategy is very complex. In that this method can 
be ignored, and only the IterativeBacktester can be used.

`get_signal()` should contain code to generate the signal for a given row of data. The signal 
should be an integer, where -1 represents a short position, 1 represents a long position, 
and 0 represents a neutral position.

**In any case it is highly recommended to check the existing strategies in
[stratestic](https://github.com/diogomatoschaves/stratestic/tree/main/stratestic/strategies) to get a better 
idea on how to implement these methods.**


### Where to save the strategy

The new strategy should be saved in `model/strategies`. If you create subdirectories in this directory (which makes 
sense to keep them organized), then you'll have to import the files into the parent directory. **Again, have a look at
the folder structure in [stratestic](https://github.com/diogomatoschaves/stratestic/tree/main/stratestic/strategies) 
to see how to achieve this.**

If everything goes well, the strategy should become available to be chosen for a new trading bot in the frontend app.
