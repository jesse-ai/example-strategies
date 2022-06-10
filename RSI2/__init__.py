"""
Connors' RSI2 Strategy
2020-06-27 original implementation - FengkieJ (fengkiejunis@gmail.com)

This strategy is a very basic mean reversion strategy, mainly using RSI(2) overbought and oversold levels to determine entry signals. 
Originally developed by Larry Connors.

Reference: - RSI(2) [ChartSchool]. Retrieved 27 June 2020, from https://school.stockcharts.com/doku.php?id=trading_strategies:rsi2
"""

from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils

class RSI2(Strategy):
    def __init__(self):
        super().__init__()

        self.vars["fast_sma_period"] = 5
        self.vars["slow_sma_period"] = 200
        self.vars["rsi_period"] = 2
        self.vars["rsi_ob_threshold"] = 90
        self.vars["rsi_os_threshold"] = 10

    @property
    def fast_sma(self):
        return ta.sma(self.candles, self.vars["fast_sma_period"])

    @property
    def slow_sma(self):
        return ta.sma(self.candles, self.vars["slow_sma_period"])

    @property
    def rsi(self):
        return ta.rsi(self.candles, self.vars["rsi_period"])

    def should_long(self) -> bool:
        # Enter long if current price is above sma(200) and RSI(2) is below oversold threshold
        return self.price > self.slow_sma and self.rsi <= self.vars["rsi_os_threshold"]

    def should_short(self) -> bool:
        # Enter long if current price is below sma(200) and RSI(2) is above oversold threshold
        return self.price < self.slow_sma and self.rsi >= self.vars["rsi_ob_threshold"]

    def should_cancel_entry(self) -> bool:
        return False

    def go_long(self):
        # Open long position and use entire balance to buy
        qty = utils.size_to_qty(self.balance, self.price, fee_rate=self.fee_rate)

        self.buy = qty, self.price

    def go_short(self):
        # Open short position and use entire balance to sell
        qty = utils.size_to_qty(self.balance, self.price, fee_rate=self.fee_rate)

        self.sell = qty, self.price

    def update_position(self):
        # Exit long position if price is above sma(5)
        if self.is_long and self.price > self.fast_sma:
            self.liquidate()
    
        # Exit short position if price is below sma(5)
        if self.is_short and self.price < self.fast_sma:
            self.liquidate()
