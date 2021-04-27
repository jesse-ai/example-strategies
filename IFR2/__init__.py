"""
IFR2 (portuguese translation of RSI2)
Repo: https://github.com/gabrielweich/jesse-strategies
Simillar to RSI2 described by Larry Connors but with some modifications.
Uses Ichimoku Cloud with parameters adapted to crypto market and also
Hilbert Transform Trendmode as filters to only buy in an uptrend.
The exit occurs when the close is above the highest high of the two
previous cadles.
References:
 - RSI2: https://school.stockcharts.com/doku.php?id=trading_strategies:rsi2
 - Ichimoku Crypto Parameters: https://www.altcointrading.net/ichimoku-cloud/
"""

from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils


class IFR2(Strategy):
    @property
    def rsi(self):
        return ta.rsi(self.candles, period=2)

    @property
    def trend_mode(self):
        return ta.ht_trendmode(self.candles)

    @property
    def ichimoku(self):
        # Ichimoku cloud using parameters adapted to crypto market
        return ta.ichimoku_cloud(
            self.candles,
            conversion_line_period=20,
            base_line_period=30,
            lagging_line_period=120,
            displacement=60,
        )

    def filter_trend_ichimoku(self):
        # Only opens a long position when close is above ichimoku cloud
        return self.close > self.ichimoku.span_a and self.close > self.ichimoku.span_b

    def filter_trend_mode(self):
        # Only opens a long position when trend_mode indicates a trend
        return self.trend_mode == 1

    def filters(self):
        return [self.filter_trend_ichimoku, self.filter_trend_mode]

    def should_long(self) -> bool:
        # Go long if candle RSI2 is below 10
        return self.rsi < 10

    def should_short(self) -> bool:
        return False

    def should_cancel(self) -> bool:
        return True

    def go_long(self):
        # Open long position using entire balance
        qty = utils.size_to_qty(self.capital, self.price, fee_rate=self.fee_rate)
        self.buy = qty, self.price

    def go_short(self):
        pass

    def update_position(self):
        # Close the position when candle is above the highest high of the two previous cadles
        if (
            self.close > self.candles[-2:, 3][-2]
            and self.close > self.candles[-3:, 3][-3]
        ):
            self.liquidate()