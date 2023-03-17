from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

class Trader:
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all
        Symbols as an input,
        and outputs a list of orders to be sent
        """

        # Initialize the method output dict as an empty dict
        result = {}

        # Iterate over all the keys (the available product) contained in the order depths
        for product in state.order_depths.keys():

            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'PEARLS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empy list
                orders: list[Order] = []

                # Define a fair value for the PEARLS
                # Current value is a dummy value
                acceptable_price = 1

                # If statement checks if there are any SELL orders in the PEARLS market
                if len(order_depth.sell_orders) > 0:

                    # Sort available sell orders by price, select lowest price sell order
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]

                    # Check if lowerst as is lower than the acceptable price
                    if best_ask < acceptable_price:

                        # BUY the sell order
                        print("BUY", str(-best_ask_volume) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_volume))
                    
                    # Add all orders to result dict
                    result[product] = orders
                
        return result