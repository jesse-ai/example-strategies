"""
Title: Simple Moving Average Crossover Strategy
Author: FengkieJ (fengkiejunis@gmail.com)
Description: Simple moving average crossover strategy is the ''hello world'' of algorithmic trading.
             This strategy uses two SMAs to determine '''Golden Cross''' to signal for long position,
             and '''Death Cross''' to signal for short position.
"""

from jesse.strategies import Strategy
from jesse.indicators import sma
from jesse import utils

class SMACrossover(Strategy):
    def prepare(self):
        # Setup strategy parameters
        self.vars["slow_sma_period"] = 200
        self.vars["fast_sma_period"] = 50

    @property
    def slow_sma(self):
        return sma(self.candles, self.vars["slow_sma_period"], "close")

    @property
    def fast_sma(self):
        return sma(self.candles, self.vars["fast_sma_period"], "close")

    def should_long(self) -> bool:
        # Golden Cross (reference: https://www.investopedia.com/terms/g/goldencross.asp)
        # Fast SMA above Slow SMA
        return self.fast_sma > self.slow_sma

    def should_short(self) -> bool:
        # Death Cross (reference: https://www.investopedia.com/terms/d/deathcross.asp)
        # Fast SMA below Slow SMA
        return self.fast_sma < self.slow_sma

    def should_cancel(self) -> bool:
        return False

    def go_long(self):
        # Open long position and use entire balance to buy
        qty = utils.size_to_qty(self.capital, self.price)

        self.buy = qty, self.price

    def go_short(self):
        # Open short position and use entire balance to sell
        qty = utils.size_to_qty(self.capital, self.price)

        self.sell = qty, self.price

    def update_position(self):
        # If there exist long position, but the signal shows Death Cross, then close the position, and vice versa.
        if self.is_long and self.should_short():
            self.liquidate()
    
        if self.is_short and self.should_long():
            self.liquidate()
