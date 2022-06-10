"""
The Original Turtle Trading Rules Strategy
2020-06-20 original implementation - FengkieJ (fengkiejunis@gmail.com)
2020-06-27 rev 1. add System 1 & System 2 as strategy parameters - FengkieJ (fengkiejunis@gmail.com)

Turtle strategy is one of classic trend-following system that has clear defined trading rules. The system was taught by Richard Dennis 
and William Eckhardt in 1983. This version implements the system described by Curtis Faith, author of bestselling book Way of the Turtle.

In Turtle system theory, a complete trading system must cover several aspects, i.e.:
   - Markets - What to buy or sell
   - Position Sizing - How much to buy or sell
   - Entries - When to buy or sell
   - Stops - When to get out of a losing position
   - Exits - When to get out of a winning position
   - Tactics - How to buy or sell

This Python module attempts to implement the system on Jesse framework as described in the pdf by Curtis Faith & Perry J. Kaufman.

Reference: - Faith, C. (2003). The Original Turtle Rules. Retrieved 14 June 2020, from http://www.tradingblox.com/originalturtles/originalturtlerules.htm
           - Kaufman, P. (2013). Trading systems and methods (5th ed., pp. 229-233). Hoboken, N.J.: Wiley.
"""

from jesse.strategies import Strategy
from jesse.indicators import donchian, atr
from jesse import utils

class TurtleRules(Strategy):
    def __init__(self):
        super().__init__()

        self.current_pyramiding_levels = 0
        self.last_opened_price = 0
        self.last_was_profitable = False

    def before(self):
        self.vars["unit_risk_percent"] = 1
        self.vars["entry_dc_period"] = 20
        self.vars["exit_dc_period"] = 10
        self.vars["atr_period"] = 20
        self.vars["atr_multiplier"] = 2
        self.vars["maximum_pyramiding_levels"] = 4
        self.vars["pyramiding_threshold"] = 0.5
        self.vars["system_type"] = "S1"

    @property
    def entry_donchian(self):
        return donchian(self.candles, self.vars["entry_dc_period"])

    @property
    def exit_donchian(self):
        return donchian(self.candles, self.vars["exit_dc_period"])

    @property
    def atr(self):
        return atr(self.candles, self.vars["atr_period"])

    def unit_qty(self, unit_risk_percent, dollars_per_point = 1):
        # In Original Turtle Rule book, the position sizing formula is defined as: 
        # Unit = 1% of Account / (N × Dollars per Point) where N is ATR(20)
        
        return ((unit_risk_percent/100) * self.balance) / (self.atr * dollars_per_point)

    def entry_signal(self):
        # "The Turtles used two related system entries, each based on Donchian’s channel breakout system.
        #     ...
        #     System 1 – A shorter-term system based on a 20-day breakout (with a filter if previous trade was profitable do not enter the next)
        #     System 2 – A simpler long-term system based on a 55-day breakout." (Faith, 2003)
        signal = None
        upperband = self.entry_donchian[0]
        lowerband = self.entry_donchian[2]

        if self.high >= upperband:
            signal = "entry_long"
        elif self.low <= lowerband:
            signal = "entry_short"
        
        return signal

    def exit_signal(self):
        # "The System 1 exit was a 10 day low for long positions and a 10 day high for short positions. 
        #   All the Units in the position would be exited if the price went against the position for a 10 day breakout.
        #   The System 2 exit was a 20 day low for long positions and a 20 day high for short positions. 
        #   All the Units in the position would be exited if the price went against the position for a 20 day breakout." (Faith, 2003)
        signal = None
        upperband = self.exit_donchian[0]
        lowerband = self.exit_donchian[2]

        if self.high >= upperband:
            signal = "exit_short"
        elif self.low <= lowerband:
            signal = "exit_long"
        
        return signal

    def should_long(self) -> bool:
        return self.entry_signal() == "entry_long"

    def should_short(self) -> bool:
        return self.entry_signal() == "entry_short"

    def should_cancel_entry(self) -> bool:
        pass

    def go_long(self):
        qty = self.unit_qty(self.vars["unit_risk_percent"])
        sl = self.price - self.vars["atr_multiplier"] * self.atr

        self.buy = qty, self.price
        self.stop_loss = qty, sl
        # self.log(f"enter long {qty}")
        self.current_pyramiding_levels += 1 # Track the pyramiding level
        self.last_opened_price = self.price # Store this value to determine when to add next pyramiding

    def go_short(self):
        qty = self.unit_qty(self.vars["unit_risk_percent"])
        sl = self.price + self.vars["atr_multiplier"] * self.atr

        self.sell = qty, self.price
        self.stop_loss = qty, sl
        # self.log(f"enter short {qty}")
        self.current_pyramiding_levels += 1 # Track the pyramiding level
        self.last_opened_price = self.price # Store this value to determine when to add next pyramiding

    def update_position(self):
        # Handle for pyramiding rules
        if self.current_pyramiding_levels < self.vars["maximum_pyramiding_levels"]:
            if self.is_long and self.price > self.last_opened_price + (self.vars["pyramiding_threshold"] * self.atr):
                qty = self.unit_qty(self.vars["unit_risk_percent"])
                self.buy = qty, self.price
                # self.log(f"atr={self.atr}, last price={self.last_opened_price}, cur price={self.price}, action: increase long position {qty}")
            
            if self.is_short and self.price < self.last_opened_price - (self.vars["pyramiding_threshold"] * self.atr):
                qty = self.unit_qty(self.vars["unit_risk_percent"])
                self.sell = qty, self.price
                # self.log(f"atr={self.atr}, last price={self.last_opened_price}, cur price={self.price}, action: increase short position {qty}")

        # "Trades are exited on the fi rst occurrence of
        #     a. The stop-loss
        #     b. An S1 or S2 reversal
        #     c. A loss of 2% relative to the portfolio (where 2L is equal to 2% of the portfolio)" (Kaufman, 2013)
        if self.is_long and (self.entry_signal() == "entry_short" or self.exit_signal() == "exit_long") \
                or self.is_short and (self.entry_signal() == "entry_long" or self.exit_signal() == "exit_short"):
            self.liquidate()
            self.current_pyramiding_levels = 0

    def on_increased_position(self, order):
        # "In order to keep total position risk at a minimum, if additional units were added, the stops for earlier units were raised by 1⁄2 N. 
        #   This generally meant that all the stops for the entire position would be placed at 2 N from the most recently added unit." (Faith, 2003)
        if self.is_long:
            self.stop_loss = abs(self.position.qty), self.price - self.vars["atr_multiplier"] * self.atr
            # self.log(f"atr={self.atr}, current position sl: {self.average_stop_loss}")
        if self.is_short:
            self.stop_loss = abs(self.position.qty), self.price + self.vars["atr_multiplier"] * self.atr
            # self.log(f"atr={self.atr}, current position sl: {self.average_stop_loss}")
        
        self.current_pyramiding_levels += 1
        self.last_opened_price = self.price
        # self.log(f"current pyramiding levels: {self.current_pyramiding_levels}")

    def on_stop_loss(self, order):
        # Reset tracked pyramiding levels
        self.current_pyramiding_levels = 0 

    def on_take_profit(self, order):
        self.last_was_profitable = True

        # Reset tracked pyramiding levels
        self.current_pyramiding_levels = 0 
    
    def filters(self):
        return [
            self.S1_filter
        ]

    def S1_filter(self):
        if self.vars["system_type"] == "S1" and self.last_was_profitable:
            # self.log(f"prev was profitable, do not enter trade")
            self.last_was_profitable = False
            return False
        return True
