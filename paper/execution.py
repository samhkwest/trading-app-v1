def simulate_buy(order_book):
    ask = order_book["Ask"][0][0]  # best ask
    return ask

def simulate_sell(order_book):
    bid = order_book["Bid"][0][0]  # best bid
    return bid