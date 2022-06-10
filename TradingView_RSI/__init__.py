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

class TradingView_RSI(Strategy):

    def hyperparameters(self):
        return [
                {'name':'rsi', 'type': int, 'min': 10, 'max':30, 'default': 5},
                {'name':'stop_loss', 'type': float, 'min': .5, 'max': .99, 'default': .95},
                {'name':'take_profit', 'type': float, 'min': 1.1, 'max': 1.2, 'default': 1.1},
                {'name':'xparam', 'type':int, 'min': 60, 'max': 90, 'default': 75}
        ]

    @property
    def rsi(self):
        return ta.rsi(self.candles, self.hp['rsi'], sequential=True)


    def should_long(self):
        qty = utils.size_to_qty(self.balance, self.price, 3, fee_rate=self.fee_rate) 

        if utils.crossed(self.rsi, 35, direction="above") and qty > 0 and self.available_margin > (qty * self.price):
            return True

    def should_short(self):
        return False

    def should_cancel_entry(self):
        return False


    def go_long(self):
        qty = utils.size_to_qty(self.balance, self.price, 3, fee_rate=self.fee_rate) 
        self.buy = qty, self.price
        self.stop_loss = qty, (self.price * self.hp['stop_loss'])        # Willing to lose 5%
        self.take_profit = qty, (self.price * self.hp['take_profit'])     # Take profits at 10%

    def go_short(self):
        pass

    def update_position(self):
        if utils.crossed(self.rsi, self.hp['xparam'], direction="below") or  utils.crossed(self.rsi, 10, direction="below"):
            self.liquidate()

