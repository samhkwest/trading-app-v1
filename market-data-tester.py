# ==========================================================
# MHI Live Market Data Entitlement Tester (V1)
# ==========================================================

from futu import *
import time

# ==========================================================
# Configuration
# ==========================================================
HOST = "127.0.0.1"
PORT = 11111
CODE = "HK.MHI2604"   # main continuous contract
KTYPE = KLType.K_5M


# ==========================================================
# Connection
# ==========================================================
def create_quote_context(host, port):
    print("Connecting to Futu OpenD...")
    ctx = OpenQuoteContext(host=host, port=port)
    print("Connected successfully.\n")
    return ctx


# ==========================================================
# Test 1: Market Snapshot (LV1)
# ==========================================================
def test_market_snapshot(ctx):
    print("Testing LV1 Market Snapshot...")

    ret, data = ctx.get_market_snapshot([CODE])

    if ret == RET_OK:
        print("✅ LV1 Snapshot access: SUCCESS")
        print("\nAvailable Columns:")
        print(data.columns)
        print("\nFull Data:")
        print(data)
    else:
        print("❌ LV1 Snapshot access: FAILED")
        print("Error:", data)

    print("\n")


# ==========================================================
# Test 2: Subscribe Real-Time Quote
# ==========================================================
def test_realtime_subscription(ctx):
    print("Testing Real-Time Quote Subscription...")

    ret, data = ctx.subscribe([CODE], [SubType.QUOTE])

    if ret == RET_OK:
        print("✅ Real-Time QUOTE subscription: SUCCESS")
    else:
        print("❌ Real-Time QUOTE subscription: FAILED")
        print("Error:", data)

    print("\n")


# ==========================================================
# Test 3: Order Book (LV2)
# ==========================================================
def test_order_book(ctx):
    print("Testing LV2 Order Book Access...")

    # First subscribe to order book
    ret_sub, data_sub = ctx.subscribe([CODE], [SubType.ORDER_BOOK])

    if ret_sub != RET_OK:
        print("❌ ORDER_BOOK subscription FAILED")
        print("Error:", data_sub)
        return

    print("✅ ORDER_BOOK subscription SUCCESS")

    # Then request order book
    ret, data = ctx.get_order_book(CODE)

    if ret == RET_OK:
        print("✅ LV2 Order Book access: SUCCESS")

        print("\nTop 3 Bid Levels:")
        for bid in data['Bid'][:3]:
            print(bid)

        print("\nTop 3 Ask Levels:")
        for ask in data['Ask'][:3]:
            print(ask)

    else:
        print("❌ LV2 Order Book access: FAILED")
        print("Error:", data)

    print("\n")


# ==========================================================
# Main Execution
# ==========================================================
if __name__ == "__main__":

    ctx = create_quote_context(HOST, PORT)

    test_market_snapshot(ctx)
    test_realtime_subscription(ctx)
    test_order_book(ctx)

    print("Test complete.")
    ctx.close()