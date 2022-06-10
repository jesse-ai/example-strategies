"""
MACD indicator with 100 period exponential moving average (EMA)
Timeframe: 1h
Repo: https://github.com/gabrielweich/jesse-strategies
When the MACD line crosses the signal line AND the closing price of the last candle is above 
the 100 period EMA a long order is placed. The script has been seet up to use the built in 
optimization, but the optimization was never completed due to lack of processing power. 
Change the default values in the hyperparameters function to manually tune parameters.
"""

"""
author      = "Connor McDonald"
copyright   = "Free For Use"
version     = "1.0"
email       = "connormcd98@gmail.com"
"""

from jesse.strategies import Strategy, cached
import jesse.indicators as ta
from jesse import utils



class MACD_EMA(Strategy):
    @property
    def macd(self): #this returns: macd, signal and hist which can be referenced as self.macd[0], self.macd[1] and self.macd[2], respectively
        return ta.macd(self.candles, self.hp['fastperiod'],self.hp['slowperiod'],self.hp['signalperiod'])

    @property
    def ema(self): #this returns a single value which is the 100EMA at the latest candle
        return ta.ema(self.candles, self.hp['ema'])

    def should_long(self):
        # return true if close is above EMA and MACD line is above signal line
        if self.close > self.ema and self.macd[0] > self.macd[1]:
            return True
        return False

    def should_short(self):
        return False

    def should_cancel_entry(self) -> bool:
        return True
        

    def go_long(self):
        # Open long position using entire balance
        qty = utils.size_to_qty(self.balance, self.price, fee_rate=self.fee_rate)
        self.buy = qty, self.price

    def go_short(self):
        pass


    def update_position(self):
        # Close the position when MACD crosses below the signal line and closing prices is less than 100EMA
        if self.macd[0] < self.macd[1] and self.close < self.ema:
            self.liquidate()



    def hyperparameters(self): # This is set up for optimization but if you just want to backtest with your own values then change the default value only.
        return [
            {'name': 'ema', 'type': int, 'min': 50, 'max': 200, 'default': 100},
            {'name': 'fastperiod', 'type': int, 'min': 10, 'max': 18, 'default': 12},
            {'name': 'slowperiod', 'type': int, 'min': 19, 'max': 36, 'default': 26},
            {'name': 'signalperiod', 'type': int, 'min': 3, 'max': 9, 'default': 9},
        ]
