class Product:
    def __init__(self, factor, period, prices, trade_amount, window_len, symbol):
        self.factor = factor
        self.period = period
        self.prices = prices
        self.last_trade_signal = ""
        self.trade_amount = trade_amount
        self.window_len = window_len
        self.symbol = symbol

    def updatePrices(self):
        price = self.getLastPrice()
        self.prices.append(price)
        if len(self.prices) > self.window_len:
            self.prices.pop(0)

    def getLastPrice(self, state):
        if self.symbol in self.state.market_trades and self.state.market_trades[self.symbol]:
            last_trade = state.market_trades[self.symbol][-1]
            return last_trade.price
        else:
            return 0