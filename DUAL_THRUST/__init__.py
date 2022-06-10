from jesse.strategies import Strategy, cached
import jesse.indicators as ta
from jesse import utils
import numpy as np

# https://medium.com/@gaea.enquiries/quantitative-strategy-research-series-one-the-dual-thrust-38380b38c2fa
# Dual Thrust by Michael Chalek

class DUAL_THRUST(Strategy):

    def should_long(self) -> bool:
        return self.long_cond

    def should_short(self) -> bool:
        return self.short_cond

    def go_long(self):
        entry = self.price
        stop = entry - self.atr * self.hp['stop_loss_atr_rate']
        qty = utils.risk_to_qty(self.balance, 2, entry, stop)
        self.buy = qty, entry
        self.stop_loss = qty, stop

    def go_short(self):
        entry = self.price
        stop = entry + self.atr * self.hp['stop_loss_atr_rate']
        qty = utils.risk_to_qty(self.balance, 2, entry, stop)
        self.sell = qty, entry
        self.stop_loss = qty, stop

    def update_position(self):
        if (self.is_long and self.short_cond) or (self.is_short and self.long_cond):
            self.liquidate()

    def should_cancel_entry(self) -> bool:
        return True

    ################################################################
    # # # # # # # # # # # # # indicators # # # # # # # # # # # # # #
    ################################################################

    @property
    def up_min_low(self):
        return np.min(self.candles[:, 4][-self.hp['up_length']:])

    @property
    def up_min_close(self):
        return np.min(self.candles[:, 2][-self.hp['up_length']:])

    @property
    def up_max_close(self):
        return np.max(self.candles[:, 2][-self.hp['up_length']:])

    @property
    def up_max_high(self):
        return np.max(self.candles[:, 3][-self.hp['up_length']:])

    @property
    def down_min_low(self):
        return np.min(self.candles[:, 4][-self.hp['down_length']:])

    @property
    def down_min_close(self):
        return np.min(self.candles[:, 2][-self.hp['down_length']:])

    @property
    def down_max_close(self):
        return np.max(self.candles[:, 2][-self.hp['down_length']:])

    @property
    def down_max_high(self):
        return np.max(self.candles[:, 4][-self.hp['down_length']:])

    @property
    def up_thurst(self):
        return self.anchor_candles[:, 1][-1] + self.hp['up_coeff'] * max(self.up_max_close - self.up_min_low, self.up_max_high - self.up_min_close)

    @property
    def down_thrust(self):
        return self.anchor_candles[:, 1][-1] - self.hp['down_coeff'] * max(self.down_max_close - self.down_min_low, self.down_max_high - self.down_min_close)

    @property
    @cached
    def anchor_candles(self):
        return self.get_candles(self.exchange, self.symbol, utils.anchor_timeframe(self.timeframe))

    @property
    def short_cond(self):
        return self.price < self.down_thrust

    @property
    def long_cond(self):
        return self.price > self.up_thurst

    @property
    def atr(self):
        return ta.atr(self.candles)


    # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Genetic
    # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def hyperparameters(self):
        return [
            {'name': 'stop_loss_atr_rate', 'type': float, 'min': 0.1, 'max': 2.0, 'default': 2},
            {'name': 'down_length', 'type': int, 'min': 3, 'max': 30, 'default': 21},
            {'name': 'up_length', 'type': int, 'min': 3, 'max': 30, 'default': 21},
            {'name': 'down_coeff', 'type': float, 'min': 0.1, 'max': 3.0, 'default': 0.67},
            {'name': 'up_coeff', 'type': float, 'min': 0.1, 'max': 3.0, 'default': 0.71},
        ]

