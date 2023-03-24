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
            "BANANAS": False,
            "COCONUTS": False,
            "PINA COLADA": False
        }
        self.buy_order_stats: Dict[str, List[int]] = {
            "PEARLS": [0, 0],
            "BANANAS": [0, 0],
            "COCONUTS": [0, 0],
            "PINA COLADA": [0, 0]
        }
        self.sell_order_stats: Dict[str, List[int]] = {
            "PEARLS": [0, 0],
            "BANANAS": [0, 0],
            "COCONUTS": [0, 0],
            "PINA COLADA": [0, 0]
        }
        #for bananas stratey
        self.banana_factor = 3
        self.banana_period = 7
        self.banana_prices=[]
        self.banana_last_trade_signal=""
        self.banana_trade_amount = 10
        self.banana_window_len = 20
 

        # for pearls
        self.pearl_factor = 3
        self.pearl_period = 7
        self.pearl_prices=[]
        self.pearl_last_trade_signal=""
        self.pearl_trade_amount = 10
        self.pearl_window_len=10

        # for coconuts
        self.coconut_factor = 3
        self.coconut_period = 7
        self.coconut_prices=[]
        self.coconut_last_trade_signal=""
        self.coconut_trade_amount = None
        self.coconut_window_len = 10

        # for pina colada
        self.pina_factor = 3
        self.pina_period = 7
        self.pina_prices=[]
        self.pina_last_trade_signal=""
        self.pina_trade_amount = None
        self.pina_window_len = 20
        
    def update_state(self, state: TradingState) -> None:
        self.state = state

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        self.update_state(state)
        self.update_profits()
        self.UpdatePrices()
        print("Pearl Prof:", self.individual_profit("PEARLS"))
        print("Banana Prof:", self.individual_profit("BANANAS"))
        print("Cum Prof:", self.cum_profit)
        print("BANANA buy order stats", self.buy_order_stats["BANANAS"])
        print("BANANA sell order stats", self.sell_order_stats["BANANAS"])
        self.PrintTrades(state)
        # Initialize the method output dict as an empty dict
        result = {}

        # Iterate over all the keys (the available products) contained in the order dephts
        for product in state.order_depths.keys():

            orders = self.execute_trading_logic(product)
            if(orders!=None):
                result[product] = orders
                self.new_order_placed[product]=True

            """
            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'PEARLS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                #append price
                #price=self.GetAveragePrice(order_depth)
                signal="HOLD"
                if(len(self.pearls_prices)>=3):
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
                #self.execute_trading_logic()
                
                orders = self.execute_trading_logic(product)
                if(orders!=None):
                    result[product] = orders
                    self.new_order_placed[product]=True
                
                
        #print basic data
        # self.PrintPosition(state)
        """
        return result
    
    #averagerpice, might not be optimal, can always switch to close price/midprice
    def UpdatePrices(self):
        for product in self.state.order_depths.keys():
            if product == 'PEARLS':
                price=self.GetLastPrice(product)
                self.pearl_prices.append(price)
                if(len(self.pearl_prices)>self.pearl_window_len):
                    self.pearl_prices.pop(0)
            if product=='BANANAS':
                price=self.GetLastPrice(product)
                self.banana_prices.append(price)
                if(len(self.banana_prices)>self.banana_window_len):
                    self.banana_prices.pop(0)
            if product=='COCONUTS':
                price=self.GetLastPrice(product)
                self.coconut_prices.append(price)
                if(len(self.coconut_prices)>self.coconut_window_len):
                    self.coconut_prices.pop(0)
            if product=='PINA COLADA':
                price=self.GetLastPrice(product)
                self.pina_prices.append(price)
                if(len(self.pina_prices)>self.pina_window_len):
                    self.pina_prices.pop(0)

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
        prices=self.pearl_prices
        length = len(prices)
        signal = "HOLD"
        i = 2 #dont want equals, might produce consecutive buy/sell signals
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
                print("   Price Hist:")
                for i in range(10):
                    index = len(self.pearl_prices) - i - 1 
                    if index >= 0 and index < len(self.pearl_prices):
                        print(self.pearl_prices[index])
            print(f"{product}: {pos}")
    
    #return your unrealized_profit
    def UnrealizedProfit(self, state: TradingState) -> float:
        profit = 0

        for product, position in state.position.items():
            symbol = product
            current_price = self.pearl_prices[-1]

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

    def execute_trading_logic(self, symbol: str):        
        if symbol == "BANANAS":
            if len(self.banana_prices) < self.banana_period + 1:
                return 
            df = pd.DataFrame(self.banana_prices, columns=['price'])
            df = self.calculate_supertrend(df, self.banana_period, self.banana_factor)
            df = self.bollinger(df, self.banana_period)

            current_signal = df.iloc[-1]['signal']
            if current_signal != self.last_trade_signal:
                if current_signal == 'long':
                    self.last_trade_signal = current_signal
                    return self.buy(symbol)
                elif current_signal == 'short':
                    self.last_trade_signal = current_signal
                    return self.sell(symbol)
            return
        elif symbol == "PEARLS":
            if len(self.pearl_prices) < self.pearl_period + 1:
                return 
            df = pd.DataFrame(self.pearl_prices, columns=['price'])
            df = self.calculate_supertrend(df, self.pearl_period, self.pearl_factor)
            df = self.bollinger(df, self.pearl_period)

            current_signal = df.iloc[-1]['signal']
            if current_signal != self.last_trade_signal:
                if current_signal == 'long':
                    self.last_trade_signal = current_signal
                    return self.buy(symbol)
                elif current_signal == 'short':
                    self.last_trade_signal = current_signal
                    return self.sell(symbol)
            return
        elif symbol == "COCONUTS":
            if len(self.coconut_prices) < self.coconut_period + 1:
                return 
            df = pd.DataFrame(self.coconut_prices, columns=['price'])
            df = self.calculate_supertrend(df, self.coconut_period, self.coconut_factor)
            df = self.bollinger(df, self.coconut_period)

            current_signal = df.iloc[-1]['signal']
            if current_signal != self.last_trade_signal:
                if current_signal == 'long':
                    self.last_trade_signal = current_signal
                    return self.buy(symbol)
                elif current_signal == 'short':
                    self.last_trade_signal = current_signal
                    return self.sell(symbol)
            return
        elif symbol == "PINA_COLADA":
            if len(self.pina_prices) < self.pina_period + 1:
                return 
            df = pd.DataFrame(self.pina_prices, columns=['price'])
            df = self.calculate_supertrend(df, self.pina_period, self.pina_factor)
            df = self.bollinger(df, self.pina_period)

            current_signal = df.iloc[-1]['signal']
            if current_signal != self.last_trade_signal:
                if current_signal == 'long':
                    self.last_trade_signal = current_signal
                    return self.buy(symbol)
                elif current_signal == 'short':
                    self.last_trade_signal = current_signal
                    return self.sell(symbol)
            return
        else:
            raise Exception("Invalid symbol type for execute_trading_logic function.\nAcceptable symbols: BANANAS, PEARLS, COCONUTS, PINA_COLADA")

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
    
    # calculates upper and lower bollinger band
    def bollinger(self, df: pd.DataFrame, period: int):
        df['sma'] = df['price'].rolling(period).mean()
        df['rstd'] = df['price'].rolling(period).std()
        df['ub'] = df['sma'] + df['rstd'] * 2
        df['lb'] = df['sma'] - df['rstd'] * 2
        return df

    #buy order have to match sell_orders keys and vise versa
    def buy(self, symbol: str):
        orders: list[Order] = []
        if symbol == 'BANANAS':
            remaining_trade_amount = self.banana_trade_amount
            sorted_bids = self.state.order_depths[symbol].sell_orders.keys()
        elif symbol == 'PEARLS':
            remaining_trade_amount = self.pearl_trade_amount
            sorted_bids = self.state.order_depths[symbol].sell_orders.keys()
        elif symbol == 'COCONUTS':
            remaining_trade_amount = self.coconut_trade_amount
            sorted_bids = self.state.order_depths[symbol].sell_orders.keys()
        elif symbol == 'PINA_COLADA':
            remaining_trade_amount = self.pina_trade_amount
            sorted_bids = self.state.order_depths[symbol].sell_orders.keys()
        else:
            raise Exception(f"Invalid Symbol: {symbol}")
        
        for bid in sorted_bids:
            bid_volume = -self.state.order_depths[symbol].sell_orders[bid]#positive
            trade_volume = min(remaining_trade_amount, bid_volume)#positive 
            orders.append(Order(symbol, bid, trade_volume))
            remaining_trade_amount -= trade_volume
            print(f"Buy signal - Buying {trade_volume} bananas at {bid} each")

            if remaining_trade_amount <= 0:
                break

        return orders

    def sell(self, symbol: str):
        orders: list[Order] = []
        if symbol == 'BANANAS':
            remaining_trade_amount = self.banana_trade_amount
            sorted_asks = self.state.order_depths[symbol].buy_orders.keys()
        elif symbol == 'PEARLS':
            remaining_trade_amount = self.pearl_trade_amount
            sorted_asks = self.state.order_depths[symbol].buy_orders.keys()
        elif symbol == 'COCONUTS':
            remaining_trade_amount = self.coconut_trade_amount
            sorted_asks = self.state.order_depths[symbol].buy_orders.keys()
        elif symbol == 'PINA_COLADA':
            remaining_trade_amount = self.pina_trade_amount
            sorted_asks = self.state.order_depths[symbol].buy_orders.keys()
        else:
            raise Exception(f"Invalid symbol: {symbol}")

        for ask in sorted_asks:
            ask_volume = self.state.order_depths[symbol].buy_orders[ask]#positive
            trade_volume = min(remaining_trade_amount, ask_volume)
            orders.append(Order(symbol, ask, -trade_volume))
            remaining_trade_amount -= trade_volume
            print(f"Sell signal - Selling {trade_volume} {symbol} at {ask} each")

            if remaining_trade_amount <= 0:
                break

        return orders