"""
Simple KDJ Indicator Strategy
1D Timeframe
Repo: https://github.com/matty5690/example-strategies
Opens position when J value is above K and D values and closes when J value is below K and D values



"""

from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils


class AwesomeStrategy(Strategy):

    @property
    def KDJIndicator(self): #KDJ Indicator
        return ta.kdj(self.candles) #returns namedtuple KDJ(k,d,j) with default parameters

    @property
    def LastKDJ(self):
        return ta.kdj(self.candles[:-1]) #returns the previous candles KDJ values

    @property
    def atr(self):
        return ta.atr(self.candles, period = 14) #14 period ATR used for calculating stop loss

    def should_long(self) -> bool:
        #long signal if J value crosses above K and D values
        return self.KDJIndicator[2] > (self.KDJIndicator[0] and self.KDJIndicator[1])

    def should_short(self) -> bool:
        return False

    def should_cancel(self) -> bool:
        return True

    def go_long(self):
        # Open long position and risk 5% of  available capital
        risk_perc = 5
        entry = self.price
        stop = entry - 2 * self.atr #trailing stop loss of 2x ATR
        qty = utils.risk_to_qty(self.capital, risk_perc, entry, stop)
        self.buy = qty, self.price
        self.stop_loss = qty, stop

    def go_short(self):
        return False

    def update_position(self):
        #if position is in profit it will close if the J value at close is less than the previous J value
        if self.is_long and self.position.pnl_percentage > 0 and self.LastKDJ[2] > self.KDJIndicator[2]:
            self.liquidate()
        #if position is not in profit and the J value crosses under the K and D values then the position will close
        elif self.is_long and self.KDJIndicator[2] < (self.KDJIndicator[0] and self.KDJIndicator[1]):
            self.liquidate()
