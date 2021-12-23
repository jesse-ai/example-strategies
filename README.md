# Example Jesse Strategies

The point of this repository is to host examples of different types of strategies that you can implement with Jesse to get you started. 

## Submission guide

All submitted strategies must be heavily documented. Try to use lots of comments! 
Provide information on symbols and timeframes they work on / were tested.


## Usage Guide
Just copy the folder into your Jesse project's `strategies` directory, and select them in the backtest tab.

Be aware that they are examples to show different approaches to code strategies, use different indicators and functions of Jesse.

The aim of this repository is NOT to provide ready-to-go proftiable strategies, but code examples.

The strategies might only work on certain timeframes / symbols. On others you might face exceptions and need to do adjustments.

Possible errors can be for example: 
- `Uncaught Exception: InvalidStrategy: qty cannot be 0`: This is related to precision and rounding. Different coins have different price precisions leading to necessary adjustments to the qty logic. For example it might be necessary to increase the precision of Jesse's qty utility functions. 
- No trades: You might be using a timeframe or symbol where the signals don't work / happen.
- "It's not profitable": That's not the aim of those strategies and besides that depends on symbol, timeframe and much more factors. 


## Disclaimer

This code is for educational purposes only. We do NOT guarantee profitable trading results in anyways. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS. Do not risk money which you are afraid to lose. There might be bugs in the code - this strategies DO NOT come with ANY warranty. All investments carry risk! Past performance is no guarantee of future results! Be aware of overfitting! 
