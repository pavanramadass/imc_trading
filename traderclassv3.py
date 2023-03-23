from typing import Dict, List, Optional
from datamodel import OrderDepth, TradingState, Order
import pandas as pd

class Trader:
    #i want state to be a global variable for coveniency, but i think of it too late, so some of my funtion still require state as param
    def __init__(self):
        self.state: Optional[TradingState] = None
        self.cum_profit = 0
        self.individual_profits: Dict[str, int] = {}
        self.new_order_placed: Dict[str, bool] = {
            "PEARLS": False,
            "BANANAS": False
        }
        self.buy_order_stats: Dict[str, List[int]] = {
            "PEARLS": [0, 0],
            "BANANAS": [0, 0]
        }
        self.sell_order_stats: Dict[str, List[int]] = {
            "PEARLS": [0, 0],
            "BANANAS": [0, 0]
        }
        #for bananas stratey
        self.factor = 3
        self.period = 7
        self.bananas_prices=[]
        self.last_trade_signal=""
        self.trade_amount = 10

    def update_state(self, state: TradingState) -> None:
        self.state = state
    #list of pearl's historical price
    pearls_prices=[]

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        self.update_state(state)
        self.update_profits()
        print("Cum Prof:", self.cum_profit)

        # Initialize the method output dict as an empty dict
        result = {}

        # Iterate over all the keys (the available products) contained in the order dephts
        for product in state.order_depths.keys():

            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'PEARLS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                #append price
                #price=self.GetAveragePrice(order_depth)
                price=self.GetLastPrice("PEARLS")
                signal="HOLD"
                if(price!=0):
                    Trader.pearls_prices.append(price)
                    if(len(Trader.pearls_prices)>=3):
                        signal=self.SimpleGrid()

                #simple grid, explain in the method

                if(signal=="BUY"):
                    orders.append(Order(product, 10000, 10))
                    self.new_order_placed["PEARLS"] = True
                elif(signal=="SELL"):
                    orders.append(Order(product, 10000, -10))
                    self.new_order_placed["PEARLS"] = True
                '''
                how the default Order works is that it trys to find you 
                the best deal in the market, and the price is threshold you'd take
                for instance, you Order(product, 10000, 10), and the order book has 
                a sell order priced at 9950 and another at 9970, the system will buy
                the 9950 one. However, if the order book has only one sell order priced at 10001
                nothing will happen becuz its above the 10000 threshold 
                '''

                result[product] = orders
            if product == 'BANANAS':
                price=self.GetLastPrice("BANANAS")
                if(price!=0):
                    self.bananas_prices.append(price)
                '''
                orders = self.execute_trading_logic()
                if(orders!=None):
                    result[product] = orders
                '''
                
        #print basic data
        self.PrintTrades(state)
        # self.PrintPosition(state)
        return result
    
    #averagerpice, might not be optimal, can always switch to close price/midprice
    def GetAveragePrice(self, order_depths:OrderDepth) -> int:
        buy_sum = sum(price * size for price, size in order_depths.buy_orders.items())
        buy_size = sum(size for size in order_depths.buy_orders.values())
        sell_sum = sum(price * size for price, size in order_depths.sell_orders.items())
        sell_size = sum(size for size in order_depths.sell_orders.values())
        if(buy_size==0 or sell_size==0):
            return 0
        buy_weighted_avg = buy_sum / buy_size
        sell_weighted_avg = sell_sum / sell_size
        return (buy_weighted_avg + sell_weighted_avg) / 2
    
    def GetLastPrice(self, symbol:str) -> int:
        if symbol in self.state.market_trades and self.state.market_trades[symbol]:
            last_trade = self.state.market_trades[symbol][-1]
            return last_trade.price
        else:
            return 0
    
    # simple grid for testing, when U shape buy, when n shape sell, other situation hold 
    def SimpleGrid(self) -> str:
        prices=Trader.pearls_prices
        length = len(prices)
        signal = "HOLD"
        i = 2#dont want equals, might produce consecutive buy/sell signals
        while prices[length - i] == prices[length - 3] and i < length:
            i += 1
        if prices[length - 1] > prices[length - i] and prices[length - i] < prices[length - (i + 1)]:
            signal = "BUY"
        elif prices[length - 1] < prices[length - i] and prices[length - i] > prices[length - (i + 1)]:
            signal = "SELL"

        return signal

    #show your last trade 
    def PrintTrades(self, state: TradingState): 
        for symbol, trades in state.own_trades.items():
            print(f"Symbol: {symbol}")
            for trade in trades:
                print(f"  {trade.quantity} shares at ${trade.price} (buyer: {trade.buyer}, seller: {trade.seller})") 

    #shor your pos
    def PrintPosition(self, state: TradingState):
        position_dict = state.position
        print("Position:")
        for product, pos in position_dict.items():
            if(self.UnrealizedProfit(state)<0):
                print("   Pirce Hist:")
                for i in range(10):
                    index = len(Trader.pearls_prices) - i - 1 
                    if index >= 0 and index < len(Trader.pearls_prices):
                        print(Trader.pearls_prices[index])
            print(f"{product}: {pos}")
    
    #return your unrealized_profit
    def UnrealizedProfit(self, state: TradingState) -> float:
        profit = 0

        for product, position in state.position.items():
            symbol = product
            current_price = Trader.pearls_prices[-1]

            # Calculate profit for long positions
            if position > 0:
                average_price = self.CalculateAveragePrice(symbol)
                profit += (current_price - average_price) * position

            # Calculate profit for short positions
            elif position < 0:
                average_price = self.CalculateAveragePrice(symbol)
                profit += (average_price - current_price) * abs(position)

        return profit
    #calculate avg price of your last trade
    def CalculateAveragePrice(self, symbol: str) -> float:
        own_trades = self.state.own_trades[symbol]
        total_cost = 0
        total_quantity = 0

        for trade in own_trades:
            total_cost += trade.price * abs(trade.quantity)
            total_quantity += abs(trade.quantity)

        if total_quantity == 0:
            return 0

        return total_cost / total_quantity
    
    #update profit 
    def update_order_stats(self, symbol: str):
        last_own_trades = self.state.own_trades[symbol]

        for trade in last_own_trades:
            if trade.buyer == "SUBMISSION":
                self.update_order_stats_dict(self.buy_order_stats, symbol, trade.price, trade.quantity)
            elif trade.seller == "SUBMISSION":
                self.update_order_stats_dict(self.sell_order_stats, symbol, trade.price, trade.quantity)

    def update_order_stats_dict(self, order_stats: Dict[str, List[int]], symbol: str, price: int, quantity: int):
        if symbol not in order_stats:
            order_stats[symbol] = [price, quantity]
        else:
            total_quantity = order_stats[symbol][1] + quantity
            avg_price = (order_stats[symbol][0] * order_stats[symbol][1] + price * quantity) / total_quantity
            order_stats[symbol] = [avg_price, total_quantity]

    def update_cum_profit(self, symbol: str):
        buy_stats = self.buy_order_stats.get(symbol, [0, 0])
        sell_stats = self.sell_order_stats.get(symbol, [0, 0])

        min_qty = min(buy_stats[1], sell_stats[1])
        netted_profit = (sell_stats[0] - buy_stats[0]) * min_qty

        self.individual_profits[symbol] = netted_profit
        self.cum_profit += netted_profit

    def update_profits(self):
        set_zero=False
        for symbol in self.state.own_trades.keys():
            if self.new_order_placed.get(symbol, False):
                if(set_zero==False):
                    self.cum_profit =0
                    set_zero=True
                self.update_order_stats(symbol)
                self.update_cum_profit(symbol)
                self.new_order_placed[symbol] = False

    def cumulative_profit(self) -> int:
        return self.cum_profit

    def individual_profit(self, symbol: str) -> int:
        return self.individual_profits.get(symbol, 0)

    #BANANNANANANANANAN
    def execute_trading_logic(self):
        if len(self.bananas_prices) < self.period + 1:
            # Not enough data to calculate SuperTrend
            return

        df = pd.DataFrame(self.bananas_prices, columns=['price'])
        supertrend_df = self.calculate_supertrend(df, self.period, self.factor)

        current_signal = supertrend_df.iloc[-1]['signal']
        if current_signal != self.last_trade_signal:
            if current_signal == 'long':
                self.buy_bananas()
            elif current_signal == 'short':
                self.sell_bananas()
            self.last_trade_signal = current_signal
        return 

    def calculate_supertrend(self, df: pd.DataFrame, period: int, factor: float) -> pd.DataFrame:
        # Calculate HL2, ATR, Up, and Dn
        df['hl2'] = (df['price'].shift(1).rolling(window=period).max() + df['price'].shift(1).rolling(window=period).min()) / 2
        df['atr'] = df['price'].diff().abs().rolling(window=period).mean()
        df['up'] = df['hl2'] - factor * df['atr']
        df['dn'] = df['hl2'] + factor * df['atr']

        # Calculate the SuperTrend and trading signals
        df['st'] = 0.0
        df['signal'] = None
        for i in range(period, len(df)):
            if df.loc[i, 'price'] > df.loc[i - 1, 'st']:
                df.loc[i, 'st'] = max(df.loc[i, 'up'], df.loc[i - 1, 'st'])
                df.loc[i, 'signal'] = 'long'
            else:
                df.loc[i, 'st'] = min(df.loc[i, 'dn'], df.loc[i - 1, 'st'])
                df.loc[i, 'signal'] = 'short'

        return df
    '''
    def buy_bananas(self):
        # Implement your buy logic here
        print("Buy signal")

    def sell_bananas(self):
        # Implement your sell logic here
        print("Sell signal")
    '''
    def buy_bananas(self):
        orders: list[Order] = []
        remaining_trade_amount = self.trade_amount
        symbol = "BANANAS"
        sorted_bids = sorted(self.state.order_depths[symbol].buy_orders.keys(), reverse=True)
        
        for bid in sorted_bids:
            bid_volume = self.state.order_depths[symbol].buy_orders[bid]
            trade_volume = min(remaining_trade_amount, bid_volume)
            orders.append(Order(symbol, bid, trade_volume))
            remaining_trade_amount -= trade_volume
            print(f"Buy signal - Buying {trade_volume} bananas at {bid} each")

            if remaining_trade_amount <= 0:
                break

        return orders

    def sell_bananas(self):
        orders: list[Order] = []
        remaining_trade_amount = self.trade_amount
        symbol = "BANANAS"
        sorted_asks = sorted(self.state.order_depths[symbol].sell_orders.keys())

        for ask in sorted_asks:
            ask_volume = self.state.order_depths[symbol].sell_orders[ask]
            trade_volume = min(remaining_trade_amount, ask_volume)
            orders.append(Order(symbol, ask, -trade_volume))
            remaining_trade_amount -= trade_volume
            print(f"Sell signal - Selling {trade_volume} bananas at {ask} each")

            if remaining_trade_amount <= 0:
                break

        return orders



        