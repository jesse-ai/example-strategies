"""
Simple Donchian Strategy
Repo: https://github.com/gabrielweich/jesse-strategies
Uses Donchian Channels to capture long term uptrends, the idea is to buy
when price closes above the upperband and only exit the position when
prices closes below the lowerband.
"""

from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils


class Donchian(Strategy):
    @property
    def donchian(self):
        # Previous Donchian Channels with default parameters
        return ta.donchian(self.candles[:-1])

    @property
    def ma_trend(self):
        return ta.sma(self.candles, period=200)

    def filter_trend(self):
        # Only opens a long position when close is above 200 SMA
        return self.close > self.ma_trend

    def filters(self):
        return [self.filter_trend]

    def should_long(self) -> bool:
        # Go long if candle closes above upperband
        return self.close > self.donchian.upperband

    def should_short(self) -> bool:
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
        # Close the position when candle closes below lowerband
        if self.close < self.donchian.lowerband:
            self.liquidate()
