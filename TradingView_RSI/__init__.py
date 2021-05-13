"""
Based on https://www.tradingview.com/script/Ru7qOVtp-RSI-Trend-Crypto/

Default Trading Rules:
Long: RSI crosses over 35
Close Long: RSI crosses under 75
Emergency Exit: RSI crosses under 10
"""

from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils

class TV_RSI(Strategy):

    @property
    def rsi(self):
        return ta.rsi(self.candles, 14, sequential=True)


    def should_long(self):
        qty = utils.size_to_qty(self.capital, self.price, 3, fee_rate=self.fee_rate) 

        if utils.crossed(self.rsi, 35, direction="above") and qty > 0 and self.available_margin > (qty * self.price):
            return True

    def should_short(self):
        return False

    def should_cancel(self):
        return False


    def go_long(self):
        qty = utils.size_to_qty(self.capital, self.price, 3, fee_rate=self.fee_rate) 
        self.buy = qty, self.price
        self.stop_loss = qty, (self.price * .95)        # Willing to lose 5%
        self.take_profit = qty, (self.price * 1.10)     # Take profits at 10%

    def go_short(self):
        pass

    def update_position(self):
        if utils.crossed(self.rsi, 75, direction="below") or  utils.crossed(self.rsi, 10, direction="below"):
            self.liquidate()

